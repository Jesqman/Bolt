from datetime import datetime
from app import db


class Finance(db.Model):
    """Finance model for tracking collections and payments"""
    __tablename__ = 'finance'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    collection_name = db.Column(db.String(200), nullable=False)  # e.g., "Textbooks", "School Trip"
    description = db.Column(db.Text)
    amount = db.Column(db.Decimal(10, 2), nullable=False)  # Expected amount per student
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    paid = db.Column(db.Boolean, default=False)
    payment_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], back_populates='finance_records')
    creator = db.relationship('User', foreign_keys=[created_by])
    class_obj = db.relationship('Class', foreign_keys=[class_id])
    
    def __repr__(self):
        return f'<Finance {self.collection_name} - Student {self.student_id}: {"Paid" if self.paid else "Unpaid"}>'
    
    def to_dict(self):
        """Convert finance record to dictionary"""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'collection_name': self.collection_name,
            'description': self.description,
            'amount': float(self.amount) if self.amount else 0,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'paid': self.paid,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'notes': self.notes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Collection(db.Model):
    """Collection model for grouping finance records"""
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    amount_per_student = db.Column(db.Decimal(10, 2), nullable=False)
    due_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    class_obj = db.relationship('Class', foreign_keys=[class_id])
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<Collection {self.name}>'
    
    def get_total_collected(self):
        """Calculate total amount collected"""
        paid_records = Finance.query.filter_by(
            class_id=self.class_id,
            collection_name=self.name,
            paid=True
        ).all()
        return sum(float(record.amount) for record in paid_records)
    
    def get_payment_status(self):
        """Get payment status summary"""
        all_records = Finance.query.filter_by(
            class_id=self.class_id,
            collection_name=self.name
        ).all()
        
        total_students = len(all_records)
        paid_count = len([r for r in all_records if r.paid])
        unpaid_count = total_students - paid_count
        
        return {
            'total_students': total_students,
            'paid': paid_count,
            'unpaid': unpaid_count,
            'total_collected': self.get_total_collected(),
            'expected_total': float(self.amount_per_student) * total_students
        }
    
    def to_dict(self):
        """Convert collection to dictionary"""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'name': self.name,
            'description': self.description,
            'amount_per_student': float(self.amount_per_student),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'payment_status': self.get_payment_status()
        }