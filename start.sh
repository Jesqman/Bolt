#!/bin/bash
# Простой скрипт запуска без venv

echo "🎓 ClassHub SaaS Platform (SQLite Edition)"
echo "=========================================="
echo ""

# Проверка зависимостей
echo "🔍 Проверка зависимостей..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📥 Установка зависимостей..."
    pip3 install -r requirements.txt
    echo "✓ Зависимости установлены"
fi

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env файл не найден!"
    echo "Создаю минимальный .env файл..."
    echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > .env
    echo "GOOGLE_CLIENT_ID=your-client-id-here" >> .env
    echo "GOOGLE_CLIENT_SECRET=your-client-secret-here" >> .env
    echo ""
    echo "✓ .env файл создан"
    echo "⚠️  ВАЖНО: Настройте Google OAuth в .env файле!"
    echo "  1. Получите credentials на https://console.cloud.google.com/"
    echo "  2. Отредактируйте .env и добавьте GOOGLE_CLIENT_ID и GOOGLE_CLIENT_SECRET"
    echo ""
fi

# Проверка базы данных
if [ ! -f "classhub.db" ]; then
    echo "🗄️  База данных не найдена. Создаю..."
    python3 init_db.py init
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка создания базы данных"
        exit 1
    fi
fi

echo ""
echo "✓ Все проверки пройдены!"
echo ""
echo "🚀 Запуск ClassHub..."
echo "📍 URL: http://localhost:5000"
echo "🗄️ База данных: SQLite (classhub.db)"
echo ""
echo "Нажмите Ctrl+C для остановки"
echo ""

# Запуск приложения
python3 app.py