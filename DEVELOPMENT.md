# 📖 Development Guide - AgentNest

Complete development roadmap and technical documentation.

## 🗂 Database Schema

### Users Table
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  username VARCHAR(100) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  balance DECIMAL(10, 2) DEFAULT 0.00,
  status VARCHAR(20) DEFAULT 'active' -- active, suspended, deleted
);
```

### Agents Table
```sql
CREATE TABLE agents (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(20) DEFAULT 'stopped', -- running, stopped, crashed, deploying
  docker_image VARCHAR(255) NOT NULL,
  docker_container_id VARCHAR(255),
  environment_variables JSONB,
  port INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_started TIMESTAMP,
  last_stopped TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Agent Logs Table
```sql
CREATE TABLE agent_logs (
  id SERIAL PRIMARY KEY,
  agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  level VARCHAR(20), -- INFO, ERROR, WARNING, DEBUG
  message TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Usage Table (for billing)
```sql
CREATE TABLE usage (
  id SERIAL PRIMARY KEY,
  agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  cpu_cores DECIMAL(5, 2),
  memory_mb DECIMAL(10, 2),
  storage_gb DECIMAL(10, 2),
  uptime_hours DECIMAL(10, 2),
  cost_amount DECIMAL(10, 4),
  period_start TIMESTAMP,
  period_end TIMESTAMP,
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Billing Table
```sql
CREATE TABLE billing (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount DECIMAL(10, 2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(20) DEFAULT 'pending', -- pending, paid, failed, cancelled
  stripe_payment_id VARCHAR(255),
  stripe_invoice_id VARCHAR(255),
  billing_period_start TIMESTAMP,
  billing_period_end TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  paid_at TIMESTAMP,
  description TEXT
);
```

### Payments Table
```sql
CREATE TABLE payments (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount DECIMAL(10, 2) NOT NULL,
  payment_method VARCHAR(50), -- stripe, paypal, crypto
  stripe_charge_id VARCHAR(255),
  status VARCHAR(20) DEFAULT 'processing', -- processing, completed, failed
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP
);
```

---

## 🔌 API Endpoints (MVP)

### Authentication
```
POST   /api/auth/signup          # Register new user
POST   /api/auth/login           # Login user
POST   /api/auth/logout          # Logout
GET    /api/auth/me              # Get current user
POST   /api/auth/refresh-token   # Refresh JWT token
```

### Agents
```
GET    /api/agents               # List user's agents
POST   /api/agents               # Deploy new agent
GET    /api/agents/{id}          # Get agent details
PUT    /api/agents/{id}          # Update agent config
DELETE /api/agents/{id}          # Delete agent
POST   /api/agents/{id}/start    # Start agent
POST   /api/agents/{id}/stop     # Stop agent
POST   /api/agents/{id}/restart  # Restart agent
```

### Monitoring
```
GET    /api/agents/{id}/logs     # Get agent logs
GET    /api/agents/{id}/stats    # Get real-time stats (CPU, RAM, uptime)
GET    /api/agents/{id}/metrics  # Get historical metrics
```

### Billing
```
GET    /api/billing/invoice      # Get current billing period
GET    /api/billing/history      # Get billing history
GET    /api/billing/usage        # Get usage details
POST   /api/billing/payment      # Initiate payment
GET    /api/billing/payment/{id} # Get payment status
```

### Account
```
GET    /api/account/profile      # Get user profile
PUT    /api/account/profile      # Update profile
POST   /api/account/password     # Change password
DELETE /api/account              # Delete account
```

---

## 🏗 Backend Setup (Step by Step)

### 1. Initialize FastAPI Project

```bash
cd backend
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Create app/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

app = FastAPI(
    title="AgentNest API",
    description="AI Agent Hosting Platform",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "AgentNest API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### 3. Run the server

```bash
python -m uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs - You'll see Swagger UI!

---

## 🎨 Frontend Setup (Step by Step)

### 1. Create React app (if not using existing)

```bash
cd frontend
npx create-react-app . --template typescript
npm install react-router-dom axios
```

### 2. Create API client (src/services/api.ts)

```typescript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

---

## 🚀 Deployment Checklist

- [ ] Backend runs locally
- [ ] Frontend runs locally
- [ ] Database connected
- [ ] Authentication working
- [ ] Agent deployment working
- [ ] Billing logic tested
- [ ] Deploy to staging
- [ ] Load testing
- [ ] Security audit
- [ ] Deploy to production

---

## 📝 Environment Variables

Create `.env` files in both backend and frontend:

### backend/.env
```
DATABASE_URL=postgresql://user:password@localhost/agentnest
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
JWT_SECRET=your-secret-key-here
DOCKER_HOST=unix:///var/run/docker.sock
```

### frontend/.env
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_STRIPE_KEY=pk_test_...
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🐳 Docker Setup

See `docker-compose.yml` for local development with PostgreSQL, Redis, etc.

```bash
docker-compose up -d
```

---

## 📚 References

- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- PostgreSQL: https://www.postgresql.org/docs/
- Docker: https://docs.docker.com/
- Stripe API: https://stripe.com/docs/api
