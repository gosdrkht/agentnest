# AgentNest Development Guide

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  username VARCHAR(100) UNIQUE NOT NULL,
  full_name VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE,
  balance DECIMAL(10, 2) DEFAULT 0,
  api_key VARCHAR(255) UNIQUE
);
```

### Agents Table
```sql
CREATE TABLE agents (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  docker_image VARCHAR(255) NOT NULL,
  status VARCHAR(50) DEFAULT 'stopped', -- running, stopped, crashed, pending
  container_id VARCHAR(255),
  cpu_limit DECIMAL(10, 2) DEFAULT 1.0,
  memory_limit_mb INTEGER DEFAULT 512,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_run TIMESTAMP,
  logs TEXT
);
```

### Usage Table (for billing)
```sql
CREATE TABLE usage (
  id SERIAL PRIMARY KEY,
  agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  cpu_hours DECIMAL(10, 2),
  memory_gb_hours DECIMAL(10, 2),
  uptime_hours DECIMAL(10, 2),
  cost DECIMAL(10, 2),
  period_start TIMESTAMP,
  period_end TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Billing Table
```sql
CREATE TABLE billing (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount DECIMAL(10, 2) NOT NULL,
  status VARCHAR(50) DEFAULT 'pending', -- pending, paid, failed, refunded
  stripe_payment_id VARCHAR(255),
  invoice_number VARCHAR(255),
  period_start TIMESTAMP,
  period_end TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  paid_at TIMESTAMP
);
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new account
- `POST /auth/login` - Login (returns JWT token)
- `POST /auth/refresh` - Refresh JWT token
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout

### Agents
- `GET /agents` - List user's agents
- `POST /agents` - Create/deploy new agent
- `GET /agents/{agent_id}` - Get agent details
- `PUT /agents/{agent_id}` - Update agent
- `DELETE /agents/{agent_id}` - Delete agent
- `POST /agents/{agent_id}/start` - Start agent
- `POST /agents/{agent_id}/stop` - Stop agent
- `GET /agents/{agent_id}/logs` - Get agent logs

### Billing
- `GET /billing/invoices` - List invoices
- `GET /billing/usage` - Get current usage
- `POST /billing/payment-method` - Add payment method (Stripe)
- `GET /billing/balance` - Get account balance

### Monitoring
- `GET /monitoring/{agent_id}/metrics` - Get agent metrics
- `GET /monitoring/{agent_id}/cpu` - Get CPU usage
- `GET /monitoring/{agent_id}/memory` - Get memory usage

## Setup Instructions

### Local Development

1. **Clone and navigate:**
```bash
git clone https://github.com/gosdrkht/agentnest.git
cd agentnest
```

2. **Start services with Docker:**
```bash
docker-compose up -d
```

3. **Setup backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

4. **Initialize database:**
```bash
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

5. **Run backend:**
```bash
python -m uvicorn app.main:app --reload
```

6. **Setup frontend (new terminal):**
```bash
cd frontend
npm install
npm start
```

## Environment Variables

Create `.env` file in backend folder:

```
# Database
DATABASE_URL=postgresql://agentnest:password@localhost:5432/agentnest

# JWT
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...

# Docker
DOCKER_SOCKET=/var/run/docker.sock

# App
APP_NAME=AgentNest
APP_VERSION=0.1.0
DEBUG=True
```

## Pricing Strategy

### Compute Costs (Margin based)
- Base cost per CPU hour: $0.0116 (AWS t3.micro equivalent)
- Base cost per GB memory hour: $0.0024
- AgentNest margin: 10-15%

### Example Pricing
- Small agent (0.5 CPU, 256MB RAM): $5-15/month
- Medium agent (1 CPU, 512MB RAM): $10-30/month
- Large agent (2 CPU, 1GB RAM): $20-60/month

### Revenue per Customer
- 1 small agent = $5-15/month
- 3 agents average = $45/month
- 50 customers × $45 = $2,250/month
- 100 customers × $45 = $4,500/month

## Deployment

### Staging (AWS EC2)
```bash
# SSH into server
ssh -i key.pem ubuntu@your-instance-ip

# Clone and setup
git clone https://github.com/gosdrkht/agentnest.git
cd agentnest

# Docker compose up
docker-compose up -d
```

### Production (Future)
- Use Kubernetes for scaling
- Multi-region deployment
- CDN for frontend
- Auto-scaling groups

## Testing

### Backend Tests
```bash
pip install pytest
pytest tests/
```

### Frontend Tests
```bash
npm test
```
