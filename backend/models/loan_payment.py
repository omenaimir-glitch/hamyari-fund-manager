from . import db
from datetime import datetime

class LoanPayment(db.Model):
    __tablename__ = 'loan_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    installment_number = db.Column(db.Integer, nullable=False)
    payment_date = db.Column(db.Date)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    payment_method = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('loan_id', 'installment_number', name='unique_loan_installment'),
        db.Index('idx_loan', 'loan_id'),
        db.Index('idx_status', 'status'),
        db.Index('idx_payments_date', 'payment_date'),
    )
    
    def to_dict(self):
        """تبدیل به دیکشنری"""
        return {
            'id': self.id,
            'loan_id': self.loan_id,
            'installment_number': self.installment_number,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'amount': float(self.amount),
            'status': self.status,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<LoanPayment {self.loan_id}-{self.installment_number}>'