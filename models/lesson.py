from datetime import datetime
from app import db


class Lesson(db.Model):
    """Lesson model for managing class schedule"""
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100))  # e.g., "Room 204"
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    class_obj = db.relationship('Class', back_populates='lessons')
    creator = db.relationship('User', foreign_keys=[created_by])
    attendance_records = db.relationship('Attendance', back_populates='lesson', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Lesson {self.subject} on {self.date}>'
    
    def get_attendance_count(self):
        """Get attendance statistics for this lesson"""
        total = len(self.attendance_records)
        present = len([a for a in self.attendance_records if a.status == 'present'])
        late = len([a for a in self.attendance_records if a.status == 'late'])
        absent = len([a for a in self.attendance_records if a.status == 'absent'])
        
        return {
            'total': total,
            'present': present,
            'late': late,
            'absent': absent
        }
    
    def to_dict(self):
        """Convert lesson to dictionary"""
        return {
            'id': self.id,
            'subject': self.subject,
            'class_id': self.class_id,
            'class_name': self.class_obj.name if self.class_obj else None,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'description': self.description,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }