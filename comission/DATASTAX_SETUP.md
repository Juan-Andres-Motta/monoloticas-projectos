# DataStax Astra Streaming Integration Guide

## Overview

The commission service has been successfully updated to use **DataStax Astra Streaming** (managed Apache Pulsar) instead of local Pulsar. This provides a cloud-native, scalable messaging solution.

## 🔧 Configuration Changes

### 1. Pulsar Client Configuration

**Before (Local Pulsar):**
```python
client = pulsar.Client('pulsar://localhost:6650')
```

**After (DataStax Astra Streaming):**
```python
client = pulsar.Client(
    'pulsar+ssl://pulsar-aws-useast2.streaming.datastax.com:6651',
    authentication=pulsar.AuthenticationToken(token)
)
```

### 2. Topic Names

**Persistent Topics:**
- **Tracking Events**: `persistent://miso-1-2025/default/tracking-events`
- **Commissions**: `persistent://miso-1-2025/default/commissions`

### 3. Consumer Configuration

**Subscription**: `commission-service-subscription` (shared type for horizontal scaling)

## 🚀 Setup Instructions

### Step 1: Get DataStax Astra Streaming Token

1. Go to [DataStax Astra Console](https://console.astra.datastax.com/)
2. Navigate to your streaming tenant
3. Generate or copy your Pulsar token
4. It should look like: `eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...`

### Step 2: Configure Environment

```bash
# In commission service directory
cd /Users/juan/Desktop/uniandes/monoliticas/comission

# Copy environment template
cp .env.example .env

# Edit .env file with your token
# Replace YOUR_PULSAR_TOKEN with your actual token
```

**Example .env:**
```env
PULSAR_SERVICE_URL=pulsar+ssl://pulsar-aws-useast2.streaming.datastax.com:6651
PULSAR_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...your-actual-token
DATABASE_URL=postgresql://commission_user:commission_password@localhost:5433/commissiondb
```

### Step 3: Configure Tracking Service

```bash
# In tracking service directory  
cd /Users/juan/Desktop/uniandes/monoliticas/tracking

# Copy environment template
cp .env.example .env

# Edit .env file with same token
```

### Step 4: Start Services

```bash
# Start databases only (no local Pulsar needed)
cd /Users/juan/Desktop/uniandes/monoliticas/comission
docker-compose up -d

# Start tracking service
cd /Users/juan/Desktop/uniandes/monoliticas/tracking
python main.py  # Port 8000

# Start commission service (new terminal)
cd /Users/juan/Desktop/uniandes/monoliticas/comission  
python main.py  # Port 8001
```

## 🧪 Testing the Integration

### Automated Test
```bash
cd /Users/juan/Desktop/uniandes/monoliticas/comission
./test_integration.sh
```

### Manual Test
```bash
# 1. Create tracking event (triggers commission via Pulsar)
curl -X POST http://localhost:8000/api/v1/tracking/events \
  -H "Content-Type: application/json" \
  -d '{
    "partner_id": "partner_premium_1",
    "campaign_id": "campaign_123",
    "visitor_id": "visitor_456",
    "interaction_type": "click", 
    "source_url": "https://example.com",
    "destination_url": "https://destination.com"
  }'

# 2. Wait a few seconds for processing

# 3. Check generated commission
curl http://localhost:8001/api/v1/commissions/partner/partner_premium_1
```

## 📊 Expected Results

### Commission Calculation
- **Click**: $2.00 base × 10% rate = $0.20
- **Premium Partner Bonus**: $0.20 × 1.5 = **$0.30 total**
- **View**: $0.50 base × 5% rate = $0.025 
- **Engagement**: $5.00 base × 15% rate = $0.75

### Event Flow Logs
```
📡 Started Pulsar publisher for topic: persistent://miso-1-2025/default/tracking-events
📤 Published tracking event: abc123...
🎧 Started Pulsar consumer for topic: persistent://miso-1-2025/default/tracking-events  
📨 Received message 'tracking event data' id='message-123'
✅ Commission calculated with ID: def456...
💰 Commission notification for partner: partner_premium_1
```

## 🔍 Troubleshooting

### Common Issues

**1. Authentication Error**
```
❌ Failed to start Pulsar consumer: Authentication failed
```
**Solution**: Check your `PULSAR_TOKEN` in `.env` file

**2. Topic Not Found**
```
❌ Topic persistent://miso-1-2025/default/tracking-events not found
```
**Solution**: Create topics in DataStax Astra Console or they'll be auto-created on first message

**3. Connection Timeout**
```
❌ Failed to connect to Pulsar service
```
**Solution**: Check internet connection and service URL

### Debug Commands

```bash
# Check environment variables
env | grep PULSAR

# Test Pulsar connection (Python)
python -c "
import pulsar
from config.pulsar_config import PulsarConfig
client = pulsar.Client(**PulsarConfig.get_client_config())
print('✅ Connected successfully')
client.close()
"

# Check service logs
docker-compose logs -f
```

## 📈 Production Considerations

### Scaling
- **Consumer Scaling**: Multiple commission service instances share the same subscription
- **Producer Scaling**: Each tracking service instance can publish independently  
- **Message Ordering**: Not guaranteed across partitions (design accordingly)

### Security
- **Token Security**: Store tokens in secure environment variables
- **Network Security**: All traffic encrypted via SSL/TLS
- **Topic ACLs**: Configure proper access controls in DataStax console

### Monitoring
- **DataStax Console**: Monitor topics, subscriptions, and throughput
- **Application Logs**: Track message processing and errors
- **Health Checks**: Use service health endpoints

## 🎯 Key Benefits

✅ **Managed Service**: No Pulsar infrastructure to maintain  
✅ **Auto-scaling**: Handles traffic spikes automatically  
✅ **High Availability**: Built-in redundancy and failover  
✅ **Security**: Enterprise-grade security and compliance  
✅ **Monitoring**: Rich monitoring and alerting capabilities  
✅ **Global**: Available in multiple regions  

The commission service is now ready for production with cloud-native messaging! 🚀
