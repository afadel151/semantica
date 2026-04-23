# Docker Deployment Guide

This guide explains how to build and deploy Semantica using Docker, and push the images to Docker Hub.

## Prerequisites

- Docker installed on your machine
- Docker Hub account (for pushing images)
- Basic understanding of Docker commands

## Architecture

The Docker setup consists of three services:

1. **Backend**: FastAPI server running on port 8000
2. **Frontend**: Nuxt.js application running on port 3000
3. **Nginx**: Reverse proxy that exposes the frontend on port 80 and proxies API requests to the backend

Only the frontend is exposed externally (via nginx on port 80). The backend is only accessible internally through the Docker network.

## Building and Running Locally

### Using Docker Compose (Recommended)

1. Build and start all services:
```bash
docker-compose up --build -d
```

2. Access the application at `http://localhost`

3. View logs:
```bash
docker-compose logs -f
```

4. Stop services:
```bash
docker-compose down
```

### Building Individual Images

#### Backend Image

```bash
cd backend
docker build -t semantica-backend:latest .
```

#### Frontend Image

```bash
cd frontend
docker build -t semantica-frontend:latest .
```

## Pushing to Docker Hub

### 1. Login to Docker Hub

```bash
docker login
```

Enter your Docker Hub username and password when prompted.

### 2. Tag Images for Docker Hub

Replace `yourusername` with your actual Docker Hub username.

```bash
# Tag backend image
docker tag semantica-backend:latest yourusername/semantica-backend:latest
docker tag semantica-backend:latest yourusername/semantica-backend:v1.0.0

# Tag frontend image
docker tag semantica-frontend:latest yourusername/semantica-frontend:latest
docker tag semantica-frontend:latest yourusername/semantica-frontend:v1.0.0
```

### 3. Push Images to Docker Hub

```bash
# Push backend image
docker push yourusername/semantica-backend:latest
docker push yourusername/semantica-backend:v1.0.0

# Push frontend image
docker push yourusername/semantica-frontend:latest
docker push yourusername/semantica-frontend:v1.0.0
```

### 4. Update docker-compose.yml for Production

After pushing to Docker Hub, update the `docker-compose.yml` to use the remote images instead of building locally:

```yaml
services:
  backend:
    image: yourusername/semantica-backend:latest
    # Remove build section
    container_name: semantica-backend
    restart: unless-stopped
    # ... rest of configuration

  frontend:
    image: yourusername/semantica-frontend:latest
    # Remove build section
    container_name: semantica-frontend
    restart: unless-stopped
    # ... rest of configuration
```

Then deploy:
```bash
docker-compose up -d
```

## Running with Docker Hub Images

To run the application using the images from Docker Hub:

1. Create a new `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    image: yourusername/semantica-backend:latest
    container_name: semantica-backend
    restart: unless-stopped
    networks:
      - semantica-network
    volumes:
      - backend-data:/app/app/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: yourusername/semantica-frontend:latest
    container_name: semantica-frontend
    restart: unless-stopped
    networks:
      - semantica-network
    environment:
      - NUXT_PUBLIC_API_BASE_URL=http://backend:8000/api/v1
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    container_name: semantica-nginx
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - semantica-network
    depends_on:
      - frontend
      - backend

networks:
  semantica-network:
    driver: bridge

volumes:
  backend-data:
```

2. Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Variables

### Frontend

- `NUXT_PUBLIC_API_BASE_URL`: The base URL for the backend API (default: `http://backend:8000/api/v1`)

### Backend

The backend uses SQLite for data storage, which is persisted in a Docker volume at `/app/app/storage`.

## Troubleshooting

### Backend healthcheck failing

Ensure curl is installed in the backend container. The Dockerfile includes curl installation.

### Frontend cannot connect to backend

Check that:
1. Both services are on the same Docker network
2. The `NUXT_PUBLIC_API_BASE_URL` is set correctly
3. The backend service is healthy

### Port already in use

If port 80 is already in use, modify the nginx port mapping in docker-compose.yml:
```yaml
ports:
  - "8080:80"  # Use port 8080 instead
```

## Volume Management

The backend data is stored in a named volume `backend-data`. To backup the data:

```bash
docker run --rm -v semantica_backend-data:/data -v $(pwd):/backup alpine tar czf /backup/semantica-backup.tar.gz /data
```

To restore:

```bash
docker run --rm -v semantica_backend-data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/semantica-backup.tar.gz --strip 1"
```

## Security Considerations

- In production, use environment variables or secrets for sensitive configuration
- Consider using HTTPS with a proper SSL certificate
- Restrict CORS origins in the backend to your actual domain
- Use specific image tags instead of `latest` for production deployments
- Regularly update base images for security patches
