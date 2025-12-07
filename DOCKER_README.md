# Image Processor - Docker Deployment

This project provides Docker containers for both the frontend and backend services.

## Quick Start

### Development
```bash
# Start both services
docker-compose up --build

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Production
```bash
# Start with production configuration
docker-compose -f docker-compose.prod.yml up --build -d

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Services

### Backend
- **Port**: 8000
- **Health Check**: `/health` endpoint
- **Technology**: Python 3.12 + FastAPI + PyTorch
- **Image Processing**: Transformers for AI image analysis

### Frontend
- **Port**: 80
- **Technology**: React + TypeScript + Vite
- **Server**: Nginx with optimized configuration
- **API Proxy**: Automatic routing to backend

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Backend Configuration
PYTHONPATH=/app
ENV=production

# Optional: Custom model paths, API keys, etc.
MODEL_CACHE_DIR=/app/models
MAX_IMAGE_SIZE=10MB
```

### Custom Domains (Production)

Edit `docker-compose.prod.yml`:

1. Replace `yourdomain.com` with your actual domain
2. Replace `your-email@domain.com` with your email for Let's Encrypt
3. Generate basic auth password for Traefik dashboard:
   ```bash
   htpasswd -c .htpasswd admin
   ```

## Development Commands

```bash
# Build only
docker-compose build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v
```

## Production Deployment

### Prerequisites
- Docker & Docker Compose installed
- Domain name pointing to your server
- Ports 80, 443 open

### Steps

1. **Clone and configure**:
   ```bash
   git clone <your-repo>
   cd project_transformers
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Update domain configuration**:
   ```bash
   # Edit docker-compose.prod.yml
   sed -i 's/yourdomain.com/your-actual-domain.com/g' docker-compose.prod.yml
   sed -i 's/your-email@domain.com/your-email@domain.com/g' docker-compose.prod.yml
   ```

3. **Deploy**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Verify**:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   curl -f https://your-domain.com/health
   ```

## Scaling

### Horizontal Scaling
```bash
# Scale backend
docker-compose -f docker-compose.prod.yml up --scale backend-prod=3 -d

# Scale with load balancer
docker-compose -f docker-compose.prod.yml up --scale frontend-prod=2 -d
```

### Resource Limits
Edit `docker-compose.prod.yml` to adjust memory/CPU limits:
```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2'
    reservations:
      memory: 2G
      cpus: '1'
```

## Monitoring

### Health Checks
- Frontend: `http://localhost/`
- Backend: `http://localhost:8000/health`
- Traefik Dashboard: `http://localhost:8080` (production)

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Follow with timestamps
docker-compose logs -f -t
```

## Troubleshooting

### Common Issues

1. **Port conflicts**:
   ```bash
   # Check what's using port 80/8000
   sudo lsof -i :80
   sudo lsof -i :8000
   ```

2. **Build failures**:
   ```bash
   # Clean build
   docker-compose build --no-cache
   docker system prune -f
   ```

3. **Permission issues**:
   ```bash
   # Fix data directory permissions
   sudo chown -R 1000:1000 ./data
   ```

4. **Memory issues**:
   ```bash
   # Check container resources
   docker stats
   
   # Increase Docker memory limit in Docker Desktop
   # Or adjust container limits in compose file
   ```

## Backup & Restore

### Backup
```bash
# Backup application data
docker run --rm -v project_transformers_app-data:/data -v $(pwd):/backup alpine tar czf /backup/app-data-backup.tar.gz -C /data .

# Backup database (if added)
docker-compose exec backend python manage.py dumpdata > backup.json
```

### Restore
```bash
# Restore application data
docker run --rm -v project_transformers_app-data:/data -v $(pwd):/backup alpine tar xzf /backup/app-data-backup.tar.gz -C /data
```

## Security Considerations

1. **Use HTTPS in production** (handled by Traefik)
2. **Regular updates**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```
3. **Firewall configuration**:
   ```bash
   # Allow only necessary ports
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```
4. **Environment secrets**: Use Docker secrets in production
5. **Regular backups**: Set up automated backups

## Performance Optimization

1. **Image optimization**: Use multi-stage builds (already implemented)
2. **Resource limits**: Set appropriate memory/CPU limits
3. **Caching**: Nginx handles static file caching
4. **Compression**: Gzip enabled for static assets
5. **CDN**: Consider adding CloudFlare for global distribution