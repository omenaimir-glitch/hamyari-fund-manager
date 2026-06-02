from . import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('managers.id'))
    action_type = db.Column(db.String(100), nullable=False)  # create, update, delete
    entity_type = db.Column(db.String(50), nullable=False)  # member, loan, charge
    entity_id = db.Column(db.Integer)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_user', 'user_id'),
        db.Index('idx_action', 'action_type'),
        db.Index('idx_date', 'created_at'),
    )
    
    def to_dict(self):
        """تبدیل به دیکشنری"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ActivityLog {self.action_type} {self.entity_type}>'