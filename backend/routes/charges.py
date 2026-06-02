from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, date, timedelta
from decimal import Decimal
from models import db, AnnualCharge, MemberCharge, Member

charges_bp = Blueprint('charges', __name__, url_prefix='/api/charges')

@charges_bp.route('/annual', methods=['GET'])
@jwt_required()
def get_annual_charges():
    """دریافت لیست شارژ‌های سالیانه"""
    try:
        charges = AnnualCharge.query.order_by(AnnualCharge.year.desc()).all()
        return jsonify({
            'success': True,
            'data': [charge.to_dict() for charge in charges]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@charges_bp.route('/annual', methods=['POST'])
@jwt_required()
def create_annual_charge():
    """ایجاد شارژ سالیانه جدید"""
    try:
        data = request.get_json()
        
        # بررسی فیلدهای الزامی
        if not data.get('year') or not data.get('charge_amount'):
            return jsonify({'success': False, 'error': 'سال و مبلغ الزامی هستند'}), 400
        
        # بررسی تکراری نبودن سال
        if AnnualCharge.query.filter_by(year=data['year']).first():
            return jsonify({'success': False, 'error': 'شارژ این سال قبلاً تعریف شده است'}), 400
        
        annual_charge = AnnualCharge(
            year=data['year'],
            charge_amount=Decimal(str(data['charge_amount'])),
            effective_from=datetime.strptime(data.get('effective_from', str(date.today())), '%Y-%m-%d').date(),
            created_by=1  # این باید از JWT گرفته شود
        )
        
        db.session.add(annual_charge)
        db.session.flush()
        
        # ایجاد شارژ‌های ماهانه برای تمام اعضا
        active_members = Member.query.filter_by(status='active').all()
        monthly_amount = Decimal(str(data['charge_amount'])) / 12
        
        for member in active_members:
            for month in range(1, 13):
                # بررسی تکراری نبودن
                existing = MemberCharge.query.filter_by(
                    member_id=member.id,
                    month=month,
                    year=data['year']
                ).first()
                
                if not existing:
                    member_charge = MemberCharge(
                        member_id=member.id,
                        month=month,
                        year=data['year'],
                        amount=monthly_amount,
                        status='pending'
                    )
                    db.session.add(member_charge)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'شارژ سالیانه {data["year"]} با موفقیت ایجاد و برای تمام اعضا توزیع شد',
            'data': annual_charge.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@charges_bp.route('/annual/<int:year>', methods=['PUT'])
@jwt_required()
def update_annual_charge(year):
    """به‌روزرسانی شارژ سالیانه"""
    try:
        annual_charge = AnnualCharge.query.filter_by(year=year).first()
        if not annual_charge:
            return jsonify({'success': False, 'error': 'شارژ این سال یافت نشد'}), 404
        
        data = request.get_json()
        
        old_amount = annual_charge.charge_amount
        annual_charge.charge_amount = Decimal(str(data.get('charge_amount', old_amount)))
        
        if 'effective_from' in data:
            annual_charge.effective_from = datetime.strptime(data['effective_from'], '%Y-%m-%d').date()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'شارژ سالیانه با موفقیت به‌روزرسانی شد',
            'data': annual_charge.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@charges_bp.route('/member/<int:member_id>', methods=['GET'])
@jwt_required()
def get_member_monthly_charges(member_id):
    """دریافت شارژ‌های ماهانه یک عضو"""
    try:
        member = Member.query.get(member_id)
        if not member:
            return jsonify({'success': False, 'error': 'عضو یافت نشد'}), 404
        
        year = request.args.get('year', type=int)
        status = request.args.get('status')
        
        query = MemberCharge.query.filter_by(member_id=member_id)
        
        if year:
            query = query.filter_by(year=year)
        if status:
            query = query.filter_by(status=status)
        
        charges = [charge.to_dict() for charge in query.all()]
        
        return jsonify({
            'success': True,
            'data': charges
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@charges_bp.route('/member/<int:member_id>/pay', methods=['POST'])
@jwt_required()
def pay_charge(member_id):
    """پرداخت شارژ ماهانه"""
    try:
        data = request.get_json()
        month = data.get('month')
        year = data.get('year')
        
        if not month or not year:
            return jsonify({'success': False, 'error': 'ماه و سال الزامی هستند'}), 400
        
        charge = MemberCharge.query.filter_by(
            member_id=member_id,
            month=month,
            year=year
        ).first()
        
        if not charge:
            return jsonify({'success': False, 'error': 'شارژ یافت نشد'}), 404
        
        if charge.status == 'paid':
            return jsonify({'success': False, 'error': 'این شارژ قبلاً پرداخت شده است'}), 400
        
        charge.status = 'paid'
        charge.payment_date = date.today()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'شارژ با موفقیت ثبت شد',
            'data': charge.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@charges_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_charges_summary():
    """دریافت خلاصه شارژ‌ها"""
    try:
        year = request.args.get('year', type=int)
        
        query = MemberCharge.query
        if year:
            query = query.filter_by(year=year)
        
        total_charges = db.session.query(db.func.sum(MemberCharge.amount)).filter(
            MemberCharge.status == 'paid'
        ).scalar() or Decimal('0')
        
        pending_charges = db.session.query(db.func.sum(MemberCharge.amount)).filter(
            MemberCharge.status.in_(['pending', 'overdue'])
        ).scalar() or Decimal('0')
        
        paid_count = MemberCharge.query.filter_by(status='paid').count()
        pending_count = MemberCharge.query.filter_by(status='pending').count()
        overdue_count = MemberCharge.query.filter_by(status='overdue').count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_paid': float(total_charges),
                'total_pending': float(pending_charges),
                'paid_count': paid_count,
                'pending_count': pending_count,
                'overdue_count': overdue_count
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
