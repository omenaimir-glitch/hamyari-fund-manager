from . import db
from datetime import datetime

class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    national_id = db.Column(db.String(20), unique=True)
    join_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, inactive, blocked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    charges = db.relationship('MemberCharge', backref='member', lazy=True, cascade='all, delete-orphan')
    loans = db.relationship('Loan', backref='member', lazy=True, cascade='all, delete-orphan')
    loan_queue = db.relationship('LoanQueue', backref='member', uselist=False, cascade='all, delete-orphan')
    
    def get_total_balance(self):
        """محاسبه کل موجودی شارژ‌های پرداخت شده"""
        from .member_charge import MemberCharge
        paid_charges = db.session.query(
            db.func.sum(MemberCharge.amount)
        ).filter(
            MemberCharge.member_id == self.id,
            MemberCharge.status == 'paid'
        ).scalar() or 0
        return float(paid_charges)
    
    def get_total_paid_charges(self, year=None):
        """محاسبه شارژ‌های پرداخت شده در سال معین"""
        from .member_charge import MemberCharge
        query = db.session.query(
            db.func.sum(MemberCharge.amount)
        ).filter(
            MemberCharge.member_id == self.id,
            MemberCharge.status == 'paid'
        )
        if year:
            query = query.filter(MemberCharge.year == year)
        return float(query.scalar() or 0)
    
    def get_total_owed_charges(self):
        """محاسبه شارژ‌های معوقه"""
        from .member_charge import MemberCharge
        owed = db.session.query(
            db.func.sum(MemberCharge.amount)
        ).filter(
            MemberCharge.member_id == self.id,
            MemberCharge.status.in_(['pending', 'overdue'])
        ).scalar() or 0
        return float(owed)
    
    def get_total_loan_amount(self):
        """محاسبه کل وام‌های فعال"""
        from .loan import Loan
        total = db.session.query(
            db.func.sum(Loan.total_remaining)
        ).filter(
            Loan.member_id == self.id,
            Loan.status == 'active'
        ).scalar() or 0
        return float(total)
    
    def to_dict(self, include_balance=False):
        """تبدیل به دیکشنری"""
        data = {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'national_id': self.national_id,
            'join_date': self.join_date.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
        if include_balance:
            data['total_balance'] = self.get_total_balance()
            data['total_owed'] = self.get_total_owed_charges()
            data['active_loans'] = self.get_total_loan_amount()
        return data
    
    def __repr__(self):
        return f'<Member {self.name}>'