from . import db
from datetime import datetime

class MemberCharge(db.Model):
    __tablename__ = 'member_charges'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('member_id', 'month', 'year', name='unique_member_month'),
        db.Index('idx_member', 'member_id'),
        db.Index('idx_status', 'status'),
        db.Index('idx_charges_year_member', 'year', 'member_id'),
    )
    
    def to_dict(self):
        """تبدیل به دیکشنری"""
        return {
            'id': self.id,
            'member_id': self.member_id,
            'month': self.month,
            'year': self.year,
            'amount': float(self.amount),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<MemberCharge {self.member_id} {self.year}/{self.month}: {self.amount}>'