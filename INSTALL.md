# Installation Guide - ClassHub SaaS Platform

This guide will walk you through setting up the ClassHub platform on your local machine or server.

## Quick Start (Development)

### 1. Install Prerequisites

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv mysql-server
```

**On macOS:**
```bash
brew install python mysql
```

**On Windows:**
- Install Python from [python.org](https://www.python.org/downloads/)
- Install MySQL from [mysql.com](https://dev.mysql.com/downloads/installer/)

### 2. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd workspace

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Database

**Create MySQL Database:**
```bash
# Login to MySQL
mysql -u root -p

# In MySQL console:
CREATE DATABASE saas_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'saas_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON saas_platform.* TO 'saas_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Set Up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Navigate to "APIs & Services" → "Credentials"
4. Click "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure consent screen if prompted
6. Set application type to "Web application"
7. Add authorized redirect URIs:
   - For development: `http://localhost:5000/auth/google-callback`
   - For production: `https://yourdomain.com/auth/google-callback`
8. Save and copy Client ID and Client Secret

### 5. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env
```

Update the following values in `.env`:
```env
SECRET_KEY=generate-a-random-secret-key-here
DATABASE_URL=mysql+pymysql://saas_user:your_password@localhost/saas_platform
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

**Generate Secret Key:**
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

**For Gmail:**
- Enable 2-factor authentication
- Create an [App Password](https://myaccount.google.com/apppasswords)
- Use the app password in `MAIL_PASSWORD`

### 6. Initialize Database

```bash
# Initialize database tables
python init_db.py init
```

### 7. Run the Application

```bash
# Development server
python app.py
```

Visit `http://localhost:5000` in your browser!

## Production Deployment

### Using Gunicorn + Nginx

**1. Install Gunicorn:**
```bash
pip install gunicorn
```

**2. Create Systemd Service:**

Create `/etc/systemd/system/classhub.service`:
```ini
[Unit]
Description=ClassHub SaaS Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/classhub
Environment="PATH=/var/www/classhub/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/var/www/classhub/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 "app:create_app()"

[Install]
WantedBy=multi-user.target
```

**3. Configure Nginx:**

Create `/etc/nginx/sites-available/classhub`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/classhub/static;
        expires 30d;
    }
}
```

**4. Enable and Start:**
```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/classhub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Start application
sudo systemctl enable classhub
sudo systemctl start classhub
```

**5. SSL with Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Using Docker (Optional)

**1. Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

**2. Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql+pymysql://saas_user:password@db/saas_platform
    depends_on:
      - db

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: saas_platform
      MYSQL_USER: saas_user
      MYSQL_PASSWORD: password
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

**3. Run:**
```bash
docker-compose up -d
```

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FLASK_ENV` | Environment (development/production) | No | development |
| `SECRET_KEY` | Flask secret key | Yes | - |
| `DATABASE_URL` | Database connection string | Yes | - |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | Yes | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | Yes | - |
| `MAIL_SERVER` | SMTP server | No | smtp.gmail.com |
| `MAIL_PORT` | SMTP port | No | 587 |
| `MAIL_USERNAME` | Email username | Yes | - |
| `MAIL_PASSWORD` | Email password | Yes | - |
| `MAIL_DEFAULT_SENDER` | Default sender email | No | noreply@classhub.com |

## Troubleshooting

### Database Connection Error
```
Error: Can't connect to MySQL server
```
**Solution:**
- Ensure MySQL is running: `sudo systemctl status mysql`
- Check credentials in `.env`
- Verify database exists: `SHOW DATABASES;`

### Google OAuth Error
```
Error 400: redirect_uri_mismatch
```
**Solution:**
- Add correct redirect URI in Google Console
- Ensure URI matches exactly (http vs https)
- Clear browser cache and try again

### Email Not Sending
```
SMTPAuthenticationError
```
**Solution:**
- Use App Password for Gmail (not regular password)
- Enable "Less secure app access" or use App Password
- Check SMTP settings in `.env`

### Permission Denied
```
PermissionError: [Errno 13] Permission denied
```
**Solution:**
```bash
sudo chown -R www-data:www-data /var/www/classhub
sudo chmod -R 755 /var/www/classhub
```

## Database Management

**View Statistics:**
```bash
python init_db.py stats
```

**Reset Database:**
```bash
python init_db.py reset
```

**Backup Database:**
```bash
mysqldump -u saas_user -p saas_platform > backup.sql
```

**Restore Database:**
```bash
mysql -u saas_user -p saas_platform < backup.sql
```

## Updating the Application

```bash
# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Apply database migrations (if any)
python init_db.py init

# Restart application
sudo systemctl restart classhub
```

## Support

For issues and questions:
- Check the [README.md](README.md) for documentation
- Open an issue on GitHub
- Contact: support@classhub.com

## Next Steps

After installation:
1. Log in with Google
2. Complete registration as Teacher
3. Create your first class
4. Add students
5. Start managing your class!

Enjoy using ClassHub! 🎓