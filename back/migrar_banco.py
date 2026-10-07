"""
Prepara o banco antes de o backend subir — chamado pelo CMD do Dockerfile,
antes do gunicorn, e pelo CI (mesmo caminho do deploy). Idempotente.

1. init_db(): cria o schema e os seeds, como em todo boot. É ele quem cria
   o banco do zero — a migration baseline não serve para isso (não tem os
   server defaults do SQL do init_db, ex.: requisicoes.status 'Pendente').
2. Banco sem `alembic_version` (criado só pelo init_db, ex.: staging):
   `stamp` na baseline — o schema dela já existe, só falta o registro.
3. `upgrade head`: aplica as revisions posteriores à baseline.

Uso: python migrar_banco.py   (usa as mesmas variáveis PG* do .env)
"""
import logging
import os
import sys
from urllib.parse import quote_plus

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

load_dotenv()

# Importados depois do load_dotenv: db.py lê as variáveis PG* no import.
from app.database.db import PG_DATABASE, init_db  # noqa: E402
from app.logging_config import configure_logging  # noqa: E402

REVISION_BASELINE = "61a73b52f4cf"

logger = logging.getLogger("gabaro.migracoes")


def _database_url():
    """Mesma URL que migrations/env.py monta — e o mesmo banco do init_db()."""
    usuario = quote_plus(os.getenv("PGUSER", "postgres"))
    senha = quote_plus(os.getenv("PGPASSWORD", "postgres"))
    host = os.getenv("PGHOST", "localhost")
    porta = os.getenv("PGPORT", "5432")
    return f"postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{PG_DATABASE}"


def main():
    configure_logging()

    # migrations/env.py prefere TEST_PGDATABASE a PGDATABASE; o init_db() só
    # usa PGDATABASE. Se divergirem, o schema seria criado num banco e as
    # migrations aplicadas em outro.
    banco_teste = os.getenv("TEST_PGDATABASE")
    if banco_teste and banco_teste != PG_DATABASE:
        logger.error("TEST_PGDATABASE (%s) difere de PGDATABASE (%s); abortando", banco_teste, PG_DATABASE)
        sys.exit(1)

    logger.info("init_db: garantindo schema e seeds")
    init_db()

    engine = create_engine(_database_url())
    try:
        tem_version = inspect(engine).has_table("alembic_version")
    finally:
        engine.dispose()

    config = Config(os.path.join(os.path.dirname(os.path.abspath(__file__)), "alembic.ini"))
    if not tem_version:
        logger.info("banco sem alembic_version: stamp na baseline %s", REVISION_BASELINE)
        command.stamp(config, REVISION_BASELINE)

    logger.info("alembic upgrade head")
    command.upgrade(config, "head")
    logger.info("migrações concluídas")


if __name__ == "__main__":
    main()
