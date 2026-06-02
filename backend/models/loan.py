from . import db
from datetime import datetime

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    loan_date = db.Column(db.Date, nullable=False)
    start_repayment = db.Column(db.Date, nullable=False)
    end_repayment = db.Column(db.Date, nullable=False)
    monthly_payment = db.Column(db.Numeric(12, 2), nullable=False)
    total_remaining = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, overdue, cancelled
    queue_position = db.Column(db.Integer)
    approved_by = db.Column(db.Integer, db.ForeignKey('managers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('LoanPayment', backref='loan', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_member', 'member_id'),
        db.Index('idx_status', 'status'),
        db.Index('idx_queue', 'queue_position'),
        db.Index('idx_loans_date', 'loan_date'),
    )
    
    def get_remaining_installments(self):
        """محاسبه تعداد اقساط باقی‌مانده"""
        from .loan_payment import LoanPayment
        paid_count = db.session.query(LoanPayment).filter(
            LoanPayment.loan_id == self.id,
            LoanPayment.status == 'paid'
        ).count()
        return 24 - paid_count
    
    def get_total_paid(self):
        """محاسبه کل پرداخت‌های انجام شده"""
        from .loan_payment import LoanPayment
        total = db.session.query(
            db.func.sum(LoanPayment.amount)
        ).filter(
            LoanPayment.loan_id == self.id,
            LoanPayment.status == 'paid'
        ).scalar() or 0
        return float(total)
    
    def to_dict(self):
        """تبدیل به دیکشنری"""
        return {
            'id': self.id,
            'member_id': self.member_id,
            'amount': float(self.amount),
            'loan_date': self.loan_date.isoformat(),
            'start_repayment': self.start_repayment.isoformat(),
            'end_repayment': self.end_repayment.isoformat(),
            'monthly_payment': float(self.monthly_payment),
            'total_remaining': float(self.total_remaining),
            'status': self.status,
            'queue_position': self.queue_position,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Loan {self.member_id}: {self.amount}>'