from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import current_user
from datetime import datetime
import io
import csv

from app import db
from models import User, Class, Finance, Collection
from utils.decorators import login_required, teacher_or_starosta_required

finance_bp = Blueprint('finance', __name__, url_prefix='/finance')


@finance_bp.route('/class/<int:class_id>')
@login_required
def class_finance(class_id):
    """View financial collections for a class"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to view this class.', 'danger')
            return redirect(url_for('dashboard.home'))
    elif current_user.class_id != class_id:
        flash('You do not have permission to view this class.', 'danger')
        return redirect(url_for('dashboard.home'))
    
    # Get all collections
    collections = Collection.query.filter_by(
        class_id=class_id
    ).order_by(Collection.created_at.desc()).all()
    
    return render_template(
        'finance/class.html',
        class_obj=class_obj,
        collections=collections
    )


@finance_bp.route('/collection/create/<int:class_id>', methods=['GET', 'POST'])
@teacher_or_starosta_required
def create_collection(class_id):
    """Create a new collection"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to create collections for this class.', 'danger')
            return redirect(url_for('finance.class_finance', class_id=class_id))
    elif current_user.class_id != class_id:
        flash('You do not have permission to create collections for this class.', 'danger')
        return redirect(url_for('finance.class_finance', class_id=class_id))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        amount_per_student = request.form.get('amount_per_student')
        due_date_str = request.form.get('due_date')
        
        if not name or not amount_per_student:
            flash('Collection name and amount are required.', 'danger')
            return render_template('finance/create_collection.html', class_obj=class_obj)
        
        try:
            amount = float(amount_per_student)
            if amount <= 0:
                raise ValueError('Amount must be positive')
        except (ValueError, TypeError):
            flash('Invalid amount. Please enter a valid positive number.', 'danger')
            return render_template('finance/create_collection.html', class_obj=class_obj)
        
        # Parse due date
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format.', 'warning')
        
        # Create collection
        collection = Collection(
            class_id=class_id,
            name=name,
            description=description,
            amount_per_student=amount,
            due_date=due_date,
            created_by=current_user.id
        )
        
        db.session.add(collection)
        db.session.flush()  # Get collection ID
        
        # Create finance records for all students
        students = class_obj.get_students()
        for student in students:
            finance_record = Finance(
                class_id=class_id,
                collection_name=name,
                description=description,
                amount=amount,
                student_id=student.id,
                paid=False,
                created_by=current_user.id
            )
            db.session.add(finance_record)
        
        db.session.commit()
        
        flash(f'Collection "{name}" has been created successfully!', 'success')
        return redirect(url_for('finance.view_collection', collection_id=collection.id))
    
    return render_template('finance/create_collection.html', class_obj=class_obj)


@finance_bp.route('/collection/<int:collection_id>')
@login_required
def view_collection(collection_id):
    """View collection details and payment status"""
    collection = Collection.query.get_or_404(collection_id)
    class_obj = collection.class_obj
    
    # Check permissions
    if current_user.is_teacher():
        if class_obj.teacher_id != current_user.id:
            flash('You do not have permission to view this collection.', 'danger')
            return redirect(url_for('dashboard.home'))
    elif current_user.class_id != collection.class_id:
        flash('You do not have permission to view this collection.', 'danger')
        return redirect(url_for('dashboard.home'))
    
    # Get all finance records for this collection
    finance_records = Finance.query.filter_by(
        class_id=collection.class_id,
        collection_name=collection.name
    ).order_by(Finance.paid.desc(), Finance.student_id).all()
    
    payment_status = collection.get_payment_status()
    
    return render_template(
        'finance/collection.html',
        collection=collection,
        class_obj=class_obj,
        finance_records=finance_records,
        payment_status=payment_status
    )


@finance_bp.route('/collection/<int:collection_id>/mark-paid', methods=['POST'])
@teacher_or_starosta_required
def mark_paid(collection_id):
    """Mark a student as paid for a collection"""
    collection = Collection.query.get_or_404(collection_id)
    
    # Check permissions
    if current_user.is_teacher():
        if collection.class_obj.teacher_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
    elif current_user.class_id != collection.class_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    student_id = request.form.get('student_id')
    paid = request.form.get('paid') == 'true'
    notes = request.form.get('notes', '')
    
    if not student_id:
        return jsonify({'error': 'Student ID is required'}), 400
    
    # Find finance record
    finance_record = Finance.query.filter_by(
        collection_name=collection.name,
        class_id=collection.class_id,
        student_id=student_id
    ).first()
    
    if not finance_record:
        return jsonify({'error': 'Finance record not found'}), 404
    
    # Update payment status
    finance_record.paid = paid
    finance_record.payment_date = datetime.utcnow() if paid else None
    finance_record.notes = notes
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Payment status updated successfully'
    })


@finance_bp.route('/collection/<int:collection_id>/toggle-active', methods=['POST'])
@teacher_or_starosta_required
def toggle_collection_active(collection_id):
    """Toggle collection active status"""
    collection = Collection.query.get_or_404(collection_id)
    
    # Check permissions
    if current_user.is_teacher():
        if collection.class_obj.teacher_id != current_user.id:
            flash('Permission denied.', 'danger')
            return redirect(url_for('finance.class_finance', class_id=collection.class_id))
    elif current_user.class_id != collection.class_id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('finance.class_finance', class_id=collection.class_id))
    
    collection.is_active = not collection.is_active
    db.session.commit()
    
    status = 'activated' if collection.is_active else 'deactivated'
    flash(f'Collection has been {status}.', 'success')
    return redirect(url_for('finance.view_collection', collection_id=collection_id))


@finance_bp.route('/student/<int:student_id>')
@login_required
def student_finance(student_id):
    """View finance records for a specific student"""
    student = User.query.get_or_404(student_id)
    
    # Check permissions
    if current_user.is_teacher():
        if not student.class_obj or student.class_obj.teacher_id != current_user.id:
            flash('You do not have permission to view this student.', 'danger')
            return redirect(url_for('dashboard.home'))
    elif current_user.id != student_id and current_user.class_id != student.class_id:
        flash('You do not have permission to view this student.', 'danger')
        return redirect(url_for('dashboard.home'))
    
    # Get finance records
    finance_records = Finance.query.filter_by(
        student_id=student_id
    ).order_by(Finance.created_at.desc()).all()
    
    # Calculate statistics
    total_amount = sum(float(f.amount) for f in finance_records)
    paid_amount = sum(float(f.amount) for f in finance_records if f.paid)
    unpaid_amount = total_amount - paid_amount
    
    return render_template(
        'finance/student.html',
        student=student,
        finance_records=finance_records,
        total_amount=total_amount,
        paid_amount=paid_amount,
        unpaid_amount=unpaid_amount
    )


@finance_bp.route('/export/collection/<int:collection_id>')
@teacher_or_starosta_required
def export_collection(collection_id):
    """Export collection payment status as CSV"""
    collection = Collection.query.get_or_404(collection_id)
    
    # Check permissions
    if current_user.is_teacher():
        if collection.class_obj.teacher_id != current_user.id:
            flash('Permission denied.', 'danger')
            return redirect(url_for('finance.class_finance', class_id=collection.class_id))
    elif current_user.class_id != collection.class_id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('finance.class_finance', class_id=collection.class_id))
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Student Name', 'Amount', 'Paid', 'Payment Date', 'Notes'])
    
    # Get all finance records for this collection
    finance_records = Finance.query.filter_by(
        class_id=collection.class_id,
        collection_name=collection.name
    ).order_by(Finance.student_id).all()
    
    for record in finance_records:
        writer.writerow([
            record.student.full_name,
            float(record.amount),
            'Yes' if record.paid else 'No',
            record.payment_date.isoformat() if record.payment_date else '',
            record.notes or ''
        ])
    
    # Add summary
    writer.writerow([])
    payment_status = collection.get_payment_status()
    writer.writerow(['Summary'])
    writer.writerow(['Total Students', payment_status['total_students']])
    writer.writerow(['Paid', payment_status['paid']])
    writer.writerow(['Unpaid', payment_status['unpaid']])
    writer.writerow(['Total Collected', payment_status['total_collected']])
    writer.writerow(['Expected Total', payment_status['expected_total']])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=collection_{collection.name}_{datetime.now().strftime("%Y%m%d")}.csv'}
    )