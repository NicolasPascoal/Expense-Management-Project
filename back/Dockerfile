FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Aplica migrations antes de subir (migrar_banco.py: init_db + stamp da
# baseline em banco sem alembic_version + alembic upgrade head). Se falhar,
# o container não sobe — melhor que servir com schema desatualizado.
# Inline em vez de um .sh para não depender de fim de linha LF no checkout.
CMD ["sh", "-c", "python migrar_banco.py && exec gunicorn -w 4 -b 0.0.0.0:5000 main:app"]