# Deployment Guide

## Prerequisites

- Docker & Docker Compose OR
- Python 3.10+, Node.js 18+, PostgreSQL 15+

## Option 1: Docker Deployment (Recommended)

### Windows
```powershell
.\start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

This will:
1. Build all Docker containers
2. Start PostgreSQL, Redis, Backend, and Frontend
3. Create database tables
4. Load sample crime data

### Manual Docker Commands

```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Option 2: Local Development

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env and configure database

# Create database tables
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

# Load sample data
python scripts/ingest_data.py

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env.local

# Start development server
npm start
```

## Production Deployment

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://host:6379
SECRET_KEY=your-production-secret-key-min-32-chars
OPENROUTE_API_KEY=your-api-key  # Optional for routing
```

**Frontend (.env.production):**
```env
REACT_APP_API_URL=https://your-api-domain.com/api
```

### Build for Production

**Backend:**
```bash
# Using Gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

**Frontend:**
```bash
npm run build
# Serve the 'build' folder with nginx or any static file server
```

### Nginx Configuration Example

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## Cloud Deployment

### AWS Deployment

1. **Database**: Amazon RDS (PostgreSQL)
2. **Cache**: Amazon ElastiCache (Redis)
3. **Backend**: AWS Elastic Beanstalk or ECS
4. **Frontend**: AWS S3 + CloudFront
5. **API Gateway**: API Gateway + Lambda (optional)

### Azure Deployment

1. **Database**: Azure Database for PostgreSQL
2. **Cache**: Azure Cache for Redis
3. **Backend**: Azure App Service
4. **Frontend**: Azure Static Web Apps
5. **Container**: Azure Container Instances or AKS

### Google Cloud Deployment

1. **Database**: Cloud SQL (PostgreSQL)
2. **Cache**: Cloud Memorystore (Redis)
3. **Backend**: Cloud Run or App Engine
4. **Frontend**: Firebase Hosting or Cloud Storage

## Monitoring & Logging

### Application Monitoring

```python
# Add to backend/requirements.txt
sentry-sdk==1.40.0
prometheus-client==0.19.0
```

```python
# Add to app/main.py
import sentry_sdk
from prometheus_client import make_asgi_app

# Sentry
sentry_sdk.init(dsn="your-sentry-dsn")

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

### Log Aggregation

- ELK Stack (Elasticsearch, Logstash, Kibana)
- Grafana + Loki
- Cloud provider logging (CloudWatch, Azure Monitor, Cloud Logging)

## Scaling Considerations

1. **Horizontal Scaling**:
   - Load balancer (nginx, AWS ALB, Azure Load Balancer)
   - Multiple backend instances
   - Stateless design (use Redis for sessions)

2. **Database Scaling**:
   - Read replicas for read-heavy workloads
   - Connection pooling (PgBouncer)
   - Sharding for very large datasets

3. **Caching**:
   - Redis for API response caching
   - CDN for frontend assets
   - Database query caching

4. **WebSocket Scaling**:
   - Redis Pub/Sub for multi-instance WebSocket
   - Socket.IO with Redis adapter (if switching)

## Security Checklist

- [ ] Use HTTPS/TLS in production
- [ ] Enable CORS only for trusted domains
- [ ] Implement rate limiting (e.g., slowapi)
- [ ] Use strong secret keys (32+ characters)
- [ ] Sanitize user inputs
- [ ] Enable CSRF protection
- [ ] Regular security updates
- [ ] Database connection encryption
- [ ] Secure API keys (use environment variables)
- [ ] Implement authentication/authorization

## Backup Strategy

### Database Backups

```bash
# Manual backup
docker-compose exec db pg_dump -U crime_user crime_db > backup.sql

# Restore
docker-compose exec -T db psql -U crime_user crime_db < backup.sql
```

### Automated Backups

- AWS RDS automated backups
- Azure Database automated backups
- Cron job with pg_dump
- Cloud provider backup services

## Troubleshooting

### Backend not starting
```bash
# Check logs
docker-compose logs backend

# Check database connection
docker-compose exec backend python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"
```

### Frontend not connecting to API
```bash
# Check API URL in browser console
# Verify CORS settings in backend
# Check network tab for failed requests
```

### WebSocket not connecting
```bash
# Check WebSocket URL (ws:// vs wss://)
# Verify proxy configuration for WebSocket upgrade
# Check firewall rules
```

## Performance Optimization

1. **Database Indexes**: Add indexes on frequently queried columns
2. **Query Optimization**: Use EXPLAIN ANALYZE to optimize slow queries
3. **Caching**: Implement Redis caching for expensive operations
4. **CDN**: Use CDN for static assets
5. **Compression**: Enable gzip compression
6. **Code Splitting**: Optimize React bundle size
7. **Image Optimization**: Compress and lazy-load images

## Maintenance

### Database Migrations

```bash
# Using Alembic
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Dependency Updates

```bash
# Backend
pip list --outdated
pip install --upgrade package-name

# Frontend
npm outdated
npm update
```
