from flask import current_app, render_template_string
from flask_mail import Message
from app import mail
from threading import Thread


def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f'Failed to send email: {str(e)}')


def send_email(subject, recipients, text_body=None, html_body=None):
    """Send email notification"""
    msg = Message(
        subject=subject,
        recipients=recipients if isinstance(recipients, list) else [recipients],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    if text_body:
        msg.body = text_body
    if html_body:
        msg.html = html_body
    
    # Send asynchronously
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


def notify_new_lesson(lesson, recipients):
    """Notify students about a new lesson"""
    subject = f'New Lesson: {lesson.subject}'
    
    text_body = f"""
    A new lesson has been scheduled:
    
    Subject: {lesson.subject}
    Date: {lesson.date.strftime('%B %d, %Y')}
    Time: {lesson.start_time.strftime('%H:%M')} - {lesson.end_time.strftime('%H:%M')}
    Location: {lesson.location or 'TBA'}
    
    Description: {lesson.description or 'No description provided'}
    """
    
    html_body = f"""
    <h2>New Lesson Scheduled</h2>
    <p>A new lesson has been scheduled for your class:</p>
    <ul>
        <li><strong>Subject:</strong> {lesson.subject}</li>
        <li><strong>Date:</strong> {lesson.date.strftime('%B %d, %Y')}</li>
        <li><strong>Time:</strong> {lesson.start_time.strftime('%H:%M')} - {lesson.end_time.strftime('%H:%M')}</li>
        <li><strong>Location:</strong> {lesson.location or 'TBA'}</li>
    </ul>
    {f'<p><strong>Description:</strong> {lesson.description}</p>' if lesson.description else ''}
    """
    
    send_email(subject, recipients, text_body, html_body)


def notify_lesson_update(lesson, recipients):
    """Notify about lesson changes"""
    subject = f'Lesson Updated: {lesson.subject}'
    
    text_body = f"""
    A lesson has been updated:
    
    Subject: {lesson.subject}
    Date: {lesson.date.strftime('%B %d, %Y')}
    Time: {lesson.start_time.strftime('%H:%M')} - {lesson.end_time.strftime('%H:%M')}
    Location: {lesson.location or 'TBA'}
    """
    
    html_body = f"""
    <h2>Lesson Updated</h2>
    <p>A lesson has been updated:</p>
    <ul>
        <li><strong>Subject:</strong> {lesson.subject}</li>
        <li><strong>Date:</strong> {lesson.date.strftime('%B %d, %Y')}</li>
        <li><strong>Time:</strong> {lesson.start_time.strftime('%H:%M')} - {lesson.end_time.strftime('%H:%M')}</li>
        <li><strong>Location:</strong> {lesson.location or 'TBA'}</li>
    </ul>
    """
    
    send_email(subject, recipients, text_body, html_body)


def notify_new_collection(collection, recipients):
    """Notify about a new financial collection"""
    subject = f'New Payment Request: {collection.name}'
    
    text_body = f"""
    A new payment collection has been created:
    
    Collection: {collection.name}
    Amount: ${collection.amount_per_student}
    Due Date: {collection.due_date.strftime('%B %d, %Y') if collection.due_date else 'Not specified'}
    
    Description: {collection.description or 'No description provided'}
    
    Please make the payment as soon as possible.
    """
    
    html_body = f"""
    <h2>New Payment Request</h2>
    <p>A new payment collection has been created:</p>
    <ul>
        <li><strong>Collection:</strong> {collection.name}</li>
        <li><strong>Amount:</strong> ${collection.amount_per_student}</li>
        <li><strong>Due Date:</strong> {collection.due_date.strftime('%B %d, %Y') if collection.due_date else 'Not specified'}</li>
    </ul>
    {f'<p><strong>Description:</strong> {collection.description}</p>' if collection.description else ''}
    <p>Please make the payment as soon as possible.</p>
    """
    
    send_email(subject, recipients, text_body, html_body)


def notify_payment_reminder(collection, student):
    """Send payment reminder to student"""
    subject = f'Payment Reminder: {collection.name}'
    
    text_body = f"""
    This is a reminder that you have an outstanding payment:
    
    Collection: {collection.name}
    Amount: ${collection.amount_per_student}
    Due Date: {collection.due_date.strftime('%B %d, %Y') if collection.due_date else 'Not specified'}
    
    Please make the payment as soon as possible.
    """
    
    html_body = f"""
    <h2>Payment Reminder</h2>
    <p>This is a reminder that you have an outstanding payment:</p>
    <ul>
        <li><strong>Collection:</strong> {collection.name}</li>
        <li><strong>Amount:</strong> ${collection.amount_per_student}</li>
        <li><strong>Due Date:</strong> {collection.due_date.strftime('%B %d, %Y') if collection.due_date else 'Not specified'}</li>
    </ul>
    <p>Please make the payment as soon as possible.</p>
    """
    
    send_email(subject, student.email, text_body, html_body)


def notify_student_added(student, class_obj):
    """Notify student when added to a class"""
    subject = f'You have been added to {class_obj.name}'
    
    text_body = f"""
    Welcome to {class_obj.name}!
    
    You have been added to the class by {class_obj.teacher.full_name}.
    
    Academic Year: {class_obj.academic_year}
    
    You can now view your schedule, attendance, and other class information.
    """
    
    html_body = f"""
    <h2>Welcome to {class_obj.name}!</h2>
    <p>You have been added to the class by {class_obj.teacher.full_name}.</p>
    <p><strong>Academic Year:</strong> {class_obj.academic_year}</p>
    <p>You can now view your schedule, attendance, and other class information.</p>
    """
    
    send_email(subject, student.email, text_body, html_body)