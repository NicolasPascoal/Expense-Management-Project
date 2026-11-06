# Mesma versão do Postgres do banco (pg_dump 15 para servidor 15) + rclone
# para enviar a cópia para fora do servidor.
FROM postgres:15-alpine

RUN apk add --no-cache rclone

COPY backup.sh agendar.sh /usr/local/bin/
# Remove CR caso o checkout tenha vindo do Windows com fim de linha CRLF.
RUN sed -i 's/\r$//' /usr/local/bin/backup.sh /usr/local/bin/agendar.sh \
    && chmod +x /usr/local/bin/backup.sh /usr/local/bin/agendar.sh

ENTRYPOINT ["agendar.sh"]
CMD []
