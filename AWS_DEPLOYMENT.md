# 🚀 Deploy AgentNest to AWS

> Production deployment guide for AgentNest on AWS EC2 with RDS, S3, and Route 53

## 📋 Prerequisites

- AWS Account with admin access
- Domain name (e.g., `agentnest.io`)
- SSH key pair for EC2
- Basic AWS/Linux knowledge
- ~$50-100/month budget for development tier

## 💰 Estimated Monthly Costs

| Service | Instance | Cost/Month |
|---------|----------|------------|
| EC2 | t3.medium | $28.29 |
| RDS PostgreSQL | t3.small | $32.88 |
| S3 | 100GB storage | $2.30 |
| Route 53 | Domain hosting | $0.50 |
| Bandwidth | 1TB outbound | $92.16 |
| **Total** | **Development** | **~$156/month** |

**For production (t3.large EC2 + t3.medium RDS): ~$250-400/month**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Route 53 (DNS)                      │
│    agentnest.io → CloudFront CDN           │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│    CloudFront CDN (Optional but recommended)│
│    - Cache static assets                    │
│    - Serve React app globally               │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  Application Load Balancer (Port 80/443)    │
│  - SSL/TLS termination                      │
│  - Route traffic to EC2 instances           │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│   EC2 Instance (Ubuntu 22.04)               │
│   - Docker containers (backend + frontend)  │
│   - Docker daemon (runs agent containers)   │
└────────────┬────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────┐   ┌──────────────┐
│   RDS    │   │   S3 Bucket  │
│PostgreSQL│   │ (Backups)    │
└──────────┘   └──────────────┘
```

---

## Step 1: Create AWS Resources

### 1.1 Create VPC & Security Groups

```bash
# Login to AWS Console → VPC Dashboard
# Or use AWS CLI:

# Create VPC
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=agentnest-vpc}]' \
  --query 'Vpc.VpcId' \
  --output text)

echo "VPC ID: $VPC_ID"

# Create public subnet
SUBNET_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --query 'Subnet.SubnetId' \
  --output text)

echo "Subnet ID: $SUBNET_ID"
```

### 1.2 Create Security Group

```bash
# Create security group
SG_ID=$(aws ec2 create-security-group \
  --group-name agentnest-sg \
  --description "AgentNest security group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

echo "Security Group ID: $SG_ID"

# Allow SSH (port 22)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# Allow HTTP (port 80)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Allow HTTPS (port 443)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

---

## Step 2: Create RDS Database

### 2.1 Create PostgreSQL RDS Instance

```bash
aws rds create-db-instance \
  --db-instance-identifier agentnest-db \
  --db-instance-class db.t3.small \
  --engine postgres \
  --engine-version 15.3 \
  --master-username postgres \
  --master-user-password "YOUR_STRONG_PASSWORD_HERE" \
  --allocated-storage 100 \
  --storage-type gp3 \
  --publicly-accessible false \
  --db-subnet-group-name default \
  --vpc-security-group-ids $SG_ID \
  --backup-retention-period 7 \
  --multi-az false
```

**⚠️ Save the endpoint and password securely!**

Wait ~15 minutes for RDS to be ready. Check status:

```bash
aws rds describe-db-instances \
  --db-instance-identifier agentnest-db \
  --query 'DBInstances[0].{Status:DBInstanceStatus,Endpoint:Endpoint.Address}'
```

---

## Step 3: Launch EC2 Instance

### 3.1 Create Key Pair

```bash
# Create SSH key pair
aws ec2 create-key-pair \
  --key-name agentnest-key \
  --query 'KeyMaterial' \
  --output text > agentnest-key.pem

# Set permissions
chmod 400 agentnest-key.pem
```

### 3.2 Launch EC2 Instance

```bash
# Get Ubuntu 22.04 LTS AMI ID
AMI_ID=$(aws ec2 describe-images \
  --owners 099720109477 \
  --filters 'Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*' \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text)

echo "AMI ID: $AMI_ID"

# Launch instance
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.medium \
  --key-name agentnest-key \
  --security-group-ids $SG_ID \
  --subnet-id $SUBNET_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=agentnest-app}]' \
  --user-data file://user-data.sh \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "Instance ID: $INSTANCE_ID"

# Get public IP
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
```

### 3.3 Create User Data Script

Create `user-data.sh`:

```bash
#!/bin/bash
set -e

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Install Node.js 18 (for frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 (process manager)
sudo npm install -g pm2

# Create app directory
mkdir -p /home/ubuntu/agentnest
cd /home/ubuntu/agentnest

# Clone repository (or download from S3)
git clone https://github.com/gosdrkht/agentnest.git .

# Create .env file (backend)
cat > /home/ubuntu/agentnest/backend/.env << EOF
DATABASE_URL=postgresql://postgres:YOUR_DB_PASSWORD@YOUR_RDS_ENDPOINT:5432/agentnest
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=$(openssl rand -hex 32)
STRIPE_SECRET_KEY=sk_live_your_stripe_key
CORS_ORIGINS=https://agentnest.io,https://www.agentnest.io
ENVIRONMENT=production
EOF

# Create .env file (frontend)
cat > /home/ubuntu/agentnest/frontend/.env << EOF
REACT_APP_API_URL=https://api.agentnest.io
EOF

# Fix permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/agentnest

# Start services with PM2
cd /home/ubuntu/agentnest
pm2 start "docker-compose up -d" --name agentnest

# Save PM2 process list
pm2 save
sudo pm2 startup ubuntu -u ubuntu --hp /home/ubuntu

echo "Setup complete! AGentNest is starting up..."
```

---

## Step 4: Configure Domain & SSL

### 4.1 Point Domain to EC2

1. Get EC2 Elastic IP:
   ```bash
   ELASTIC_IP=$(aws ec2 allocate-address \
     --domain vpc \
     --instance-id $INSTANCE_ID \
     --query 'PublicIp' \
     --output text)
   
   echo "Elastic IP: $ELASTIC_IP"
   ```

2. In Route 53:
   - Create A record: `agentnest.io` → `$ELASTIC_IP`
   - Create CNAME: `api.agentnest.io` → `agentnest.io`
   - Create CNAME: `www.agentnest.io` → `agentnest.io`

### 4.2 Setup SSL with Let's Encrypt

SSH into EC2:

```bash
ssh -i agentnest-key.pem ubuntu@YOUR_ELASTIC_IP

# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone \
  -d agentnest.io \
  -d www.agentnest.io \
  -d api.agentnest.io \
  --agree-tos \
  --email admin@agentnest.io

# Verify certificate
sudo certbot certificates
```

---

## Step 5: Configure Nginx Reverse Proxy

### 5.1 Install Nginx

```bash
sudo apt-get install -y nginx

# Create Nginx config
sudo tee /etc/nginx/sites-available/agentnest > /dev/null << 'EOF'
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name agentnest.io www.agentnest.io api.agentnest.io;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name agentnest.io www.agentnest.io;

    ssl_certificate /etc/letsencrypt/live/agentnest.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/agentnest.io/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name api.agentnest.io;

    ssl_certificate /etc/letsencrypt/live/agentnest.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/agentnest.io/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 10M;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
    }

    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable config
sudo ln -s /etc/nginx/sites-available/agentnest /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Start Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## Step 6: Update Docker Compose for Production

Update `docker-compose.yml` on EC2:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: agentnest-db
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: agentnest
    # Use RDS instead of Docker:
    # Remove this service and use DATABASE_URL in backend

  redis:
    image: redis:7-alpine
    container_name: agentnest-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: agentnest-backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/agentnest
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      STRIPE_SECRET_KEY: ${STRIPE_SECRET_KEY}
      ENVIRONMENT: production
      DEBUG: "False"
    depends_on:
      - redis
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: agentnest-frontend
    command: serve -s build -l 3000
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: https://api.agentnest.io
    restart: unless-stopped

volumes:
  redis_data:
```

---

## Step 7: Setup Monitoring & Logging

### 7.1 CloudWatch Logs

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Configure CloudWatch
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard

# Start agent
sudo systemctl start amazon-cloudwatch-agent
sudo systemctl enable amazon-cloudwatch-agent
```

### 7.2 Setup Alarms

```bash
# High CPU usage
aws cloudwatch put-metric-alarm \
  --alarm-name agentnest-high-cpu \
  --alarm-description "Alert when CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID
```

---

## Step 8: Setup Backups

### 8.1 RDS Automated Backups

```bash
# Already enabled with 7-day retention
# Verify:
aws rds describe-db-instances \
  --db-instance-identifier agentnest-db \
  --query 'DBInstances[0].BackupRetentionPeriod'
```

### 8.2 Database Backups to S3

```bash
# Create S3 bucket
aws s3 mb s3://agentnest-backups-$(date +%s)

# Create backup script
cat > ~/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_FILE="agentnest-db-$(date +%Y%m%d-%H%M%S).sql"
DB_HOST="your-rds-endpoint.rds.amazonaws.com"
DB_NAME="agentnest"
DB_USER="postgres"

pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_FILE
aws s3 cp $BACKUP_FILE s3://agentnest-backups/
rm $BACKUP_FILE
EOF

# Make executable
chmod +x ~/backup-db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup-db.sh") | crontab -
```

---

## Step 9: Test Production Deployment

```bash
# Test API
curl -X POST https://api.agentnest.io/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123!"
  }'

# Test frontend
open https://agentnest.io

# Check logs
docker logs agentnest-backend
docker logs agentnest-frontend

# Monitor performance
sudo cloudwatch-cli get-metric-statistics \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID \
  --statistics Average \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300
```

---

## 🚨 Troubleshooting

### Backend won't connect to RDS

```bash
# Check security group
aws ec2 describe-security-groups --group-ids $SG_ID

# Ensure port 5432 is open from EC2 to RDS
# Test connection
psql -h YOUR_RDS_ENDPOINT -U postgres -d agentnest
```

### SSL certificate issues

```bash
# Verify certificate
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Docker socket permission denied

```bash
# Add ubuntu to docker group
sudo usermod -aG docker ubuntu

# Restart Docker
sudo systemctl restart docker

# Logout and login again
exit
ssh -i agentnest-key.pem ubuntu@YOUR_ELASTIC_IP
```

---

## 📊 Monitoring & Alerts

### CloudWatch Dashboard

Create dashboard for monitoring:

```bash
aws cloudwatch put-dashboard \
  --dashboard-name AgentNest \
  --dashboard-body file://dashboard.json
```

### Key Metrics to Monitor

- **CPU Utilization** - Alert if > 80% for 15 min
- **Memory Usage** - Alert if > 90% for 10 min
- **Disk Space** - Alert if < 20% free
- **API Response Time** - Alert if p99 > 5s
- **Error Rate** - Alert if > 1% of requests
- **Database Connections** - Alert if > 90% of max

---

## ✅ Deployment Checklist

- [ ] AWS account created
- [ ] RDS PostgreSQL instance deployed
- [ ] EC2 instance launched
- [ ] Domain registered and pointed to EC2 IP
- [ ] SSL certificate installed
- [ ] Nginx reverse proxy configured
- [ ] Docker Compose running on EC2
- [ ] Backend connected to RDS
- [ ] Frontend built and served
- [ ] SSL certificate auto-renewal configured
- [ ] CloudWatch monitoring enabled
- [ ] Database backups configured
- [ ] Health checks passing

---

## 🎉 You're Live!

Your AgentNest is now running in production!

**Next Steps:**
1. Set up Stripe billing
2. Configure email notifications
3. Monitor performance metrics
4. Get first customers
5. Iterate based on feedback

**Support:**
- Logs: `docker logs -f agentnest-backend`
- Nginx: `sudo tail -f /var/log/nginx/error.log`
- CloudWatch: AWS Console → CloudWatch

