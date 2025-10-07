#!/bin/bash
# ClassHub Startup Script

echo "🎓 ClassHub SaaS Platform"
echo "=========================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "Please copy .env.example to .env and configure it:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    exit 1
fi

# Check if database is initialized
echo "Checking database..."
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); from models import User; print('Database OK')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Database not initialized or connection failed!"
    echo "Please initialize the database:"
    echo "  python init_db.py init"
    echo ""
    exit 1
fi

echo ""
echo "✓ All checks passed!"
echo ""
echo "Starting ClassHub..."
echo "Visit http://localhost:5000 in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python app.py