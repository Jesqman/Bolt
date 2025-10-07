from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

from app import db
from models import User, Class, Lesson, Attendance, Finance, Collection
from utils.decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    """Main landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    return redirect(url_for('auth.login'))


@dashboard_bp.route('/dashboard')
@login_required
def home():
    """Dashboard home - redirect based on role"""
    if current_user.is_teacher():
        return redirect(url_for('dashboard.teacher_dashboard'))
    elif current_user.is_starosta():
        return redirect(url_for('dashboard.starosta_dashboard'))
    else:
        return redirect(url_for('dashboard.student_dashboard'))


@dashboard_bp.route('/dashboard/teacher')
@login_required
def teacher_dashboard():
    """Teacher dashboard"""
    if not current_user.is_teacher():
        return redirect(url_for('dashboard.home'))
    
    # Get teacher's classes
    classes = Class.query.filter_by(teacher_id=current_user.id, is_active=True).all()
    
    # Get upcoming lessons (next 7 days)
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    upcoming_lessons = []
    for class_obj in classes:
        lessons = Lesson.query.filter(
            and_(
                Lesson.class_id == class_obj.id,
                Lesson.date >= today,
                Lesson.date <= next_week
            )
        ).order_by(Lesson.date, Lesson.start_time).all()
        upcoming_lessons.extend(lessons)
    
    # Sort by date and time
    upcoming_lessons.sort(key=lambda x: (x.date, x.start_time))
    
    # Get statistics
    total_students = sum(class_obj.get_student_count() for class_obj in classes)
    total_lessons = sum(len(class_obj.lessons) for class_obj in classes)
    
    return render_template(
        'dashboard/teacher.html',
        classes=classes,
        upcoming_lessons=upcoming_lessons[:5],  # Show next 5 lessons
        total_students=total_students,
        total_lessons=total_lessons
    )


@dashboard_bp.route('/dashboard/starosta')
@login_required
def starosta_dashboard():
    """Starosta dashboard"""
    if not current_user.is_starosta():
        return redirect(url_for('dashboard.home'))
    
    # Get starosta's class
    class_obj = current_user.class_obj
    
    if not class_obj:
        return render_template('dashboard/starosta.html', class_obj=None)
    
    # Get upcoming lessons
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    upcoming_lessons = Lesson.query.filter(
        and_(
            Lesson.class_id == class_obj.id,
            Lesson.date >= today,
            Lesson.date <= next_week
        )
    ).order_by(Lesson.date, Lesson.start_time).limit(5).all()
    
    # Get active collections
    collections = Collection.query.filter_by(
        class_id=class_obj.id,
        is_active=True
    ).order_by(Collection.created_at.desc()).all()
    
    # Get recent attendance
    recent_lessons = Lesson.query.filter_by(
        class_id=class_obj.id
    ).order_by(Lesson.date.desc(), Lesson.start_time.desc()).limit(5).all()
    
    return render_template(
        'dashboard/starosta.html',
        class_obj=class_obj,
        upcoming_lessons=upcoming_lessons,
        collections=collections,
        recent_lessons=recent_lessons
    )


@dashboard_bp.route('/dashboard/student')
@login_required
def student_dashboard():
    """Student dashboard"""
    if not current_user.is_student():
        return redirect(url_for('dashboard.home'))
    
    # Get student's class
    class_obj = current_user.class_obj
    
    if not class_obj:
        return render_template('dashboard/student.html', class_obj=None)
    
    # Get upcoming lessons
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    upcoming_lessons = Lesson.query.filter(
        and_(
            Lesson.class_id == class_obj.id,
            Lesson.date >= today,
            Lesson.date <= next_week
        )
    ).order_by(Lesson.date, Lesson.start_time).limit(5).all()
    
    # Get attendance statistics
    total_lessons = Lesson.query.filter(
        Lesson.class_id == class_obj.id,
        Lesson.date <= today
    ).count()
    
    attendance_records = Attendance.query.filter_by(
        student_id=current_user.id
    ).all()
    
    present_count = len([a for a in attendance_records if a.status == 'present'])
    late_count = len([a for a in attendance_records if a.status == 'late'])
    absent_count = len([a for a in attendance_records if a.status == 'absent'])
    
    # Get pending payments
    pending_payments = Finance.query.filter_by(
        student_id=current_user.id,
        paid=False
    ).all()
    
    return render_template(
        'dashboard/student.html',
        class_obj=class_obj,
        upcoming_lessons=upcoming_lessons,
        total_lessons=total_lessons,
        present_count=present_count,
        late_count=late_count,
        absent_count=absent_count,
        pending_payments=pending_payments
    )