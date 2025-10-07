#!/usr/bin/env python
"""Database initialization script"""
import os
import sys
from app import create_app, db
from models import User, Class, Lesson, Attendance, Finance, Collection


def init_database():
    """Initialize the database with tables"""
    print("🗄️  Инициализация базы данных...")
    
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("📝 Создание таблиц...")
        db.create_all()
        print("✓ Таблицы базы данных созданы успешно!")
        print("")
        print("База данных готова к использованию!")
        print("Запустите приложение: python app.py")


def reset_database():
    """Reset the database (drop and recreate all tables)"""
    confirm = input("⚠️  Это удалит ВСЕ данные. Вы уверены? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Отменено.")
        return
    
    print("🔄 Сброс базы данных...")
    
    app = create_app()
    
    with app.app_context():
        print("🗑️  Удаление всех таблиц...")
        db.drop_all()
        print("📝 Создание таблиц заново...")
        db.create_all()
        print("✓ База данных успешно сброшена!")


def show_stats():
    """Show database statistics"""
    app = create_app()
    
    with app.app_context():
        print("\n📊 === Статистика базы данных ===")
        print(f"👥 Пользователи: {User.query.count()}")
        print(f"   - Учителя: {User.query.filter_by(role='teacher').count()}")
        print(f"   - Старосты: {User.query.filter_by(role='starosta').count()}")
        print(f"   - Студенты: {User.query.filter_by(role='student').count()}")
        print(f"🎓 Классы: {Class.query.count()}")
        print(f"📚 Уроки: {Lesson.query.count()}")
        print(f"✅ Записи посещаемости: {Attendance.query.count()}")
        print(f"💰 Финансовые записи: {Finance.query.count()}")
        print(f"🗂️  Сборы: {Collection.query.count()}")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🗄️  Инструмент управления базой данных")
        print("\nИспользование:")
        print("  python init_db.py init      - Инициализировать базу данных")
        print("  python init_db.py reset     - Сбросить БД (ВНИМАНИЕ: удаляет все данные!)")
        print("  python init_db.py stats     - Показать статистику")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_database()
    elif command == 'reset':
        reset_database()
    elif command == 'stats':
        show_stats()
    else:
        print(f"Неизвестная команда: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()