## ✅ Basic Technical Requirements

This project implements a production-style backend service using modern tools and infrastructure. The core requirements are:

### 🔧 Functionality
- [ ] Shorten a long URL via REST API (`POST /shorten`)
- [ ] Redirect a short URL to the original (`GET /{short_code}`)
- [ ] Track per-access analytics (IP, timestamp, user-agent)
- [ ] View basic usage stats (`GET /stats/{short_code}`)

### 🗃️ Storage
- [ ] **PostgreSQL** for storing original URLs and short codes
- [ ] **Redis** for caching frequent short code lookups
- [ ] **MongoDB** for storing analytics logs

### ⚙️ Backend Stack
- [ ] **Python 3.11+**
- [ ] **FastAPI** for async REST API
- [ ] **asyncpg**, **motor**, and **redis-py** for async DB access
- [ ] **Docker** for containerization

### ☸️ Deployment
- [ ] Deploy all components on **Kubernetes via Minikube**
- [ ] Define resources using **YAML manifests**
- [ ] (Optional) Use **Terraform** to provision Kubernetes resources

### 📈 Observability
- [ ] Expose custom metrics via `/metrics` for **Prometheus**
- [ ] Create dashboards in **Grafana** to monitor:
  - Request count per endpoint
  - Redirect latency
  - Cache hit ratio
  - Top-used short codes

### 🧪 Testing
- [ ] Unit tests for core logic (shortening, redirecting)
- [ ] Integration tests for full API workflows

