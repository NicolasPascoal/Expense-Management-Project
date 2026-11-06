# Deploy em produção (VPS)

Passo a passo para colocar o Gabaro no ar num servidor na nuvem, com HTTPS, backup diário com cópia no Google Drive e os dados que já existem (ex.: a instalação no Mac do cliente).

Como fica no servidor (`docker-compose.yml`):

```
internet ──443/80──> caddy (HTTPS automático) ──> frontend (nginx: React + /api) ──> backend (Flask) ──> db_postgres
                                                                                       backup ──────────┘ (dump diário → ./backups + Google Drive)
```

Só as portas 80 e 443 ficam abertas. Banco e backend só existem na rede interna do Docker.

---

## 0. O que você precisa

- **VPS** com Ubuntu 24.04, datacenter em São Paulo, 1–2 vCPU, 2 GB de RAM e ~40 GB de disco.
- **Domínio** registrado (ex.: no registro.br).
- **Conta Google** para guardar a cópia dos backups no Drive.
- No seu PC: terminal com `ssh` (o Windows já tem) e o [rclone](https://rclone.org/downloads/) (`winget install Rclone.Rclone`), usado só uma vez para autorizar o Drive.

Nos comandos abaixo, troque `IP_DO_SERVIDOR`, `gabaro.exemplo.com.br` e `deploy` (usuário do servidor) pelos seus.

## 1. DNS

No painel do domínio (no registro.br: "DNS" → "Editar zona" / modo avançado), crie um registro **A**:

| Nome | Tipo | Valor |
|---|---|---|
| `gabaro` (ou vazio, para o domínio raiz) | A | `IP_DO_SERVIDOR` |

A propagação pode levar de minutos a algumas horas. Confira com `nslookup gabaro.exemplo.com.br`, que deve responder o IP do servidor. O HTTPS só funciona depois disso.

## 2. Preparar o servidor (uma vez)

```bash
ssh root@IP_DO_SERVIDOR

# usuário próprio (não usar root no dia a dia)
adduser deploy
usermod -aG sudo deploy
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy   # copia sua chave SSH, se entrou com chave

# firewall: só SSH, HTTP e HTTPS
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw enable

# atualizações de segurança automáticas
apt update && apt -y upgrade
apt -y install unattended-upgrades git
dpkg-reconfigure -plow unattended-upgrades

# Docker (script oficial)
curl -fsSL https://get.docker.com | sh
usermod -aG docker deploy
exit
```

Entre de novo já como `deploy` (`ssh deploy@IP_DO_SERVIDOR`) para o grupo `docker` valer.

## 3. Instalar o Gabaro

```bash
git clone https://github.com/NicolasPascoal/Expense-Management-Project.git gabaro
cd gabaro
cp .env.example .env
openssl rand -hex 24   # use como PGPASSWORD
openssl rand -hex 32   # use como JWT_SECRET_KEY
nano .env              # preencha DOMINIO, PGPASSWORD, JWT_SECRET_KEY
```

- **Vai migrar dados existentes** (seção 5)? Deixe `ADMIN_USERNAME`/`ADMIN_PASSWORD` vazios: os usuários vêm junto com os dados.
- **Instalação nova sem dados?** Preencha os dois: é o primeiro login de admin.

**Não suba tudo ainda** se for migrar dados: a ordem está na seção 5.

## 4. Cópia do backup no Google Drive (uma vez)

O serviço `backup` faz um dump do banco ao subir e depois todo dia às 03:00 (Brasília). Guarda 14 dias em `./backups` e, configurado o rclone, manda uma cópia para o Drive (60 dias por lá).

1. No servidor, abra o assistente do rclone dentro do container de backup:
   ```bash
   docker compose run --rm --entrypoint rclone backup config
   ```
2. Responda:
   - `n` (novo remote)
   - nome: `gdrive`
   - storage: `drive`
   - client_id e client_secret: em branco
   - scope: `drive.file` (o rclone só enxerga os arquivos que ele mesmo criar)
   - service_account_file: em branco
   - "Edit advanced config": `n`
   - "Use web browser to automatically authenticate": **`n`** (o servidor não tem navegador)
3. O rclone mostra um comando `rclone authorize "drive" "..."`. Rode esse comando **no seu PC** (com o rclone instalado): o navegador abre, você autoriza com a conta Google e o terminal do PC devolve um token. Cole o token no servidor.
4. "Shared Drive": `n`. Confirme com `y` e saia com `q`. A configuração fica em `./rclone/rclone.conf` (fora do Git, contém o token).
5. No `.env`, defina `RCLONE_DESTINO=gdrive:gabaro-backups`.

**Opcional (recomendado):** crie um check gratuito em [healthchecks.io](https://healthchecks.io) com período de 1 dia e coloque a URL de ping em `BACKUP_PING_URL`. Se o backup parar de rodar, você recebe um e-mail.

## 5. Migrar os dados do Mac

Combine um horário com o cliente: **ninguém pode lançar nada no Mac** a partir do passo 1. O que for lançado depois do dump fica para trás.

1. **No Mac**, gere o dump:
   - Se o sistema roda com Docker:
     ```bash
     docker exec meu_projeto_db pg_dump -U postgres -Fc expense_management > gabaro_mac.dump
     ```
     Se o container tiver outro nome, veja com `docker ps`.
   - Se roda com Postgres instalado direto no Mac:
     ```bash
     pg_dump --version                  # precisa ser 15.x; se for maior, pare e peça ajuda
     pg_dump -U postgres -Fc expense_management -f gabaro_mac.dump
     ```
2. Copie o dump para o servidor (do Mac):
   ```bash
   scp gabaro_mac.dump deploy@IP_DO_SERVIDOR:~/
   ```
3. **No servidor**, suba só o banco, restaure e confira:
   ```bash
   cd ~/gabaro
   docker compose up -d db_postgres
   docker compose exec -T db_postgres pg_restore --clean --if-exists --no-owner -U postgres -d expense_management < ~/gabaro_mac.dump
   docker compose exec db_postgres psql -U postgres -d expense_management -c \
     "select (select count(*) from projetos) obras, (select count(*) from usuarios) usuarios, (select count(*) from lancamentos_v2) lancamentos"
   ```
   Rode a mesma consulta no Mac e compare os números. Avisos de `pg_restore` sobre objetos que "não existem" são normais com `--clean`.
4. Suba o resto (seção 6). Ao iniciar, o backend aplica sozinho as migrations que faltarem nesse banco.

## 6. Subir tudo

```bash
docker compose up -d --build
docker compose ps                 # todos "running"/"healthy"
docker compose logs caddy         # deve mostrar o certificado obtido para o DOMINIO
docker compose logs backup        # deve mostrar "backup local: ..." e, com o rclone, "cópia enviada"
```

Abra `https://gabaro.exemplo.com.br`.

## 7. Checklist do lançamento

- [ ] Login com cada papel (admin, gestor de obra, financeiro, prestador): cada um vê só o que deve.
- [ ] Obras, lançamentos, orçamento e fluxo de caixa batem com o Mac.
- [ ] Lançar uma nota com 2 itens e excluir depois.
- [ ] Acessar pelo celular **no 4G** (fora do Wi-Fi do escritório).
- [ ] Arquivo do backup aparece na pasta `gabaro-backups` do Google Drive.
- [ ] **Teste de restauração** (seção 9.1) feito ao menos uma vez.
- [ ] Monitor de "site fora do ar" criado (ex.: [UptimeRobot](https://uptimerobot.com), gratuito, verificando `https://gabaro.exemplo.com.br` a cada 5 min, alerta por e-mail).
- [ ] Mac guardado por alguns dias como plano B e depois desligado (não usar os dois ao mesmo tempo).

## 8. Atualizar o sistema

```bash
cd ~/gabaro
docker compose exec backup backup.sh   # backup extra antes de atualizar
git pull
docker compose up -d --build
```

As migrations rodam sozinhas ao subir o backend. Se ele não subir, veja `docker compose logs backend`.

## 9. Backups

- **Onde estão:** `~/gabaro/backups/gabaro_AAAA-MM-DD_HHMMSS.dump` (14 dias) e a pasta `gabaro-backups` no Google Drive (60 dias).
- **Fazer um agora:** `docker compose exec backup backup.sh`

### 9.1 Teste de restauração (sem tocar no banco de verdade)

Faça no lançamento e depois a cada 3 meses.

```bash
cd ~/gabaro
ARQ=$(ls -t backups/*.dump | head -1)
docker compose exec db_postgres createdb -U postgres teste_restauracao
docker compose exec -T db_postgres pg_restore --no-owner -U postgres -d teste_restauracao < "$ARQ"
docker compose exec db_postgres psql -U postgres -d teste_restauracao -c "select count(*) from lancamentos_v2"
docker compose exec db_postgres dropdb -U postgres teste_restauracao
```

### 9.2 Restaurar de verdade (perda de dados)

Isto substitui todo o banco pelo backup: o que foi lançado depois dele se perde.

```bash
cd ~/gabaro
docker compose stop backend
docker compose exec -T db_postgres pg_restore --clean --if-exists --no-owner -U postgres -d expense_management < backups/ARQUIVO_ESCOLHIDO.dump
docker compose start backend
```

Para restaurar a partir do Drive (ex.: o servidor foi perdido), baixe o `.dump` da pasta `gabaro-backups` e siga a seção 5 a partir do passo 2.

## 10. Problemas comuns

| Sintoma | Causa provável |
|---|---|
| Navegador avisa "conexão não segura" / Caddy não obtém certificado | DNS ainda não aponta para o servidor, ou portas 80/443 bloqueadas (`ufw status`, firewall do provedor) |
| `502 Bad Gateway` | Backend ou frontend fora do ar: `docker compose ps` e `docker compose logs backend` |
| `defina ... no .env` ao rodar `docker compose` | Variável obrigatória vazia no `.env` (DOMINIO, PGPASSWORD, JWT_SECRET_KEY) |
| Todos foram deslogados | `JWT_SECRET_KEY` mudou. Normal se foi de propósito |
| Backup sem "cópia enviada" | `RCLONE_DESTINO` vazio ou token do Drive expirado: refaça a seção 4 |
