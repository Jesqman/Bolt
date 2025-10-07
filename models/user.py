from datetime import datetime
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """User model for teachers, students, and starostas"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('teacher', 'student', 'starosta'), nullable=False)
    profile_picture = db.Column(db.String(500))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    class_obj = db.relationship('Class', back_populates='members', foreign_keys=[class_id])
    taught_classes = db.relationship('Class', back_populates='teacher', foreign_keys='Class.teacher_id')
    attendance_records = db.relationship('Attendance', back_populates='student', cascade='all, delete-orphan')
    finance_records = db.relationship('Finance', back_populates='student', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
    
    def is_teacher(self):
        """Check if user is a teacher"""
        return self.role == 'teacher'
    
    def is_starosta(self):
        """Check if user is a starosta"""
        return self.role == 'starosta'
    
    def is_student(self):
        """Check if user is a student"""
        return self.role == 'student'
    
    def can_manage_class(self):
        """Check if user can manage class (teacher or starosta)"""
        return self.role in ['teacher', 'starosta']
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'class_id': self.class_id,
            'profile_picture': self.profile_picture,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }