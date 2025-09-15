# fastapi-url-shortener

URL shortener built with FastAPI.

### Stack:
- API: FastAPI
- ORM: SQLModel
- Databases: 
    - PostgresQL (URL storage)
    - Redis (cache of recent/frequent URLs)
    - MongoDB (analytics)
- Telemetry: Prometheus
- Auth: HTTP bearer tokens

### REST API
Public endpoints:
- `POST /{url}` - posting url, returning short url
- `GET /{short_url}` - redirects to original site with 303 from short url

Private endpoints (bearer token protected):
- `/metrics` - Prometheus scraping endpoint
- `/logs`

Additionally, Swagger docs are available via `/docs`.

### Deployment

1. Set up `.env`:
```
POSTGRES_URI = "postgresql+asyncpg://user:password@postgres:5432/database_name"
MONGO_URI = "mongodb://root:example@mongodb:27017"
REDIS_URI="redis://redis:6379"
API_TOKEN="abcd1234"
```

2. Deploy with `docker`:
```
docker compose up -d
```

Endpoints should then be available on port 8000, with docs on endpoint `/docs`.

### Tests
A test-runner service is available:
```
docker compose up --build --abort-on-container-exit test_runner
```
