-- Initialize database schema for AI Training exercises
-- This script runs automatically when the container is first created

-- Create schema for audit trails and logging
CREATE SCHEMA IF NOT EXISTS audit;

-- Audit trails table for tracking system events
CREATE TABLE IF NOT EXISTS audit.event_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    event_source VARCHAR(100) NOT NULL,
    event_data JSONB,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_event_logs_type ON audit.event_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_event_logs_created_at ON audit.event_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_event_logs_user_id ON audit.event_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_event_logs_session_id ON audit.event_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_event_logs_event_data ON audit.event_logs USING GIN(event_data);

-- Application logs table
CREATE TABLE IF NOT EXISTS audit.application_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    logger_name VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    exception_info TEXT,
    stack_trace TEXT,
    context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for log queries
CREATE INDEX IF NOT EXISTS idx_app_logs_level ON audit.application_logs(level);
CREATE INDEX IF NOT EXISTS idx_app_logs_created_at ON audit.application_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_app_logs_logger ON audit.application_logs(logger_name);

-- API request logs table
CREATE TABLE IF NOT EXISTS audit.api_requests (
    id SERIAL PRIMARY KEY,
    method VARCHAR(10) NOT NULL,
    endpoint VARCHAR(500) NOT NULL,
    status_code INTEGER,
    request_headers JSONB,
    request_body JSONB,
    response_body JSONB,
    response_time_ms INTEGER,
    user_id VARCHAR(255),
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for API request analysis
CREATE INDEX IF NOT EXISTS idx_api_requests_endpoint ON audit.api_requests(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_requests_status ON audit.api_requests(status_code);
CREATE INDEX IF NOT EXISTS idx_api_requests_created_at ON audit.api_requests(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_requests_user_id ON audit.api_requests(user_id);

-- Model predictions table for ML model tracking
CREATE TABLE IF NOT EXISTS audit.model_predictions (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    input_data JSONB NOT NULL,
    prediction JSONB NOT NULL,
    confidence_score FLOAT,
    processing_time_ms INTEGER,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Index for model tracking
CREATE INDEX IF NOT EXISTS idx_model_predictions_model ON audit.model_predictions(model_name, model_version);
CREATE INDEX IF NOT EXISTS idx_model_predictions_created_at ON audit.model_predictions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_model_predictions_user_id ON audit.model_predictions(user_id);

-- Create a function to clean old logs (retention policy)
CREATE OR REPLACE FUNCTION audit.clean_old_logs(retention_days INTEGER DEFAULT 90)
RETURNS TABLE(
    event_logs_deleted BIGINT,
    app_logs_deleted BIGINT,
    api_logs_deleted BIGINT,
    predictions_deleted BIGINT
) AS $$
DECLARE
    event_count BIGINT;
    app_count BIGINT;
    api_count BIGINT;
    pred_count BIGINT;
BEGIN
    -- Delete old event logs
    DELETE FROM audit.event_logs
    WHERE created_at < CURRENT_TIMESTAMP - (retention_days || ' days')::INTERVAL;
    GET DIAGNOSTICS event_count = ROW_COUNT;

    -- Delete old application logs
    DELETE FROM audit.application_logs
    WHERE created_at < CURRENT_TIMESTAMP - (retention_days || ' days')::INTERVAL;
    GET DIAGNOSTICS app_count = ROW_COUNT;

    -- Delete old API request logs
    DELETE FROM audit.api_requests
    WHERE created_at < CURRENT_TIMESTAMP - (retention_days || ' days')::INTERVAL;
    GET DIAGNOSTICS api_count = ROW_COUNT;

    -- Delete old model predictions
    DELETE FROM audit.model_predictions
    WHERE created_at < CURRENT_TIMESTAMP - (retention_days || ' days')::INTERVAL;
    GET DIAGNOSTICS pred_count = ROW_COUNT;

    RETURN QUERY SELECT event_count, app_count, api_count, pred_count;
END;
$$ LANGUAGE plpgsql;

-- Create sample data for testing
INSERT INTO audit.event_logs (event_type, event_source, event_data, user_id, ip_address) VALUES
    ('user.login', 'auth_service', '{"method": "oauth"}', 'user_123', '192.168.1.100'),
    ('model.inference', 'prediction_service', '{"model": "sentiment_analyzer", "latency_ms": 45}', 'user_123', '192.168.1.100'),
    ('data.upload', 'data_service', '{"file_type": "csv", "size_bytes": 1024000}', 'user_456', '192.168.1.101');

INSERT INTO audit.application_logs (level, logger_name, message, context) VALUES
    ('INFO', 'app.startup', 'Application started successfully', '{"version": "1.0.0", "environment": "development"}'),
    ('WARNING', 'app.database', 'Connection pool running low', '{"pool_size": 10, "active_connections": 9}'),
    ('ERROR', 'app.api', 'Failed to process request', '{"endpoint": "/api/predict", "error": "Timeout"}');

INSERT INTO audit.api_requests (method, endpoint, status_code, response_time_ms, user_id, ip_address) VALUES
    ('GET', '/api/health', 200, 5, NULL, '192.168.1.100'),
    ('POST', '/api/predict', 200, 125, 'user_123', '192.168.1.100'),
    ('POST', '/api/train', 500, 3000, 'user_456', '192.168.1.101');

INSERT INTO audit.model_predictions (model_name, model_version, input_data, prediction, confidence_score, processing_time_ms, user_id) VALUES
    ('sentiment_analyzer', 'v1.2.0', '{"text": "This is great!"}', '{"sentiment": "positive"}', 0.95, 45, 'user_123'),
    ('image_classifier', 'v2.0.0', '{"image_id": "img_001"}', '{"class": "cat", "bbox": [10, 20, 100, 150]}', 0.87, 230, 'user_456');

-- Grant permissions
GRANT USAGE ON SCHEMA audit TO PUBLIC;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA audit TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA audit TO PUBLIC;

-- Display initialization success message
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully!';
    RAISE NOTICE 'Schema: audit';
    RAISE NOTICE 'Tables created: event_logs, application_logs, api_requests, model_predictions';
    RAISE NOTICE 'Sample data inserted for testing';
END $$;
