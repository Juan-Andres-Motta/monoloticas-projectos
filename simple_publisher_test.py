#!/usr/bin/env python3
"""
Simple Publisher Test - Compatible with existing STRING schema topics
Tests publishing messages using StringSchema to match consumer expectations
"""

import json
import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any
from dotenv import load_dotenv
import pulsar
from pulsar import MessageId

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StringSchemaPublisher:
