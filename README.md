# ClassHub - SaaS Platform for Teachers and Students

A comprehensive web application that enables teachers and class leaders (starostas) to manage classes, schedules, attendance, and financial collections without relying on external systems.

## Features

### 🎓 For Teachers
- **Class Management**: Create and manage multiple classes
- **Student Management**: Add/remove students, assign class leaders (starostas)
- **Schedule Creation**: Create and edit lesson schedules
- **Attendance Tracking**: Mark and view student attendance with detailed statistics
- **Financial Management**: Track class collections and payments
- **Export Reports**: Export attendance and financial data to CSV/Excel
- **Dashboard**: Comprehensive overview of all classes and activities

### ⭐ For Starostas (Class Leaders)
- **Lesson Management**: Add lessons to the schedule
- **Attendance Marking**: Mark student attendance for lessons
- **Financial Collections**: Create and manage payment collections
- **Payment Tracking**: Track which students have paid
- **Student Overview**: View all students in the class
- **Dashboard**: Class-specific statistics and upcoming events

### 📚 For Students
- **Schedule Viewing**: See upcoming lessons and class schedule
- **Attendance Records**: View personal attendance history and statistics
- **Payment Status**: Track pending and completed payments
- **Notifications**: Receive updates about schedule changes and payment reminders
- **Dashboard**: Personalized view of class activities

## Technology Stack

### Backend
- **Framework**: Flask 3.0
- **Database**: MySQL/MariaDB with SQLAlchemy ORM
- **Authentication**: Google OAuth 2.0
- **Email**: Flask-Mail for notifications

### Frontend
- **Templates**: Jinja2
- **CSS Framework**: Bootstrap 5.3
- **Icons**: Bootstrap Icons
- **Responsive Design**: Mobile-friendly interface

### Security
- HTTPS support (Let's Encrypt)
- Role-based access control (RBAC)
- Session management
- Secure authentication with Google OAuth

## Installation

### Prerequisites
- Python 3.8+
- MySQL/MariaDB
- Google Cloud Platform account (for OAuth)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd workspace
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database
1. Create a MySQL database:
```sql
CREATE DATABASE saas_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Create a database user:
```sql
CREATE USER 'saas_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON saas_platform.* TO 'saas_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 5: Set Up Google OAuth 2.0
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" and create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:5000/auth/google-callback` (for development)
   - `https://yourdomain.com/auth/google-callback` (for production)
6. Copy the Client ID and Client Secret

### Step 6: Environment Configuration
1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and configure:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://saas_user:your_password@localhost/saas_platform
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Step 7: Initialize Database
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### Step 8: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### First Time Setup

1. **Register as Teacher**:
   - Visit `http://localhost:5000`
   - Click "Sign in with Google"
   - Complete registration and select "Teacher" role

2. **Create a Class**:
   - Go to Dashboard
   - Click "Create New Class"
   - Fill in class details (name, academic year)

3. **Add Students**:
   - Students must first register with Google
   - Go to your class → Students → Add Student
   - Enter student's email address

4. **Assign Starosta**:
   - Go to your class → Students
   - Click "Make Starosta" next to a student's name

5. **Create Schedule**:
   - Go to Schedule → Add Lesson
   - Fill in subject, date, time, and location

### Daily Operations

**For Teachers/Starostas**:
- Mark attendance after each lesson
- Create financial collections for trips, books, etc.
- Track payment status
- Export reports as needed

**For Students**:
- Check upcoming lessons
- View attendance records
- See pending payments

## Project Structure

```
workspace/
├── app.py                  # Application factory
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── models/               # Database models
│   ├── user.py          # User model
│   ├── class_model.py   # Class model
│   ├── lesson.py        # Lesson model
│   ├── attendance.py    # Attendance model
│   └── finance.py       # Finance models
├── routes/              # Application routes
│   ├── auth.py         # Authentication routes
│   ├── dashboard.py    # Dashboard routes
│   ├── classes.py      # Class management
│   ├── attendance.py   # Attendance tracking
│   ├── finance.py      # Financial management
│   └── schedule.py     # Schedule management
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── auth/           # Authentication templates
│   ├── dashboard/      # Dashboard templates
│   ├── classes/        # Class templates
│   ├── attendance/     # Attendance templates
│   ├── finance/        # Finance templates
│   └── schedule/       # Schedule templates
├── static/              # Static files
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript
│   └── images/         # Images
└── utils/               # Utility functions
    ├── decorators.py   # RBAC decorators
    └── notifications.py # Email notifications
```

## User Roles

### Teacher
- Full control over their classes
- Create/edit/delete classes, lessons, and schedules
- Manage students (add/remove, assign starosta)
- Mark attendance
- View all statistics and export reports

### Starosta (Class Leader)
- Almost same rights as teacher (within their class)
- Add lessons and mark attendance
- Create and manage financial collections
- Cannot remove teacher or delete class

### Student
- View schedule and lesson details
- See personal attendance records
- View pending payments
- Receive notifications

## API Endpoints

### Authentication
- `GET /auth/login` - Login page
- `GET /auth/google-login` - Initiate Google OAuth
- `GET /auth/google-callback` - OAuth callback
- `GET /auth/register` - Complete registration
- `GET /auth/logout` - Logout

### Dashboard
- `GET /dashboard` - Main dashboard (role-based redirect)
- `GET /dashboard/teacher` - Teacher dashboard
- `GET /dashboard/starosta` - Starosta dashboard
- `GET /dashboard/student` - Student dashboard

### Classes
- `GET /classes` - List classes
- `GET /classes/create` - Create class form
- `POST /classes/create` - Create class
- `GET /classes/<id>` - View class details
- `GET /classes/<id>/students` - View students
- `POST /classes/<id>/students/add` - Add student

### Attendance
- `GET /attendance/class/<id>` - Class attendance
- `GET /attendance/lesson/<id>` - Lesson attendance
- `POST /attendance/lesson/<id>/mark` - Mark attendance
- `GET /attendance/export/class/<id>` - Export attendance

### Finance
- `GET /finance/class/<id>` - Class collections
- `POST /finance/collection/create/<id>` - Create collection
- `GET /finance/collection/<id>` - View collection
- `POST /finance/collection/<id>/mark-paid` - Mark payment
- `GET /finance/export/collection/<id>` - Export payments

### Schedule
- `GET /schedule/class/<id>` - Class schedule
- `POST /schedule/lesson/create/<id>` - Create lesson
- `GET /schedule/lesson/<id>` - View lesson
- `POST /schedule/lesson/<id>/edit` - Edit lesson
- `POST /schedule/lesson/<id>/delete` - Delete lesson

## Production Deployment

### Prerequisites
- Ubuntu 20.04+ or similar Linux distribution
- Domain name with DNS configured
- SSL certificate (Let's Encrypt)

### Deployment Steps

1. **Install System Dependencies**:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx mysql-server
```

2. **Configure MySQL**:
```bash
sudo mysql_secure_installation
# Create database and user as shown above
```

3. **Clone and Setup Application**:
```bash
cd /var/www
sudo git clone <repository-url> classhub
cd classhub
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

4. **Configure Environment**:
```bash
sudo nano .env
# Add production configuration
```

5. **Create Systemd Service**:
```bash
sudo nano /etc/systemd/system/classhub.service
```

```ini
[Unit]
Description=ClassHub SaaS Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/classhub
Environment="PATH=/var/www/classhub/venv/bin"
ExecStart=/var/www/classhub/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

6. **Configure Nginx**:
```bash
sudo nano /etc/nginx/sites-available/classhub
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /var/www/classhub/static;
    }
}
```

7. **Enable and Start Services**:
```bash
sudo systemctl enable classhub
sudo systemctl start classhub
sudo systemctl enable nginx
sudo systemctl restart nginx
```

8. **Configure SSL with Let's Encrypt**:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Troubleshooting

### Database Connection Issues
- Check MySQL is running: `sudo systemctl status mysql`
- Verify credentials in `.env`
- Ensure database exists

### OAuth Errors
- Verify Google Client ID and Secret
- Check authorized redirect URIs in Google Console
- Ensure correct callback URL

### Email Not Sending
- Enable "Less secure app access" or use App Password for Gmail
- Check SMTP settings
- Verify firewall allows outbound SMTP

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create an issue on GitHub
- Email: support@classhub.com

## Roadmap

### Future Features
- [ ] Dedicated frontend (React/Vue)
- [ ] Mobile apps (iOS/Android)
- [ ] Integration with Zoom/Google Meet
- [ ] Automated parent reports
- [ ] Gamification (points, ratings)
- [ ] In-app chat
- [ ] Background tasks with Celery + Redis
- [ ] Multi-language support
- [ ] Advanced analytics and insights
- [ ] Grade management
- [ ] Homework assignments

## Credits

Developed with ❤️ for teachers and students worldwide.

## Version History

- **v1.0.0** (2025) - Initial release
  - Basic class management
  - Attendance tracking
  - Financial collections
  - Google OAuth authentication
  - Email notifications
  - Export functionality