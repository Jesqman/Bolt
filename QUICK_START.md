# 🚀 Быстрый старт ClassHub (SQLite версия)

## Минимальная установка для разработки

### 1. Установить зависимости

```bash
# Создать виртуальное окружение
python3 -m venv venv

# Активировать
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установить пакеты
pip install -r requirements.txt
```

### 2. Настроить Google OAuth (обязательно!)

1. Перейти на https://console.cloud.google.com/
2. Создать новый проект
3. Перейти в "APIs & Services" → "Credentials"
4. Создать "OAuth 2.0 Client ID"
5. Тип приложения: "Web application"
6. Добавить Authorized redirect URIs:
   - `http://localhost:5000/auth/google-callback`
7. Скопировать Client ID и Client Secret

### 3. Создать .env файл

```bash
cp .env.example .env
nano .env  # или используйте любой редактор
```

**Минимальная конфигурация .env:**
```env
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=ваш-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=ваш-client-secret
```

**Сгенерировать SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Инициализировать базу данных

```bash
python init_db.py init
```

### 5. Запустить приложение

```bash
python app.py
```

Откройте браузер: http://localhost:5000

---

## 📝 Первый вход

1. Нажмите "Sign in with Google"
2. Выберите Google аккаунт
3. Выберите роль:
   - **Teacher** - если вы преподаватель
   - **Student** - если вы студент
   - **Starosta** - если вы староста
4. Готово! 🎉

---

## ⚡ Упрощенный старт БЕЗ email уведомлений

Если не хотите настраивать email (для тестирования):

**В .env оставьте только:**
```env
SECRET_KEY=ваш-секретный-ключ
GOOGLE_CLIENT_ID=ваш-client-id
GOOGLE_CLIENT_SECRET=ваш-client-secret
```

Email уведомления просто не будут отправляться, но все остальное будет работать!

---

## 🗄️ База данных

Приложение использует **SQLite** - файл `classhub.db` создается автоматически.

**Команды управления базой:**

```bash
# Инициализировать БД
python init_db.py init

# Посмотреть статистику
python init_db.py stats

# Сбросить БД (удалить все данные!)
python init_db.py reset
```

---

## 🔧 Устранение проблем

### Ошибка: "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Ошибка: "GOOGLE_CLIENT_ID is None"
Проверьте что `.env` файл создан и содержит правильные данные.

### Ошибка: "redirect_uri_mismatch"
В Google Console добавьте точный URL:
`http://localhost:5000/auth/google-callback`

### База данных заблокирована
```bash
python init_db.py reset
```

---

## 📚 Что дальше?

После входа:

**Для Teachers:**
1. Создайте класс
2. Добавьте студентов (они должны сначала зарегистрироваться)
3. Создайте расписание
4. Отмечайте посещаемость
5. Создавайте финансовые сборы

**Для Students:**
1. Смотрите расписание
2. Проверяйте посещаемость
3. Смотрите платежи

**Для Starosta:**
1. Добавляйте уроки
2. Отмечайте посещаемость
3. Управляйте сборами денег

---

## 🎯 Готовая команда для запуска

```bash
# Все в одной команде
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
python init_db.py init && \
python app.py
```

---

## 💡 Советы

1. **SQLite** подходит для разработки и тестирования
2. Для production лучше использовать **PostgreSQL** или **MySQL**
3. База данных хранится в файле `classhub.db`
4. Для переноса на production - см. `INSTALL.md`

---

## 📞 Помощь

- Документация: `README.md`
- Установка production: `INSTALL.md`
- Структура проекта: `PROJECT_SUMMARY.md`

**Удачного использования! 🎓**