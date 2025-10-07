from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from datetime import datetime, timedelta, time
from sqlalchemy import and_

from app import db
from models import Class, Lesson
from utils.decorators import login_required, teacher_or_starosta_required

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')


@schedule_bp.route('/class/<int:class_id>')
@login_required
def class_schedule(class_id):
    """View schedule for a class"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to view this schedule.', 'danger')
            return redirect(url_for('dashboard.home'))
    elif current_user.class_id != class_id:
        flash('You do not have permission to view this schedule.', 'danger')
        return redirect(url_for('dashboard.home'))
    
    # Get date range from query params or use current week
    week_offset = request.args.get('week', 0, type=int)
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)
    
    # Get lessons for the week
    lessons = Lesson.query.filter(
        and_(
            Lesson.class_id == class_id,
            Lesson.date >= start_of_week,
            Lesson.date <= end_of_week
        )
    ).order_by(Lesson.date, Lesson.start_time).all()
    
    # Organize lessons by day
    week_schedule = {}
    current_day = start_of_week
    for i in range(7):
        day = current_day + timedelta(days=i)
        week_schedule[day] = [l for l in lessons if l.date == day]
    
    return render_template(
        'schedule/class.html',
        class_obj=class_obj,
        week_schedule=week_schedule,
        start_of_week=start_of_week,
        end_of_week=end_of_week,
        week_offset=week_offset
    )


@schedule_bp.route('/lesson/create/<int:class_id>', methods=['GET', 'POST'])
@teacher_or_starosta_required
def create_lesson(class_id):
    """Create a new lesson"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to create lessons for this class.', 'danger')
            return redirect(url_for('schedule.class_schedule', class_id=class_id))
    elif current_user.class_id != class_id:
        flash('You do not have permission to create lessons for this class.', 'danger')
        return redirect(url_for('schedule.class_schedule', class_id=class_id))
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        date_str = request.form.get('date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        description = request.form.get('description')
        location = request.form.get('location')
        
        if not all([subject, date_str, start_time_str, end_time_str]):
            flash('All required fields must be filled.', 'danger')
            return render_template('schedule/create_lesson.html', class_obj=class_obj)
        
        try:
            lesson_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            
            if end_time <= start_time:
                flash('End time must be after start time.', 'danger')
                return render_template('schedule/create_lesson.html', class_obj=class_obj)
            
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return render_template('schedule/create_lesson.html', class_obj=class_obj)
        
        # Create lesson
        lesson = Lesson(
            subject=subject,
            class_id=class_id,
            date=lesson_date,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            created_by=current_user.id
        )
        
        db.session.add(lesson)
        db.session.commit()
        
        flash(f'Lesson "{subject}" has been created successfully!', 'success')
        return redirect(url_for('schedule.class_schedule', class_id=class_id))
    
    # Pre-fill with current date and default times
    default_date = datetime.now().date()
    default_start_time = '09:00'
    default_end_time = '10:00'
    
    return render_template(
        'schedule/create_lesson.html',
        class_obj=class_obj,
        default_date=default_date,
        default_start_time=default_start_time,
        default_end_time=default_end_time
    )


@schedule_bp.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    """View lesson details"""
    lesson = Lesson.query.get_or_404(lesson_id)
    class_obj = lesson.class_obj
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to view this lesson.', 'danger')
            return redirect(url_for('dashboard.home'))
    elif current_user.class_id != lesson.class_id:
        flash('You do not have permission to view this lesson.', 'danger')
        return redirect(url_for('dashboard.home'))
    
    attendance_stats = lesson.get_attendance_count()
    
    return render_template(
        'schedule/lesson.html',
        lesson=lesson,
        class_obj=class_obj,
        attendance_stats=attendance_stats
    )


@schedule_bp.route('/lesson/<int:lesson_id>/edit', methods=['GET', 'POST'])
@teacher_or_starosta_required
def edit_lesson(lesson_id):
    """Edit lesson details"""
    lesson = Lesson.query.get_or_404(lesson_id)
    class_obj = lesson.class_obj
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to edit this lesson.', 'danger')
            return redirect(url_for('schedule.view_lesson', lesson_id=lesson_id))
    elif current_user.class_id != lesson.class_id:
        flash('You do not have permission to edit this lesson.', 'danger')
        return redirect(url_for('schedule.view_lesson', lesson_id=lesson_id))
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        date_str = request.form.get('date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        description = request.form.get('description')
        location = request.form.get('location')
        
        if not all([subject, date_str, start_time_str, end_time_str]):
            flash('All required fields must be filled.', 'danger')
            return render_template('schedule/edit_lesson.html', lesson=lesson, class_obj=class_obj)
        
        try:
            lesson_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            
            if end_time <= start_time:
                flash('End time must be after start time.', 'danger')
                return render_template('schedule/edit_lesson.html', lesson=lesson, class_obj=class_obj)
            
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return render_template('schedule/edit_lesson.html', lesson=lesson, class_obj=class_obj)
        
        # Update lesson
        lesson.subject = subject
        lesson.date = lesson_date
        lesson.start_time = start_time
        lesson.end_time = end_time
        lesson.description = description
        lesson.location = location
        
        db.session.commit()
        
        flash('Lesson has been updated successfully!', 'success')
        return redirect(url_for('schedule.view_lesson', lesson_id=lesson_id))
    
    return render_template('schedule/edit_lesson.html', lesson=lesson, class_obj=class_obj)


@schedule_bp.route('/lesson/<int:lesson_id>/delete', methods=['POST'])
@teacher_or_starosta_required
def delete_lesson(lesson_id):
    """Delete a lesson"""
    lesson = Lesson.query.get_or_404(lesson_id)
    class_obj = lesson.class_obj
    class_id = lesson.class_id
    
    # Check permissions (only teachers can delete lessons)
    if not current_user.is_teacher() or class_obj.teacher_id != current_user.id:
        flash('You do not have permission to delete this lesson.', 'danger')
        return redirect(url_for('schedule.view_lesson', lesson_id=lesson_id))
    
    db.session.delete(lesson)
    db.session.commit()
    
    flash('Lesson has been deleted successfully.', 'success')
    return redirect(url_for('schedule.class_schedule', class_id=class_id))