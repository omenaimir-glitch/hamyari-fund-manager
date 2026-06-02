import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from models import db
from routes import register_routes
from datetime import datetime

# بارگذاری متغیرهای محیطی
load_dotenv()

def create_app(config_name='development'):
    """ایجاد و تنظیم اپلیکیشن Flask"""
    
    app = Flask(__name__)
    
    # تنظیم کانفیگ
    app.config.from_object(config[config_name])
    
    # تنظیم CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # تنظیم JWT
    jwt = JWTManager(app)
    
    # تنظیم پایگاه داده
    db.init_app(app)
    
    # ثبت مسیرها
    register_routes(app)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'صفحه یافت نشد'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'خطای سرور داخلی'
        }), 500
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'احراز هویت الزامی است'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'دسترسی غیرمجاز'
        }), 403
    
    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'success': True,
            'message': 'سرور فعال است',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(
        host=os.getenv('SERVER_HOST', '0.0.0.0'),
        port=int(os.getenv('SERVER_PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
