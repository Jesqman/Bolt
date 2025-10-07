#!/usr/bin/env python
"""Database initialization script"""
import os
import sys
from app import create_app, db
from models import User, Class, Lesson, Attendance, Finance, Collection


def init_database():
    """Initialize the database with tables"""
    print("Initializing database...")
    
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Optionally create a test teacher account
        create_test = input("\nCreate test teacher account? (y/n): ").lower()
        if create_test == 'y':
            email = input("Enter teacher email: ")
            full_name = input("Enter full name: ")
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                print(f"User with email {email} already exists!")
            else:
                test_teacher = User(
                    google_id=f"test_{email}",  # Placeholder - will be replaced on first Google login
                    email=email,
                    full_name=full_name,
                    role='teacher',
                    is_active=True
                )
                db.session.add(test_teacher)
                db.session.commit()
                print(f"✓ Test teacher account created for {email}")
                print("  Note: This user needs to log in with Google to activate the account.")


def reset_database():
    """Reset the database (drop and recreate all tables)"""
    confirm = input("⚠️  This will delete ALL data. Are you sure? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Aborted.")
        return
    
    print("Resetting database...")
    
    app = create_app()
    
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("✓ Database reset successfully!")


def show_stats():
    """Show database statistics"""
    app = create_app()
    
    with app.app_context():
        print("\n=== Database Statistics ===")
        print(f"Users: {User.query.count()}")
        print(f"  - Teachers: {User.query.filter_by(role='teacher').count()}")
        print(f"  - Starostas: {User.query.filter_by(role='starosta').count()}")
        print(f"  - Students: {User.query.filter_by(role='student').count()}")
        print(f"Classes: {Class.query.count()}")
        print(f"Lessons: {Lesson.query.count()}")
        print(f"Attendance Records: {Attendance.query.count()}")
        print(f"Finance Records: {Finance.query.count()}")
        print(f"Collections: {Collection.query.count()}")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Database Management Tool")
        print("\nUsage:")
        print("  python init_db.py init      - Initialize database")
        print("  python init_db.py reset     - Reset database (CAUTION: deletes all data)")
        print("  python init_db.py stats     - Show database statistics")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_database()
    elif command == 'reset':
        reset_database()
    elif command == 'stats':
        show_stats()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()