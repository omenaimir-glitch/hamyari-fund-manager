from . import db
from datetime import datetime

class AnnualCharge(db.Model):
    __tablename__ = 'annual_charges'
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False, unique=True)
    charge_amount = db.Column(db.Numeric(12, 2), nullable=False)
    effective_from = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('managers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """تبدیل به دیکشنری"""
        return {
            'id': self.id,
            'year': self.year,
            'charge_amount': float(self.charge_amount),
            'effective_from': self.effective_from.isoformat(),
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<AnnualCharge {self.year}: {self.charge_amount}>'