# Development Docker Setup

Quick setup for local development testing.

## Quick Start

```bash
# Start development environment
./deploy-dev.sh

# Access your application:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## What's Included

- **Backend**: FastAPI server with image processing capabilities
- **Frontend**: React app with Nginx serving
- **Auto-restart**: Containers restart automatically if they crash
- **Volume mounting**: Backend source code mounted for development

## Useful Commands

```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f

# View specific service logs
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend

# Stop everything
docker-compose -f docker-compose.dev.yml down

# Restart services
./deploy-dev.sh

# Clean build (if you have issues)
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d
```

## Testing Your Setup

1. **Test Backend Health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Image Upload**:
   - Go to http://localhost:3000
   - Upload an image
   - Check if analysis works

3. **Check Logs** if something doesn't work:
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f
   ```

## Troubleshooting

### Port Conflicts
If ports 3000 or 8000 are already in use:
```bash
# Check what's using the ports
sudo lsof -i :3000
sudo lsof -i :8000

# Kill the process or change ports in docker-compose.dev.yml
```

### Build Issues
```bash
# Clean everything and rebuild
docker-compose -f docker-compose.dev.yml down
docker system prune -f
./deploy-dev.sh
```

### Backend Not Starting
Check backend logs:
```bash
docker-compose -f docker-compose.dev.yml logs backend
```

Common issues:
- Missing Python dependencies
- GPU/CUDA issues (the backend should work on CPU)
- File permissions

### Frontend Not Loading
Check frontend logs:
```bash
docker-compose -f docker-compose.dev.yml logs frontend
```

Common issues:
- Build failures
- Nginx configuration errors