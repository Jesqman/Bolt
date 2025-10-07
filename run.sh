#!/bin/bash
# ClassHub Startup Script

echo "🎓 ClassHub SaaS Platform (SQLite Edition)"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "Creating minimal .env file..."
    echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" > .env
    echo "GOOGLE_CLIENT_ID=your-client-id-here" >> .env
    echo "GOOGLE_CLIENT_SECRET=your-client-secret-here" >> .env
    echo ""
    echo "✓ .env file created"
    echo "⚠️  ВАЖНО: Настройте Google OAuth в .env файле!"
    echo "  1. Получите credentials на https://console.cloud.google.com/"
    echo "  2. Отредактируйте .env и добавьте GOOGLE_CLIENT_ID и GOOGLE_CLIENT_SECRET"
    echo ""
fi

# Check if database exists
if [ ! -f "classhub.db" ]; then
    echo "🗄️  Database not found. Creating..."
    python init_db.py init
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create database"
        exit 1
    fi
fi

echo ""
echo "✓ All checks passed!"
echo ""
echo "🚀 Starting ClassHub..."
echo "📍 URL: http://localhost:5000"
echo "🗄️ Database: SQLite (classhub.db)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python app.py