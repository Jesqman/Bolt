from datetime import datetime
from app import db


class Attendance(db.Model):
    """Attendance model for tracking student presence"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    status = db.Column(db.Enum('present', 'late', 'absent'), nullable=False)
    notes = db.Column(db.Text)
    marked_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], back_populates='attendance_records')
    lesson = db.relationship('Lesson', back_populates='attendance_records')
    marker = db.relationship('User', foreign_keys=[marked_by])
    
    # Unique constraint: one attendance record per student per lesson
    __table_args__ = (
        db.UniqueConstraint('student_id', 'lesson_id', name='unique_student_lesson'),
    )
    
    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.lesson_id}: {self.status}>'
    
    def to_dict(self):
        """Convert attendance to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'lesson_id': self.lesson_id,
            'status': self.status,
            'notes': self.notes,
            'marked_by': self.marked_by,
            'marked_by_name': self.marker.full_name if self.marker else None,
            'marked_at': self.marked_at.isoformat() if self.marked_at else None
        }