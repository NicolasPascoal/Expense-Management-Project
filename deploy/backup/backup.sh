#!/bin/sh
# Um backup do banco: dump no formato custom do pg_dump (restaura com
# pg_restore), retenção local e — se RCLONE_DESTINO estiver definido — cópia
# para fora do servidor (Google Drive via rclone). Conexão pelas variáveis
# PGHOST/PGUSER/PGPASSWORD/PGDATABASE. Restauração: docs/Deploy.md.
set -eu

DIR=${BACKUP_DIR:-/backups}
ARQ="$DIR/gabaro_$(date -u +%Y-%m-%d_%H%M%S).dump"

mkdir -p "$DIR"
rm -f "$DIR"/*.parcial  # sobra de uma execução que falhou no meio
pg_dump --format=custom --file="$ARQ.parcial"
mv "$ARQ.parcial" "$ARQ"  # só vira .dump depois de completo
echo "backup local: $ARQ ($(du -h "$ARQ" | cut -f1))"

find "$DIR" -name 'gabaro_*.dump' -mtime +"${BACKUP_RETENCAO_DIAS:-14}" -delete

if [ -n "${RCLONE_DESTINO:-}" ]; then
  rclone copy "$ARQ" "$RCLONE_DESTINO"
  rclone delete "$RCLONE_DESTINO" --include 'gabaro_*.dump' --min-age "${BACKUP_RETENCAO_REMOTA_DIAS:-60}d"
  echo "cópia enviada para $RCLONE_DESTINO"
fi

# Aviso de "backup não rodou": serviço de ping (ex.: healthchecks.io) que
# manda e-mail se ficar mais de um dia sem receber este sinal.
if [ -n "${BACKUP_PING_URL:-}" ]; then
  wget -q -O /dev/null "$BACKUP_PING_URL" || echo "aviso: não consegui avisar $BACKUP_PING_URL" >&2
fi
