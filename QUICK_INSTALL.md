# ⚡ Супер Быстрая Установка (БЕЗ venv)

## 🚀 За 2 минуты

### Вариант 1: Автоматический (рекомендуется)

```bash
chmod +x start.sh
./start.sh
```

### Вариант 2: Вручную (3 команды)

```bash
# 1. Установить зависимости
pip3 install -r requirements.txt

# 2. Создать .env
cp .env.example .env
# Отредактировать .env и добавить Google OAuth credentials

# 3. Запустить
python3 init_db.py init
python3 app.py
```

## 🔑 Google OAuth Setup (ОБЯЗАТЕЛЬНО!)

1. Перейти: https://console.cloud.google.com/
2. Создать проект
3. APIs & Services → Credentials → Create OAuth 2.0 Client ID
4. Authorized redirect URIs: `http://localhost:5000/auth/google-callback`
5. Скопировать Client ID и Secret в .env

## 📝 Минимальный .env файл

```env
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=ваш-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=ваш-secret
```

Сгенерировать SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## ❓ Устранение проблем

### Ошибка: "No module named 'flask'"
```bash
pip3 install -r requirements.txt
```

### Ошибка: "AttributeError: Decimal"
Уже исправлено! Просто скачайте последнюю версию.

### Ошибка: "venv/bin/activate: No such file or directory"
Используйте `start.sh` вместо `run.sh` - он работает без venv

## 🎯 После установки

Откройте: http://localhost:5000

1. Войти через Google
2. Выбрать роль (Teacher/Student/Starosta)
3. Начать работу! 🎉

---

**Готово!** Всего 2 минуты на запуск! ⚡