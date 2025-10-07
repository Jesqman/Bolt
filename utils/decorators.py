from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def teacher_required(f):
    """Decorator to require teacher role"""
    return role_required('teacher')(f)


def starosta_required(f):
    """Decorator to require starosta role"""
    return role_required('starosta')(f)


def teacher_or_starosta_required(f):
    """Decorator to require teacher or starosta role"""
    return role_required('teacher', 'starosta')(f)


def student_required(f):
    """Decorator to require student role"""
    return role_required('student')(f)


def same_class_required(f):
    """Decorator to ensure user is in the same class"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Get class_id from kwargs or args
        class_id = kwargs.get('class_id') or (args[0] if args else None)
        
        if not class_id:
            abort(400, 'Class ID not provided')
        
        # Teachers can access their own classes
        if current_user.is_teacher():
            from models import Class
            class_obj = Class.query.get_or_404(class_id)
            if class_obj.teacher_id != current_user.id:
                flash('You do not have permission to access this class.', 'danger')
                abort(403)
        # Students and starostas must be in the class
        elif current_user.class_id != int(class_id):
            flash('You do not have permission to access this class.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function