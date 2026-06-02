from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Manager(db.Model):
    __tablename__ = 'managers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='moderator')  # admin, moderator
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    charges = db.relationship('AnnualCharge', backref='manager', lazy=True)
    activity_logs = db.relationship('ActivityLog', backref='manager', lazy=True)
    loans = db.relationship('Loan', backref='approver', lazy=True)
    
    def set_password(self, password):
        """تنظیم رمز عبور"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """تحقق از رمز عبور"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """تبدیل به دیکشنری"""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Manager {self.name}>'