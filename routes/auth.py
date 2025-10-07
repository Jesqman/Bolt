import json
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_user, logout_user, current_user
from authlib.integrations.flask_client import OAuth
from werkzeug.security import gen_salt
import requests

from app import db, login_manager
from models import User
from config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Initialize OAuth
oauth = OAuth()


def init_oauth(app):
    """Initialize OAuth with app configuration"""
    oauth.init_app(app)
    
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


@auth_bp.route('/login')
def login():
    """Display login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('auth/login.html')


@auth_bp.route('/google-login')
def google_login():
    """Redirect to Google OAuth login"""
    # Generate a random nonce for security
    nonce = gen_salt(16)
    session['nonce'] = nonce
    
    # Store the redirect URL if provided
    redirect_url = request.args.get('next') or url_for('dashboard.index')
    session['redirect_after_login'] = redirect_url
    
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)


@auth_bp.route('/google-callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Get OAuth token
        token = oauth.google.authorize_access_token()
        
        # Verify nonce
        nonce = session.pop('nonce', None)
        if not nonce:
            flash('Authentication failed. Please try again.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Parse user info from token
        user_info = token.get('userinfo')
        if not user_info:
            flash('Failed to get user information from Google.', 'danger')
            return redirect(url_for('auth.login'))
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        full_name = user_info.get('name')
        profile_picture = user_info.get('picture')
        
        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Check if user exists by email
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Update Google ID for existing user
                user.google_id = google_id
                user.profile_picture = profile_picture
            else:
                # New user - redirect to registration
                session['pending_user'] = {
                    'google_id': google_id,
                    'email': email,
                    'full_name': full_name,
                    'profile_picture': profile_picture
                }
                return redirect(url_for('auth.register'))
        
        # Update profile picture if changed
        if user and user.profile_picture != profile_picture:
            user.profile_picture = profile_picture
        
        db.session.commit()
        
        # Log in user
        login_user(user, remember=True)
        flash(f'Welcome back, {user.full_name}!', 'success')
        
        # Redirect to intended page or dashboard
        next_page = session.pop('redirect_after_login', url_for('dashboard.index'))
        return redirect(next_page)
        
    except Exception as e:
        flash(f'Authentication failed: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user after Google OAuth"""
    pending_user = session.get('pending_user')
    
    if not pending_user:
        flash('No pending registration found. Please log in with Google first.', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        # This would typically be used when a teacher invites students
        # For now, we'll create a basic registration
        role = request.form.get('role', 'student')
        
        # Validate role
        if role not in ['teacher', 'student', 'starosta']:
            flash('Invalid role selected.', 'danger')
            return render_template('auth/register.html', pending_user=pending_user)
        
        # Create new user
        user = User(
            google_id=pending_user['google_id'],
            email=pending_user['email'],
            full_name=pending_user['full_name'],
            profile_picture=pending_user.get('profile_picture'),
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Clear pending user from session
        session.pop('pending_user', None)
        
        # Log in user
        login_user(user, remember=True)
        flash(f'Welcome, {user.full_name}! Your account has been created.', 'success')
        
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/register.html', pending_user=pending_user)


@auth_bp.route('/logout')
def logout():
    """Log out current user"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))