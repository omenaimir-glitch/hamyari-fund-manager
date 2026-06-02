from . import db
from datetime import datetime

class LoanQueue(db.Model):
    __tablename__ = 'loan_queue'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False, unique=True)
    requested_amount = db.Column(db.Numeric(12, 2))
    queue_position = db.Column(db.Integer, nullable=False)
    request_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='waiting')  # waiting, approved, rejected, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('member_id', name='unique_member_queue'),
        db.Index('idx_position', 'queue_position'),
        db.Index('idx_status', 'status'),
    )
    
    def to_dict(self):
        """تبدیل به دیکشنری"""
        return {
            'id': self.id,
            'member_id': self.member_id,
            'requested_amount': float(self.requested_amount) if self.requested_amount else None,
            'queue_position': self.queue_position,
            'request_date': self.request_date.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<LoanQueue {self.member_id}: Position {self.queue_position}>'