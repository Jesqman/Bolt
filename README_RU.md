# ClassHub - SaaS Платформа для Учителей и Студентов

Веб-приложение для управления классами, расписанием, посещаемостью и финансами без зависимости от внешних систем.

## 🚀 Быстрый старт (5 минут)

### Шаг 1: Установка

```bash
# Скачать или клонировать проект
cd workspace

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```

### Шаг 2: Google OAuth (ОБЯЗАТЕЛЬНО!)

1. Перейдите на https://console.cloud.google.com/
2. Создайте проект
3. "APIs & Services" → "Credentials" → "Create OAuth 2.0 Client ID"
4. Добавьте redirect URI: `http://localhost:5000/auth/google-callback`
5. Скопируйте Client ID и Secret

### Шаг 3: Настройка

```bash
# Создать .env файл
cp .env.example .env

# Отредактировать .env
nano .env
```

**Минимум в .env:**
```env
SECRET_KEY=сгенерируйте-случайный-ключ
GOOGLE_CLIENT_ID=ваш-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=ваш-secret
```

Сгенерировать ключ:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Шаг 4: Запуск

```bash
# Инициализировать базу данных
python init_db.py init

# Запустить приложение
python app.py
```

Откройте http://localhost:5000

## ✨ Возможности

### 👨‍🏫 Для Учителей
- ✅ Создание и управление классами
- ✅ Управление списком студентов
- ✅ Назначение старосты
- ✅ Создание расписания занятий
- ✅ Отметка посещаемости
- ✅ Управление финансовыми сборами
- ✅ Экспорт отчетов в CSV
- ✅ Просмотр статистики

### ⭐ Для Старост
- ✅ Добавление уроков
- ✅ Отметка посещаемости
- ✅ Создание финансовых сборов
- ✅ Отслеживание платежей
- ✅ Управление списком студентов

### 🎓 Для Студентов
- ✅ Просмотр расписания
- ✅ Просмотр своей посещаемости
- ✅ Проверка статуса платежей
- ✅ Получение уведомлений

## 🗄️ База данных

Проект использует **SQLite** для разработки - легкая, быстрая, не требует настройки!

База данных создается автоматически в файле `classhub.db`.

### Команды управления:

```bash
# Инициализация
python init_db.py init

# Статистика
python init_db.py stats

# Сброс (удаляет ВСЕ данные!)
python init_db.py reset
```

## 📁 Структура проекта

```
workspace/
├── app.py                  # Главный файл приложения
├── config.py              # Настройки
├── requirements.txt       # Зависимости
├── init_db.py            # Скрипт для БД
├── run.sh                # Скрипт запуска
├── .env.example          # Пример настроек
├── models/               # Модели БД
├── routes/               # Маршруты
├── templates/            # HTML шаблоны
├── utils/                # Утилиты
└── classhub.db          # База данных SQLite
```

## 🔧 Технологии

- **Backend:** Flask 3.0
- **Database:** SQLite (для разработки)
- **Auth:** Google OAuth 2.0
- **UI:** Bootstrap 5
- **Email:** Flask-Mail (опционально)

## 📝 Первое использование

1. **Регистрация:**
   - Войдите через Google
   - Выберите роль (Teacher/Student/Starosta)

2. **Для учителя:**
   - Создайте класс
   - Добавьте студентов (они должны зарегистрироваться)
   - Назначьте старосту
   - Создайте расписание

3. **Для студентов:**
   - Учитель добавит вас в класс
   - Смотрите расписание и посещаемость

## ⚙️ Настройки

### Без Email уведомлений

Для тестирования можно не настраивать email:

**.env (минимум):**
```env
SECRET_KEY=ваш-ключ
GOOGLE_CLIENT_ID=ваш-id
GOOGLE_CLIENT_SECRET=ваш-secret
```

Email уведомления не будут работать, но все остальное - да!

### С Email уведомлениями

Добавьте в .env:
```env
MAIL_USERNAME=ваш-email@gmail.com
MAIL_PASSWORD=app-specific-password
```

Для Gmail:
1. Включите 2FA
2. Создайте App Password: https://myaccount.google.com/apppasswords

## 🚨 Решение проблем

### "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "GOOGLE_CLIENT_ID is None"
Проверьте .env файл - он должен существовать и содержать данные.

### "redirect_uri_mismatch"
В Google Console URI должен быть ТОЧНО:
`http://localhost:5000/auth/google-callback`

### Ошибка базы данных
```bash
python init_db.py reset
python init_db.py init
```

## 📚 Документация

- **QUICK_START.md** - Быстрый старт (5 минут)
- **README.md** - Полная документация (English)
- **INSTALL.md** - Production установка
- **PROJECT_SUMMARY.md** - Обзор проекта

## 🔄 Production

Для production рекомендуется:
- PostgreSQL или MySQL вместо SQLite
- Nginx + Gunicorn
- HTTPS (Let's Encrypt)

См. `INSTALL.md` для подробностей.

## 🎯 Основные команды

```bash
# Быстрый запуск
./run.sh

# Или вручную
python app.py

# Управление БД
python init_db.py init    # Создать
python init_db.py stats   # Статистика
python init_db.py reset   # Сбросить
```

## 💡 Советы

1. SQLite отлично подходит для разработки и малых классов (<100 студентов)
2. Для больших классов используйте PostgreSQL/MySQL
3. База данных в файле `classhub.db` - можно делать backup
4. Email уведомления опциональны
5. Все пароли хранятся в Google - максимальная безопасность!

## 📞 Поддержка

- GitHub Issues
- Email: support@classhub.com
- Документация в проекте

## 📄 Лицензия

MIT License

## 🎓 Использование

1. Учитель создает класс
2. Студенты регистрируются
3. Учитель добавляет студентов в класс
4. Учитель назначает старосту
5. Создается расписание
6. Отмечается посещаемость
7. Создаются финансовые сборы
8. Все работает! 🎉

---

**Приятного использования ClassHub!** 🚀