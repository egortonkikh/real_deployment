# Maison Auto

Демо-каталог люксовых автомобилей: Mercedes-Benz, BMW, Audi, Porsche, Lexus.
Фронтенд на HTML/CSS/JS, бэкенд на FastAPI, инфраструктура в Docker Compose.

> **О проекте.** Это мой первый опыт самостоятельного деплоя реального (тестового) сайта.
> Я учусь DevOps и писал бэкенд руками. Здесь — что реализовано и чему я научился.

## Стек

- **Frontend**: HTML, CSS, ванильный JS
- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic 2
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Reverse proxy**: nginx 1.27
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, pytest-cov, fakeredis
- **CI/CD**: GitHub Actions

## Архитектура

```
browser → nginx (:80) → FastAPI (:8000) → PostgreSQL (:5432)
                          ↓
                       Redis (:6379)
```

nginx отдаёт статику фронтенда из примонтированной папки и проксирует `/api/*` на FastAPI. FastAPI ходит в PostgreSQL за данными, в Redis за кэшем. Все сервисы в одной Docker-сети, наружу торчит только 80 порт.

## API

| Endpoint | Method | Описание |
|---|---|---|
| `/api/health` | GET | Health check (`SELECT 1` из БД) |
| `/api/cars` | GET | Список машин, опционально `?brand=`. Кэшируется в Redis на 60 сек |
| `/api/cars/{id}` | GET | Одна машина по ID |
| `/api/cars` | POST | Создать машину. **Инвалидирует кэш** `cars:*` |
| `/api/leads` | POST | Создать лид (заявку). Rate limit: 4 запроса/мин с IP |

## Безопасность

nginx security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy`. CSP настроен под фронтенд — разрешены Google Fonts и inline `data:` SVG силуэты машин. Rate limit на `/api/leads` возвращает `429 Too Many Requests` при превышении.

## Запуск

```bash
cp .env.example .env            # поменяй пароль PostgreSQL
docker compose up -d --build
```

- Сайт: http://localhost
- API: http://localhost/api/cars

## Тесты

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest --cov=app --cov-report=term-missing
```

9 тестов, покрытие 99%. Тестируется: все endpoints, кэш-логика (hit/miss), инвалидация при мутациях, fallback на БД при падении Redis. Redis подменяется `fakeredis` — реальные сервисы в тестах не нужны.

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`):

- **test** — Python 3.12 (как в Dockerfile), `pytest --cov`, загрузка `.coverage` как артефакта
- **build** — Docker build (пока без пуша), кэш слоёв в GitHub Actions cache

Запускается на push в `main` (при изменениях в `backend/`, `nginx/`, `frontend/`, `.github/workflows/`) и на любой PR в `main`.

## Структура проекта

```
luxury-cars/
├── backend/
│   ├── app/                 # FastAPI: main, db, models, seed
│   ├── tests/               # conftest.py + test_api.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── pytest.ini
├── frontend/                # index.html, css/, js/, img/
├── nginx/
│   └── default.conf         # reverse proxy + security headers + rate limit
├── .github/workflows/
│   └── ci.yml               # GitHub Actions
├── docker-compose.yml
├── .env.example
└── README.md
```

## Чему я научился

Это мой первый боевой проект. В процессе разобрался с:

- **Docker Compose оркестрация**: 4 сервиса (db, redis, app, nginx), healthchecks, `depends_on` с условиями `service_healthy`
- **Тестирование FastAPI**: `TestClient`, `autouse`-фикстуры для пересоздания БД между тестами, `fakeredis` для изоляции Redis, `pytest-cov` для измерения покрытия
- **Cache-aside pattern**: кэш в Redis с TTL, инвалидация через `SCAN` + `DELETE` по паттерну `cars:*`, fallback на БД через `try/except redis.RedisError`
- **nginx hardening**: security headers, Content-Security-Policy с учётом реальных источников фронта (Google Fonts, `data:` SVG), rate limit через `limit_req_zone` + `limit_req_status 429`
- **CI/CD**: GitHub Actions с двумя jobs, кэширование pip и Docker слоёв через `actions/cache` и `type=gha`

Что было сложно:

- Python 3.14 vs pinned-зависимости — у старых версий `psycopg-binary` и `sqlalchemy` нет колёс под 3.14, пришлось бампать до 3.3.6 и 2.0.55 соответственно
- PEP 668 — Debian защищает системный Python от `pip install --user`, пришлось разобраться с venv
- starlette TestClient перешёл с `httpx` на `httpx2` — неочевидный breaking change, лечится добавлением `httpx2` в `requirements-dev.txt`

## Roadmap

- [ ] Пуш Docker image в GHCR (GitHub Container Registry) из CI
- [ ] Deploy на VPS через SSH + `docker compose pull && up -d`
- [ ] HTTPS через Let's Encrypt / Certbot
- [ ] Логирование (Loki или ELK)
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Загрузка фото машин (backend + S3-совместимое хранилище)

## Фото

См. `frontend/img/README.txt`.

## Лицензия

Учебный проект. Не для коммерческого использования.