from . import db
from datetime import datetime

class FundBalance(db.Model):
    __tablename__ = 'fund_balance'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    total_balance = db.Column(db.Numeric(14, 2), nullable=False)
    total_charges = db.Column(db.Numeric(14, 2), nullable=False)
    total_active_loans = db.Column(db.Numeric(14, 2), nullable=False)
    available_balance = db.Column(db.Numeric(14, 2), nullable=False)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_date', 'date'),
    )
    
    def to_dict(self):
        """تبدیل به دیکشنری"""
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'total_balance': float(self.total_balance),
            'total_charges': float(self.total_charges),
            'total_active_loans': float(self.total_active_loans),
            'available_balance': float(self.available_balance),
            'calculated_at': self.calculated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<FundBalance {self.date}: {self.total_balance}>'