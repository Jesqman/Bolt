from datetime import datetime
from app import db


class Class(db.Model):
    """Class model for managing classes"""
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "7A"
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    academic_year = db.Column(db.String(20))  # e.g., "2024-2025"
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', back_populates='taught_classes', foreign_keys=[teacher_id])
    members = db.relationship('User', back_populates='class_obj', foreign_keys='User.class_id')
    lessons = db.relationship('Lesson', back_populates='class_obj', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Class {self.name}>'
    
    def get_students(self):
        """Get all students in the class"""
        return [member for member in self.members if member.role == 'student']
    
    def get_starosta(self):
        """Get the starosta of the class"""
        for member in self.members:
            if member.role == 'starosta':
                return member
        return None
    
    def get_student_count(self):
        """Get total number of students"""
        return len([m for m in self.members if m.role == 'student'])
    
    def to_dict(self):
        """Convert class to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.full_name if self.teacher else None,
            'academic_year': self.academic_year,
            'student_count': self.get_student_count(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }