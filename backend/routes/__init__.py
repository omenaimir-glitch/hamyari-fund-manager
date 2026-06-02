from flask import Blueprint

# ایمپورت بلوپرین‌ها
from .auth import auth_bp
from .members import members_bp
from .charges import charges_bp
from .loans import loans_bp
from .reports import reports_bp

def register_routes(app):
    """ثبت تمام روت‌ها"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(charges_bp)
    app.register_blueprint(loans_bp)
    app.register_blueprint(reports_bp)
