from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from datetime import datetime

from app import db
from models import User, Class, Lesson
from utils.decorators import login_required, teacher_required, teacher_or_starosta_required

classes_bp = Blueprint('classes', __name__, url_prefix='/classes')


@classes_bp.route('/')
@login_required
def index():
    """List all classes (for teachers)"""
    if current_user.is_teacher():
        classes = Class.query.filter_by(
            teacher_id=current_user.id,
            is_active=True
        ).all()
    elif current_user.class_id:
        classes = [current_user.class_obj]
    else:
        classes = []
    
    return render_template('classes/index.html', classes=classes)


@classes_bp.route('/create', methods=['GET', 'POST'])
@teacher_required
def create():
    """Create a new class"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        academic_year = request.form.get('academic_year')
        
        if not name:
            flash('Class name is required.', 'danger')
            return render_template('classes/create.html')
        
        # Create class
        new_class = Class(
            name=name,
            description=description,
            academic_year=academic_year,
            teacher_id=current_user.id
        )
        
        db.session.add(new_class)
        db.session.commit()
        
        flash(f'Class "{name}" has been created successfully!', 'success')
        return redirect(url_for('classes.view', class_id=new_class.id))
    
    # Generate current academic year
    now = datetime.now()
    current_year = now.year
    next_year = current_year + 1
    academic_year = f"{current_year}-{next_year}"
    
    return render_template('classes/create.html', academic_year=academic_year)


@classes_bp.route('/<int:class_id>')
@login_required
def view(class_id):
    """View class details"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to view this class.', 'danger')
            return redirect(url_for('classes.index'))
    elif current_user.class_id != class_id:
        flash('You do not have permission to view this class.', 'danger')
        return redirect(url_for('classes.index'))
    
    students = class_obj.get_students()
    starosta = class_obj.get_starosta()
    
    # Get recent lessons
    recent_lessons = Lesson.query.filter_by(
        class_id=class_id
    ).order_by(Lesson.date.desc(), Lesson.start_time.desc()).limit(5).all()
    
    return render_template(
        'classes/view.html',
        class_obj=class_obj,
        students=students,
        starosta=starosta,
        recent_lessons=recent_lessons
    )


@classes_bp.route('/<int:class_id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit(class_id):
    """Edit class details"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check permissions
    if class_obj.teacher_id != current_user.id:
        flash('You do not have permission to edit this class.', 'danger')
        return redirect(url_for('classes.index'))
    
    if request.method == 'POST':
        class_obj.name = request.form.get('name')
        class_obj.description = request.form.get('description')
        class_obj.academic_year = request.form.get('academic_year')
        
        db.session.commit()
        
        flash('Class has been updated successfully!', 'success')
        return redirect(url_for('classes.view', class_id=class_id))
    
    return render_template('classes/edit.html', class_obj=class_obj)


@classes_bp.route('/<int:class_id>/students')
@login_required
def students(class_id):
    """View all students in a class"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to view this class.', 'danger')
            return redirect(url_for('classes.index'))
    elif current_user.class_id != class_id:
        flash('You do not have permission to view this class.', 'danger')
        return redirect(url_for('classes.index'))
    
    students = class_obj.get_students()
    starosta = class_obj.get_starosta()
    
    return render_template(
        'classes/students.html',
        class_obj=class_obj,
        students=students,
        starosta=starosta
    )


@classes_bp.route('/<int:class_id>/students/add', methods=['GET', 'POST'])
@teacher_or_starosta_required
def add_student(class_id):
    """Add student to class"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to modify this class.', 'danger')
            return redirect(url_for('classes.index'))
    elif current_user.class_id != class_id:
        flash('You do not have permission to modify this class.', 'danger')
        return redirect(url_for('classes.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Email is required.', 'danger')
            return render_template('classes/add_student.html', class_obj=class_obj)
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash(f'No user found with email {email}. They need to register first.', 'warning')
            return render_template('classes/add_student.html', class_obj=class_obj)
        
        # Check if already in a class
        if user.class_id:
            flash(f'{user.full_name} is already in a class.', 'warning')
            return render_template('classes/add_student.html', class_obj=class_obj)
        
        # Add to class
        user.class_id = class_id
        db.session.commit()
        
        flash(f'{user.full_name} has been added to the class!', 'success')
        return redirect(url_for('classes.students', class_id=class_id))
    
    return render_template('classes/add_student.html', class_obj=class_obj)


@classes_bp.route('/<int:class_id>/students/<int:student_id>/remove', methods=['POST'])
@teacher_required
def remove_student(class_id, student_id):
    """Remove student from class"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check permissions
    if class_obj.teacher_id != current_user.id:
        flash('You do not have permission to modify this class.', 'danger')
        return redirect(url_for('classes.index'))
    
    student = User.query.get_or_404(student_id)
    
    if student.class_id != class_id:
        flash('Student is not in this class.', 'danger')
        return redirect(url_for('classes.students', class_id=class_id))
    
    student.class_id = None
    db.session.commit()
    
    flash(f'{student.full_name} has been removed from the class.', 'success')
    return redirect(url_for('classes.students', class_id=class_id))


@classes_bp.route('/<int:class_id>/starosta/assign', methods=['POST'])
@teacher_required
def assign_starosta(class_id):
    """Assign starosta to class"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check permissions
    if class_obj.teacher_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    student_id = request.form.get('student_id')
    
    if not student_id:
        return jsonify({'error': 'Student ID is required'}), 400
    
    student = User.query.get_or_404(student_id)
    
    if student.class_id != class_id:
        return jsonify({'error': 'Student is not in this class'}), 400
    
    # Remove previous starosta
    old_starosta = class_obj.get_starosta()
    if old_starosta:
        old_starosta.role = 'student'
    
    # Assign new starosta
    student.role = 'starosta'
    db.session.commit()
    
    flash(f'{student.full_name} has been assigned as starosta!', 'success')
    return redirect(url_for('classes.students', class_id=class_id))