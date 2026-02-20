# PostgreSQL Database

This directory contains a Docker Compose configuration for running PostgreSQL 14 with a pre-configured schema for audit trails and logging.

## Quick Start

### Start PostgreSQL

```bash
docker-compose up -d
```

### Stop PostgreSQL

```bash
docker-compose down
```

### Stop and Remove Data

```bash
docker-compose down -v
```

## Configuration

### Default Credentials

- **Username**: `postgres`
- **Password**: `postgres`
- **Database**: `ai_training`
- **Port**: `5432`

### Environment Variables

You can override defaults by setting environment variables:

```bash
export POSTGRES_USER=myuser
export POSTGRES_PASSWORD=mypassword
export POSTGRES_DB=mydatabase
docker-compose up -d
```

Or create a `.env` file:

```env
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydatabase
```

## Database Schema

The `init.sql` script automatically creates the following schema on first startup:

### Schema: `audit`

#### Tables

1. **event_logs**: System event tracking
   - Event type, source, data (JSONB)
   - User and session tracking
   - IP address logging
   - Metadata support

2. **application_logs**: Application-level logging
   - Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Exception and stack trace storage
   - Contextual information (JSONB)

3. **api_requests**: API request/response logging
   - HTTP method, endpoint, status code
   - Request/response headers and bodies
   - Response time tracking
   - User and IP tracking

4. **model_predictions**: ML model inference tracking
   - Model name and version
   - Input data and predictions (JSONB)
   - Confidence scores
   - Processing time metrics

### Functions

- **clean_old_logs(retention_days)**: Cleanup function for log retention management

## Usage

### Connect with psql

```bash
docker exec -it postgres_db psql -U postgres -d ai_training
```

### Connect with Python

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="ai_training",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM audit.event_logs LIMIT 5;")
print(cursor.fetchall())
```

### Query Examples

```sql
-- View recent event logs
SELECT * FROM audit.event_logs ORDER BY created_at DESC LIMIT 10;

-- View API requests by endpoint
SELECT endpoint, COUNT(*), AVG(response_time_ms)
FROM audit.api_requests
GROUP BY endpoint;

-- View model prediction statistics
SELECT model_name, model_version,
       COUNT(*) as predictions,
       AVG(confidence_score) as avg_confidence,
       AVG(processing_time_ms) as avg_time_ms
FROM audit.model_predictions
GROUP BY model_name, model_version;

-- Clean logs older than 30 days
SELECT * FROM audit.clean_old_logs(30);
```

## Backup and Restore

### Backup Database

```bash
docker exec postgres_db pg_dump -U postgres ai_training > backup.sql
```

### Restore Database

```bash
docker exec -i postgres_db psql -U postgres ai_training < backup.sql
```

## Health Check

The service includes a health check that runs every 10 seconds to ensure the database is ready.

## Volumes

- `postgres_data`: Persistent storage for database data

## Troubleshooting

### Check logs

```bash
docker-compose logs -f postgres
```

### Restart service

```bash
docker-compose restart postgres
```

### Reset database

```bash
docker-compose down -v
docker-compose up -d
```

### Access psql shell

```bash
docker exec -it postgres_db psql -U postgres -d ai_training
```

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/14/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
- [SQLAlchemy PostgreSQL Dialect](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html)
