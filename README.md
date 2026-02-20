# Pond Mobile API Proxy

Прокси-сервер для Pond Mobile API сVault-интеграцией и защитой по IP/токенам.

## Архитектура

```
Client → Caddy → FastAPI → Pond Mobile API
                     ↓
                  Vault (KV v2)
```

## Требования

- Docker & Docker Compose
- Python 3.11+
- HashiCorp Vault

## Быстрый старт

```bash
# Копирование переменных окружения
cp .env.example .env

# Запуск через Docker Compose
cd docker
docker-compose up -d

# Инициализация Vault
./deploy/init_vault.sh

# Проверка здоровья
curl http://localhost/health
```

## API Endpoints

### Proxy

```bash
POST /proxy/v2.1/network-access/cancel-lu-requests?iccid={iccid}
Headers:
  Authorization: Bearer {token}
  request-id: {uuid}
  version: 2.1
```

### Health

```bash
GET /health
GET /health/ready
```

## Безопасность

- Валидация Bearer токенов
- IP whitelist
- Vault для хранения секретов
- TLS через Caddy

## Разработка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Лицензия

MIT
