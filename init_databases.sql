-- ===========================================
-- DATABASE INITIALIZATION SCRIPT
-- Creating basic tables for all microservices
-- ===========================================

-- ===========================================
-- CAMPAIGN DATABASE TABLES
-- ===========================================

-- Switch to campaign database
\c campaigndb;

-- Create campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    video_urls JSONB DEFAULT '[]',
    accepted_partners JSONB DEFAULT '{}'
);

-- Create campaign_events table for event store
CREATE TABLE IF NOT EXISTS campaign_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- Insert sample campaign data
INSERT INTO campaigns (id, name, description, status) VALUES 
    ('123e4567-e89b-12d3-a456-426614174001', 'Winter Sale Campaign', 'Promote winter clothing collection', 'active'),
    ('123e4567-e89b-12d3-a456-426614174002', 'Spring Collection', 'New spring fashion line', 'draft'),
    ('123e4567-e89b-12d3-a456-426614174003', 'Summer Accessories', 'Summer accessories promotion', 'active')
ON CONFLICT (id) DO NOTHING;

-- ===========================================
-- TRACKING DATABASE TABLES
-- ===========================================

-- Switch to tracking database
\c trackingdb;

-- Create tracking_events table
CREATE TABLE IF NOT EXISTS tracking_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id VARCHAR(255) NOT NULL,
    campaign_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    processed BOOLEAN DEFAULT FALSE
);

-- Create attribution_data table
CREATE TABLE IF NOT EXISTS attribution_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id VARCHAR(255) NOT NULL,
    campaign_id UUID NOT NULL,
    click_id VARCHAR(255),
    conversion_id VARCHAR(255),
    attribution_window_hours INTEGER DEFAULT 24,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample tracking data
INSERT INTO tracking_events (partner_id, campaign_id, event_type, event_data) VALUES 
    ('partner_fashion_blogger_001', '123e4567-e89b-12d3-a456-426614174001', 'click', '{"source": "instagram", "post_id": "ABC123"}'),
    ('partner_fashion_blogger_001', '123e4567-e89b-12d3-a456-426614174001', 'conversion', '{"order_id": "ORD-12345", "amount": 150.00}')
ON CONFLICT DO NOTHING;

-- ===========================================
-- COMMISSION DATABASE TABLES
-- ===========================================

-- Switch to commission database
\c commissiondb;

-- Create commissions table
CREATE TABLE IF NOT EXISTS commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id VARCHAR(255) NOT NULL,
    campaign_id UUID NOT NULL,
    tracking_event_id UUID,
    commission_type VARCHAR(50) NOT NULL,
    commission_rate DECIMAL(5,2) NOT NULL,
    base_amount DECIMAL(10,2),
    commission_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'pending',
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP
);

-- Create commission_calculations table for detailed breakdown
CREATE TABLE IF NOT EXISTS commission_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commission_id UUID REFERENCES commissions(id),
    calculation_details JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample commission data
INSERT INTO commissions (partner_id, campaign_id, commission_type, commission_rate, base_amount, commission_amount) VALUES 
    ('partner_fashion_blogger_001', '123e4567-e89b-12d3-a456-426614174001', 'CPA', 10.50, 150.00, 15.75),
    ('partner_fashion_blogger_001', '123e4567-e89b-12d3-a456-426614174002', 'CPL', 5.00, 0.00, 5.00)
ON CONFLICT DO NOTHING;

-- ===========================================
-- PAYMENT DATABASE TABLES
-- ===========================================

-- Switch to payment database
\c paymentdb;

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id VARCHAR(255) NOT NULL,
    payment_request_id UUID,
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) DEFAULT 'pending',
    account_info JSONB,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    invoice_details JSONB
);

-- Create payment_commissions table (many-to-many)
CREATE TABLE IF NOT EXISTS payment_commissions (
    payment_id UUID REFERENCES payments(id),
    commission_id UUID,
    commission_amount DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (payment_id, commission_id)
);

-- Insert sample payment data
INSERT INTO payments (partner_id, total_amount, payment_method, payment_status, account_info) VALUES 
    ('partner_fashion_blogger_001', 150.75, 'BANK_TRANSFER', 'completed', '{"account_type": "CHECKING", "last_four": "1234"}'),
    ('partner_tech_affiliate_002', 85.00, 'PAYPAL', 'pending', '{"email": "partner@example.com"}')
ON CONFLICT DO NOTHING;

-- ===========================================
-- CREATE INDEXES FOR PERFORMANCE
-- ===========================================

-- Campaign indexes
\c campaigndb;
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaign_events_aggregate_id ON campaign_events(aggregate_id);

-- Tracking indexes
\c trackingdb;
CREATE INDEX IF NOT EXISTS idx_tracking_events_partner_id ON tracking_events(partner_id);
CREATE INDEX IF NOT EXISTS idx_tracking_events_campaign_id ON tracking_events(campaign_id);
CREATE INDEX IF NOT EXISTS idx_tracking_events_timestamp ON tracking_events(timestamp);

-- Commission indexes
\c commissiondb;
CREATE INDEX IF NOT EXISTS idx_commissions_partner_id ON commissions(partner_id);
CREATE INDEX IF NOT EXISTS idx_commissions_campaign_id ON commissions(campaign_id);
CREATE INDEX IF NOT EXISTS idx_commissions_status ON commissions(status);

-- Payment indexes
\c paymentdb;
CREATE INDEX IF NOT EXISTS idx_payments_partner_id ON payments(partner_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(payment_status);

SELECT 'Database initialization completed!' as status;
