from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token
from datetime import datetime, timedelta
from models import db, Manager
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """ثبت‌نام مدیر جدید"""
    try:
        data = request.get_json()
        
        # بررسی فیلدهای الزامی
        required = ['name', 'email', 'password']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} الزامی است'}), 400
        
        # بررسی تکراری نبودن ایمیل
        if Manager.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'error': 'این ایمیل قبلاً ثبت شده است'}), 400
        
        manager = Manager(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            role=data.get('role', 'moderator')
        )
        manager.set_password(data['password'])
        
        db.session.add(manager)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'ثبت‌نام با موفقیت انجام شد',
            'data': manager.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """ورود مدیر"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'error': 'ایمیل و رمز عبور الزامی هستند'}), 400
        
        manager = Manager.query.filter_by(email=data['email']).first()
        if not manager or not manager.check_password(data['password']):
            return jsonify({'success': False, 'error': 'ایمیل یا رمز عبور غلط است'}), 401
        
        access_token = create_access_token(identity=manager.id, expires_delta=timedelta(hours=24))
        refresh_token = create_refresh_token(identity=manager.id, expires_delta=timedelta(days=30))
        
        return jsonify({
            'success': True,
            'message': 'ورود با موفقیت انجام شد',
            'data': {
                'manager': manager.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """تازه‌سازی توکن دسترسی"""
    try:
        from flask_jwt_extended import get_jwt_identity
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity, expires_delta=timedelta(hours=24))
        
        return jsonify({
            'success': True,
            'access_token': access_token
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """دریافت اطلاعات مدیر فعلی"""
    try:
        from flask_jwt_extended import get_jwt_identity
        manager_id = get_jwt_identity()
        manager = Manager.query.get(manager_id)
        
        if not manager:
            return jsonify({'success': False, 'error': 'مدیر یافت نشد'}), 404
        
        return jsonify({
            'success': True,
            'data': manager.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
