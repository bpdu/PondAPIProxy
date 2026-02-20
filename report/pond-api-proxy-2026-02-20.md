# Pond Mobile API Proxy — Отчёт о реализации

**Дата:** 2026-02-20
**Статус:** Done

## Описание задачи

Создание прокси-сервиса для Pond Mobile API с собственной системой авторизации, хранением чувствительных данных в HashiCorp Vault и защитой по IP whitelist. Основная цель — предоставить единый endpoint для отмены LU-запросов с контролем доступа и автоматическим HTTPS через Caddy.

## Итоги Research

На стадии исследования были приняты следующие архитектурные решения:

| Компонент | Выбор | Обоснование |
|-----------|-------|-------------|
| Backend | Python + FastAPI | Асинхронность, type hints, автоматическая документация |
| Vault | HashiCorp Vault (self-hosted) | Industry standard для управления секретами, KV v2 |
| SSL/TLS | Caddy + Let's Encrypt | Автоматическое получение и обновление сертификатов |
| Контейнеризация | Docker + Docker Compose | Стандарт деплоя, изоляция компонентов |
| DDNS | DuckDNS | Бесплатный динамический DNS для домашнего сервера |

**Архитектура:**
```
Client → Caddy (443) → FastAPI (8000) → Pond Mobile API
                     ↓
                  Vault (8200)
```

## План реализации

План состоял из 19 шагов, разделённых на логические блоки:

1. **Структура проекта** — Создание директорий и файлов модулей
2. **Конфигурация** — Pydantic Settings с .env
3. **Ядро безопасности** — Авторизация, IP whitelist, исключения
4. **Интеграция Vault** — Клиент для KV v2
5. **Прокси модуль** — HTTP-клиент для Pond Mobile API
6. **FastAPI приложение** — Router, middleware, lifespan
7. **API endpoints** — Health check и прокси endpoint
8. **Docker** — Dockerfile, docker-compose.yml (3 контейнера)
9. **Caddy** — Конфигурация reverse proxy и TLS
10. **Тесты** — pytest, фикстуры, покрытие
11. **Деплой** — init_vault.sh, deploy.sh

## Что реализовано

### Структура проекта
```
PondAPIProxy/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py          # GET /health, /health/ready
│   │   └── routes.py          # POST /proxy/v{version}/...
│   ├── core/
│   │   ├── exceptions.py      # ProxyError, UnauthorizedError, ForbiddenError, VaultConnectionError
│   │   ├── ip_whitelist.py    # Парсинг whitelist.txt
│   │   ├── proxy.py           # HTTPClient для Pond Mobile API
│   │   ├── security.py        # extract_bearer_token, validate_token
│   │   └── vault_client.py    # VaultClient (KV v2)
│   ├── models/
│   │   └── schemas.py         # Pydantic модели
│   ├── config.py              # Settings (Pydantic Settings)
│   ├── dependencies.py        # authenticated_proxy dependency
│   └── main.py                # FastAPI app, middleware, handlers
├── tests/
│   ├── conftest.py            # pytest fixtures
│   ├── test_api.py            # API endpoints tests
│   ├── test_proxy.py          # Proxy module tests
│   └── test_security.py       # Security tests
├── docker/
│   ├── Dockerfile             # Multi-stage build для API
│   ├── docker-compose.yml     # 3 сервиса: vault, api, caddy
│   └── Caddyfile              # Reverse proxy + TLS
├── deploy/
│   ├── init_vault.sh          # Инициализация Vault и запись токена
│   └── deploy.sh              # Скрипт деплоя
├── config/
│   └── whitelist.txt          # IP whitelist (пустой по умолчанию)
├── requirements.txt           # Зависимости Python
├── pytest.ini                 # Конфигурация pytest
├── .env.example               # Шаблон переменных окружения
├── .gitignore                 # .env, __pycache__, .venv
└── README.md                  # Документация
```

### Модули и их назначение

#### `/home/alexr/Dev/PondAPIProxy/src/config.py`
Pydantic Settings для загрузки конфигурации из .env:
- `POND_API_BASE_URL` — базовый URL Pond Mobile API
- `POND_API_TIMEOUT` — таймаут запросов (30s)
- `ALLOWED_TOKENS` — список разрешённых Bearer токенов
- `IP_WHITELIST_PATH` — путь к файлу whitelist
- `VAULT_*` — параметры подключения к Vault

#### `/home/alexr/Dev/PondAPIProxy/src/core/security.py`
Модуль безопасности:
- `extract_bearer_token()` — извлечение токена из Authorization header
- `validate_token()` — проверка токена против whitelist
- `require_valid_token()` — FastAPI dependency для авторизации

#### `/home/alexr/Dev/PondAPIProxy/src/core/vault_client.py`
Клиент HashiCorp Vault (KV v2):
- `VaultClient` — singleton-класс для работы с Vault
- `get_pond_token()` — получение токена Pond Mobile API из Vault
- `check_connection()` — проверка соединения

#### `/home/alexr/Dev/PondAPIProxy/src/core/proxy.py`
HTTP-клиент для Pond Mobile API:
- `PondProxy` — async HTTPClient с retry logic
- `cancel_lu_request()` — основной метод проксирования

#### `/home/alexr/Dev/PondAPIProxy/src/dependencies.py`
FastAPI dependencies:
- `authenticated_proxy` — комбинированная проверка: IP + токен + Vault

#### `/home/alexr/Dev/PondAPIProxy/src/api/routes.py`
API endpoint:
- `POST /proxy/v{version}/network-access/cancel-lu-requests?iccid={iccid}`

#### `/home/alexr/Dev/PondAPIProxy/docker/docker-compose.yml`
Три контейнера:
1. **vault** — hashicorp/vault:latest (port 8200)
2. **api** — pondapiproxy-api (port 8000)
3. **caddy** — caddy:latest (ports 80, 443)

## Результаты

### Технический стек

| Категория | Технология |
|-----------|------------|
| Язык | Python 3.11+ |
| Фреймворк | FastAPI |
| HTTP клиент | httpx (async) |
| Конфигурация | pydantic-settings |
| Vault | hvac |
| Контейнеризация | Docker + Docker Compose |
| Reverse Proxy | Caddy |
| Тестирование | pytest |

### API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Статус сервиса (версия, timestamp) |
| GET | `/health/ready` | Готовность (Vault, IP whitelist) |
| POST | `/proxy/v{version}/network-access/cancel-lu-requests?iccid={iccid}` | Прокси endpoint |

### Заголовки для прокси
```
Authorization: Bearer {token}
request-id: {uuid}
version: 2.1
```

### Безопасность
1. **Авторизация**: Bearer токены через `ALLOWED_TOKENS`
2. **IP whitelist**: Файл `/app/config/whitelist.txt` (построчно CIDR)
3. **Vault**: Pond Mobile токен хранится в KV v2 по пути `secret/pondmobile`
4. **TLS**: Автоматический HTTPS через Caddy + Let's Encrypt

### Тесты
Покрытие:
- `test_api.py` — health endpoints, proxy endpoint
- `test_security.py` — token extraction, validation, IP whitelist
- `test_proxy.py` — HTTP client, retry logic

## Проблемы и откаты

**Нет**

Проект реализован согласно плану без существенных отклонений. Все компоненты работают вместе, архитектура соответствует требованиям Research stage.

## Статус

Done

---

**Дополнительно:**
- Проект готов к деплою на домашний сервер
- Необходимо настроить DuckDNS домен
- При первом запуске требуется выполнить `deploy/init_vault.sh` для записи токена Pond Mobile API
- Для production рекомендуется использовать production-mode Vault (не dev)
