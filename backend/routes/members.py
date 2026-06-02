from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from decimal import Decimal
from models import db, Member, MemberCharge, AnnualCharge
from functools import wraps

members_bp = Blueprint('members', __name__, url_prefix='/api/members')

def manager_required(fn):
    """تزئین برای بررسی اینکه کاربر مدیر است"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

@members_bp.route('', methods=['GET'])
@jwt_required()
def get_members():
    """دریافت لیست تمام اعضا"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Member.query
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.paginate(page=page, per_page=per_page)
        members = [member.to_dict(include_balance=True) for member in pagination.items]
        
        return jsonify({
            'success': True,
            'data': members,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/<int:member_id>', methods=['GET'])
@jwt_required()
def get_member(member_id):
    """دریافت اطلاعات یک عضو"""
    try:
        member = Member.query.get(member_id)
        if not member:
            return jsonify({'success': False, 'error': 'عضو یافت نشد'}), 404
        
        return jsonify({
            'success': True,
            'data': member.to_dict(include_balance=True)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('', methods=['POST'])
@manager_required
def create_member():
    """ایجاد عضو جدید"""
    try:
        data = request.get_json()
        
        # بررسی فیلدهای الزامی
        required_fields = ['name', 'phone', 'national_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} الزامی است'}), 400
        
        # بررسی تکراری نبودن
        if Member.query.filter_by(national_id=data['national_id']).first():
            return jsonify({'success': False, 'error': 'این شناسه ملی قبلاً ثبت شده است'}), 400
        
        member = Member(
            name=data['name'],
            phone=data['phone'],
            email=data.get('email'),
            national_id=data['national_id'],
            join_date=datetime.strptime(data.get('join_date', str(date.today())), '%Y-%m-%d').date(),
            status=data.get('status', 'active')
        )
        
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'عضو با موفقیت ایجاد شد',
            'data': member.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/<int:member_id>', methods=['PUT'])
@manager_required
def update_member(member_id):
    """به‌روزرسانی اط��اعات عضو"""
    try:
        member = Member.query.get(member_id)
        if not member:
            return jsonify({'success': False, 'error': 'عضو یافت نشد'}), 404
        
        data = request.get_json()
        
        # به‌روزرسانی فیلدها
        if 'name' in data:
            member.name = data['name']
        if 'phone' in data:
            member.phone = data['phone']
        if 'email' in data:
            member.email = data['email']
        if 'status' in data:
            member.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'عضو با موفقیت به‌روزرسانی شد',
            'data': member.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/<int:member_id>/balance', methods=['GET'])
@jwt_required()
def get_member_balance(member_id):
    """دریافت موجودی و اطلاعات مالی عضو"""
    try:
        member = Member.query.get(member_id)
        if not member:
            return jsonify({'success': False, 'error': 'عضو یافت نشد'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'member_id': member_id,
                'name': member.name,
                'total_balance': member.get_total_balance(),
                'total_owed': member.get_total_owed_charges(),
                'active_loans': member.get_total_loan_amount()
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/<int:member_id>/charges', methods=['GET'])
@jwt_required()
def get_member_charges(member_id):
    """دریافت شارژ‌های عضو"""
    try:
        member = Member.query.get(member_id)
        if not member:
            return jsonify({'success': False, 'error': 'عضو یافت نشد'}), 404
        
        year = request.args.get('year', type=int)
        query = MemberCharge.query.filter_by(member_id=member_id)
        
        if year:
            query = query.filter_by(year=year)
        
        charges = [charge.to_dict() for charge in query.all()]
        
        return jsonify({
            'success': True,
            'data': charges
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/count', methods=['GET'])
@jwt_required()
def get_members_count():
    """دریافت تعداد اعضا"""
    try:
        total = Member.query.count()
        active = Member.query.filter_by(status='active').count()
        inactive = Member.query.filter_by(status='inactive').count()
        blocked = Member.query.filter_by(status='blocked').count()
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'active': active,
                'inactive': inactive,
                'blocked': blocked
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
