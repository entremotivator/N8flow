#!/bin/bash

# n8n Business Suite - Quick Start Script
# This script sets up and runs the n8n Business Suite

echo "🚀 Starting n8n Business Suite Setup..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed. Please install pip3."
    exit 1
fi

# Install requirements
echo "📦 Installing required packages..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install requirements. Please check your Python environment."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/forms
mkdir -p data/webhooks
mkdir -p data/models
mkdir -p data/settings

# Set permissions
chmod +x run.sh

echo "✅ Setup complete!"
echo ""
echo "🎯 Starting n8n Business Suite..."
echo "📱 The application will be available at: http://localhost:8501"
echo "🔗 Use this URL to access your business automation suite"
echo ""
echo "📋 Features available:"
echo "   • Form Builder with 15+ field types"
echo "   • Business Process Modeler"
echo "   • 50+ Ready-to-use Examples"
echo "   • Webhook Management & Testing"
echo "   • Comprehensive Settings"
echo "   • Chatbot Integration"
echo ""
echo "🛑 Press Ctrl+C to stop the application"
echo ""

# Run Streamlit
streamlit run main.py --server.port=8501 --server.address=0.0.0.0

