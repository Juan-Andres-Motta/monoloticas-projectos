#!/bin/bash

# 🚀 Quick Setup Guide for DataStax Astra Streaming

echo "🎯 DataStax Astra Streaming Quick Setup"
echo "========================================"
echo ""

# Step 1: Check environment
echo "1. Checking environment configuration..."
if [ -f .env ]; then
    echo "✅ .env file exists"
    if grep -q "YOUR_PULSAR_TOKEN" .env; then
        echo "❌ Please update PULSAR_TOKEN in .env file"
        echo "   Get your token from: https://console.astra.datastax.com/"
        echo ""
        exit 1
    else
        echo "✅ PULSAR_TOKEN appears to be set"
    fi
else
    echo "❌ .env file missing - creating from template..."
    cp .env.example .env
    echo "   Please edit .env and set your PULSAR_TOKEN"
    exit 1
fi

echo ""

# Step 2: Test minimal configuration
echo "2. Testing basic DataStax connection..."
echo "   This will test different topic configurations..."
python3 -c "
import os
import sys
sys.path.append('.')

try:
    from config.pulsar_config import PulsarConfig
    import pulsar
    
    print(f'   Service URL: {PulsarConfig.SERVICE_URL}')
    print(f'   Token length: {len(PulsarConfig.TOKEN)} chars')
    
    # Test basic client
    config = PulsarConfig.get_client_config()
    client = pulsar.Client(**config)
    print('   ✅ Client connection successful')
    
    # Try simple topic
    simple_topics = [
        'persistent://public/default/test',
        'non-persistent://public/default/test',
        'persistent://miso-1-2025/default/test'
    ]
    
    working_topic = None
    for topic in simple_topics:
        try:
            producer = client.create_producer(topic)
            print(f'   ✅ Topic works: {topic}')
            working_topic = topic
            producer.close()
            break
        except Exception as e:
            print(f'   ❌ Failed: {topic} - {str(e)[:50]}...')
    
    client.close()
    
    if working_topic:
        print(f'')
        print(f'🎉 Success! Working topic pattern found: {working_topic}')
        print(f'')
        print(f'💡 Update your .env file:')
        parts = working_topic.split('/')
        if len(parts) >= 4:
            tenant = parts[2]
            namespace = parts[3]
            print(f'   PULSAR_TENANT={tenant}')
            print(f'   PULSAR_NAMESPACE={namespace}')
        print(f'')
        print(f'Now run: ./start_services.sh')
    else:
        print(f'')
        print(f'❌ No working topic configuration found')
        print(f'')
        print(f'🔧 Please check:')
        print(f'   1. DataStax Console: https://console.astra.datastax.com/')
        print(f'   2. Verify tenant/namespace exists')
        print(f'   3. Check token permissions')
        print(f'   4. Create topics manually in console')
        sys.exit(1)
        
except ImportError as e:
    print(f'❌ Missing dependencies: {e}')
    print('   Run: pip install pulsar-client')
    sys.exit(1)
except Exception as e:
    print(f'❌ Connection failed: {e}')
    print('')
    print('🔧 Troubleshooting:')
    print('   1. Check PULSAR_TOKEN in .env file')
    print('   2. Verify DataStax Astra setup')
    print('   3. Check network connectivity')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Configuration test passed!"
    echo ""
    echo "Next steps:"
    echo "1. Start databases: docker-compose up -d"
    echo "2. Start tracking service: cd ../tracking && python main.py"
    echo "3. Start commission service: python main.py"
    echo "4. Test integration: ./test_integration.sh"
fi
