# Qdrant Vector Database

This directory contains a Docker Compose configuration for running Qdrant, a high-performance vector database.

## Quick Start

### Start Qdrant

```bash
docker-compose up -d
```

### Stop Qdrant

```bash
docker-compose down
```

### Stop and Remove Data

```bash
docker-compose down -v
```

## Configuration

### Ports

- **6333**: HTTP API endpoint
- **6334**: gRPC API endpoint

### Volumes

- `qdrant_storage`: Persistent storage for vector data and indices

## Health Check

The service includes a health check that monitors the HTTP API endpoint every 30 seconds.

## Usage

### HTTP API

Access the Qdrant dashboard at: `http://localhost:6333/dashboard`

### Python Client Example

```python
from qdrant_client import QdrantClient

# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# Create a collection
client.create_collection(
    collection_name="my_collection",
    vectors_config={
        "size": 384,
        "distance": "Cosine"
    }
)
```

### cURL Example

```bash
# Check health
curl http://localhost:6333/health

# List collections
curl http://localhost:6333/collections
```

## Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Python Client](https://github.com/qdrant/qdrant-client)
- [REST API Reference](https://qdrant.github.io/qdrant/redoc/index.html)

## Troubleshooting

### Check logs

```bash
docker-compose logs -f qdrant
```

### Restart service

```bash
docker-compose restart qdrant
```

### Reset data

```bash
docker-compose down -v
docker-compose up -d
```
