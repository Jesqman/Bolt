from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from datetime import datetime, timedelta
from sqlalchemy import and_

from app import db
from models import User, Class, Lesson, Attendance
from utils.decorators import login_required, teacher_or_starosta_required
import io
import csv

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('/class/<int:class_id>')
@login_required
def class_attendance(class_id):
    """View attendance for a class"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to view this class.', 'danger')
            return redirect(url_for('dashboard.home'))
    elif current_user.class_id != class_id:
        flash('You do not have permission to view this class.', 'danger')
        return redirect(url_for('dashboard.home'))
    
    # Get lessons for the past 30 days
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    lessons = Lesson.query.filter(
        and_(
            Lesson.class_id == class_id,
            Lesson.date >= thirty_days_ago,
            Lesson.date <= today
        )
    ).order_by(Lesson.date.desc(), Lesson.start_time.desc()).all()
    
    students = class_obj.get_students()
    
    return render_template(
        'attendance/class.html',
        class_obj=class_obj,
        lessons=lessons,
        students=students
    )


@attendance_bp.route('/lesson/<int:lesson_id>')
@login_required
def lesson_attendance(lesson_id):
    """View/edit attendance for a specific lesson"""
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
    
    students = class_obj.get_students()
    
    # Get existing attendance records
    attendance_dict = {}
    for record in lesson.attendance_records:
        attendance_dict[record.student_id] = record
    
    return render_template(
        'attendance/lesson.html',
        lesson=lesson,
        class_obj=class_obj,
        students=students,
        attendance_dict=attendance_dict
    )


@attendance_bp.route('/lesson/<int:lesson_id>/mark', methods=['POST'])
@teacher_or_starosta_required
def mark_attendance(lesson_id):
    """Mark attendance for a lesson"""
    lesson = Lesson.query.get_or_404(lesson_id)
    class_obj = lesson.class_obj
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
    elif current_user.class_id != lesson.class_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    student_id = request.form.get('student_id')
    status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    if not student_id or not status:
        return jsonify({'error': 'Student ID and status are required'}), 400
    
    if status not in ['present', 'late', 'absent']:
        return jsonify({'error': 'Invalid status'}), 400
    
    # Check if attendance already exists
    attendance = Attendance.query.filter_by(
        student_id=student_id,
        lesson_id=lesson_id
    ).first()
    
    if attendance:
        # Update existing record
        attendance.status = status
        attendance.notes = notes
        attendance.marked_by = current_user.id
        attendance.marked_at = datetime.utcnow()
    else:
        # Create new record
        attendance = Attendance(
            student_id=student_id,
            lesson_id=lesson_id,
            status=status,
            notes=notes,
            marked_by=current_user.id
        )
        db.session.add(attendance)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Attendance marked successfully'})


@attendance_bp.route('/lesson/<int:lesson_id>/bulk-mark', methods=['POST'])
@teacher_or_starosta_required
def bulk_mark_attendance(lesson_id):
    """Mark attendance for multiple students at once"""
    lesson = Lesson.query.get_or_404(lesson_id)
    class_obj = lesson.class_obj
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to modify this lesson.', 'danger')
            return redirect(url_for('attendance.lesson_attendance', lesson_id=lesson_id))
    elif current_user.class_id != lesson.class_id:
        flash('You do not have permission to modify this lesson.', 'danger')
        return redirect(url_for('attendance.lesson_attendance', lesson_id=lesson_id))
    
    students = class_obj.get_students()
    
    for student in students:
        status = request.form.get(f'status_{student.id}')
        notes = request.form.get(f'notes_{student.id}', '')
        
        if status and status in ['present', 'late', 'absent']:
            # Check if attendance already exists
            attendance = Attendance.query.filter_by(
                student_id=student.id,
                lesson_id=lesson_id
            ).first()
            
            if attendance:
                attendance.status = status
                attendance.notes = notes
                attendance.marked_by = current_user.id
                attendance.marked_at = datetime.utcnow()
            else:
                attendance = Attendance(
                    student_id=student.id,
                    lesson_id=lesson_id,
                    status=status,
                    notes=notes,
                    marked_by=current_user.id
                )
                db.session.add(attendance)
    
    db.session.commit()
    flash('Attendance has been marked successfully!', 'success')
    return redirect(url_for('attendance.lesson_attendance', lesson_id=lesson_id))


@attendance_bp.route('/student/<int:student_id>')
@login_required
def student_attendance(student_id):
    """View attendance records for a specific student"""
    student = User.query.get_or_404(student_id)
    
    # Check permissions
    if current_user.is_teacher():
        if not student.class_obj or student.class_obj.teacher_id != current_user.id:
            flash('You do not have permission to view this student.', 'danger')
            return redirect(url_for('dashboard.home'))
    elif current_user.id != student_id and current_user.class_id != student.class_id:
        flash('You do not have permission to view this student.', 'danger')
        return redirect(url_for('dashboard.home'))
    
    # Get attendance records
    attendance_records = Attendance.query.filter_by(
        student_id=student_id
    ).order_by(Attendance.marked_at.desc()).all()
    
    # Calculate statistics
    total = len(attendance_records)
    present = len([a for a in attendance_records if a.status == 'present'])
    late = len([a for a in attendance_records if a.status == 'late'])
    absent = len([a for a in attendance_records if a.status == 'absent'])
    
    attendance_rate = (present / total * 100) if total > 0 else 0
    
    return render_template(
        'attendance/student.html',
        student=student,
        attendance_records=attendance_records,
        total=total,
        present=present,
        late=late,
        absent=absent,
        attendance_rate=attendance_rate
    )


@attendance_bp.route('/export/class/<int:class_id>')
@teacher_or_starosta_required
def export_class_attendance(class_id):
    """Export class attendance as CSV"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to export this data.', 'danger')
            return redirect(url_for('dashboard.home'))
    elif current_user.class_id != class_id:
        flash('You do not have permission to export this data.', 'danger')
        return redirect(url_for('dashboard.home'))
    
    from flask import Response
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Student Name', 'Date', 'Subject', 'Status', 'Notes', 'Marked By', 'Marked At'])
    
    # Get all lessons for the class
    lessons = Lesson.query.filter_by(class_id=class_id).order_by(Lesson.date.desc()).all()
    
    for lesson in lessons:
        for attendance in lesson.attendance_records:
            writer.writerow([
                attendance.student.full_name,
                lesson.date.isoformat(),
                lesson.subject,
                attendance.status,
                attendance.notes or '',
                attendance.marker.full_name if attendance.marker else '',
                attendance.marked_at.isoformat() if attendance.marked_at else ''
            ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=attendance_{class_obj.name}_{datetime.now().strftime("%Y%m%d")}.csv'}
    )