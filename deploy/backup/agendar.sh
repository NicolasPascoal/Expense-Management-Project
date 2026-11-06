#!/bin/sh
# Roda um backup assim que o container sobe (confirma na hora que a
# configuração funciona) e depois todo dia às BACKUP_HORA_UTC (padrão 6 =
# 03:00 em Brasília). Loop simples em vez de crond: o crond do BusyBox não
# repassa as variáveis de ambiente do container (PGPASSWORD...) para o job.
HORA=${BACKUP_HORA_UTC:-6}

backup.sh || echo "BACKUP FALHOU" >&2

while true; do
  agora=$(( $(date -u +%s) % 86400 ))
  espera=$(( (HORA * 3600 - agora + 86400) % 86400 ))
  [ "$espera" -eq 0 ] && espera=86400
  sleep "$espera"
  backup.sh || echo "BACKUP FALHOU" >&2
done
