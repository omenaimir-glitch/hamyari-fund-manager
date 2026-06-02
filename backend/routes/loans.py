from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, date
from decimal import Decimal
from models import db, Loan, LoanPayment, Member

loans_bp = Blueprint('loans', __name__, url_prefix='/api/loans')

@loans_bp.route('', methods=['GET'])
@jwt_required()
def get_loans():
    """دریافت لیست وام‌ها"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        member_id = request.args.get('member_id', type=int)
        
        query = Loan.query
        if status:
            query = query.filter_by(status=status)
        if member_id:
            query = query.filter_by(member_id=member_id)
        
        pagination = query.paginate(page=page, per_page=per_page)
        loans = [loan.to_dict() for loan in pagination.items]
        
        return jsonify({
            'success': True,
            'data': loans,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@loans_bp.route('/<int:loan_id>', methods=['GET'])
@jwt_required()
def get_loan(loan_id):
    """دریافت اطلاعات یک وام"""
    try:
        loan = Loan.query.get(loan_id)
        if not loan:
            return jsonify({'success': False, 'error': 'وام یافت نشد'}), 404
        
        loan_data = loan.to_dict()
        loan_data['remaining_installments'] = loan.get_remaining_installments()
        loan_data['total_paid'] = loan.get_total_paid()
        
        return jsonify({
            'success': True,
            'data': loan_data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@loans_bp.route('', methods=['POST'])
@jwt_required()
def create_loan():
    """ایجاد وام جدید"""
    try:
        data = request.get_json()
        
        # بررسی فیلدهای الزامی
        required = ['member_id', 'amount', 'loan_date']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} الزامی است'}), 400
        
        # بررسی وجود عضو
        member = Member.query.get(data['member_id'])
        if not member:
            return jsonify({'success': False, 'error': 'عضو یافت نشد'}), 404
        
        if member.status != 'active':
            return jsonify({'success': False, 'error': 'عضو فعال نیست'}), 400
        
        loan_amount = Decimal(str(data['amount']))
        loan_date = datetime.strptime(data['loan_date'], '%Y-%m-%d').date()
        
        # محاسبه تاریخ شروع و پایان بازپرداخت
        start_repayment = loan_date + timedelta(days=30)  # شروع ماه بعد
        end_repayment = start_repayment + timedelta(days=24*30)  # 24 ماه
        
        # محاسبه پرداخت ماهانه (بدون سود)
        monthly_payment = loan_amount / 24
        
        loan = Loan(
            member_id=data['member_id'],
            amount=loan_amount,
            loan_date=loan_date,
            start_repayment=start_repayment,
            end_repayment=end_repayment,
            monthly_payment=monthly_payment,
            total_remaining=loan_amount,
            status='active',
            queue_position=data.get('queue_position', 1),
            approved_by=1  # این باید از JWT گرفته شود
        )
        
        db.session.add(loan)
        db.session.flush()
        
        # ایجاد 24 قسط
        for installment in range(1, 25):
            payment_date = start_repayment + timedelta(days=30*installment)
            payment = LoanPayment(
                loan_id=loan.id,
                installment_number=installment,
                amount=monthly_payment,
                status='pending'
            )
            db.session.add(payment)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'وام با موفقیت ایجاد شد',
            'data': loan.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@loans_bp.route('/<int:loan_id>/payments', methods=['GET'])
@jwt_required()
def get_loan_payments(loan_id):
    """دریافت قسط‌های یک وام"""
    try:
        loan = Loan.query.get(loan_id)
        if not loan:
            return jsonify({'success': False, 'error': 'وام یافت نشد'}), 404
        
        status = request.args.get('status')
        query = LoanPayment.query.filter_by(loan_id=loan_id)
        
        if status:
            query = query.filter_by(status=status)
        
        payments = [payment.to_dict() for payment in query.all()]
        
        return jsonify({
            'success': True,
            'data': payments
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@loans_bp.route('/payments/<int:payment_id>/record', methods=['POST'])
@jwt_required()
def record_payment(payment_id):
    """ثبت پرداخت قسط"""
    try:
        payment = LoanPayment.query.get(payment_id)
        if not payment:
            return jsonify({'success': False, 'error': 'قسط یافت نشد'}), 404
        
        if payment.status == 'paid':
            return jsonify({'success': False, 'error': 'این قسط قبلاً پرداخت شده است'}), 400
        
        data = request.get_json()
        
        payment.status = 'paid'
        payment.payment_date = datetime.strptime(data.get('payment_date', str(date.today())), '%Y-%m-%d').date()
        payment.payment_method = data.get('payment_method', 'cash')
        payment.notes = data.get('notes')
        
        # به‌روزرسانی وام
        loan = payment.loan
        paid_amount = Decimal(str(payment.amount))
        loan.total_remaining = loan.total_remaining - paid_amount
        
        if loan.total_remaining <= 0:
            loan.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'قسط با موفقیت ثبت شد',
            'data': payment.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@loans_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_loans_summary():
    """دریافت خلاصه وام‌ها"""
    try:
        total_active_loans = Loan.query.filter_by(status='active').count()
        total_completed = Loan.query.filter_by(status='completed').count()
        total_overdue = Loan.query.filter_by(status='overdue').count()
        
        total_amount = db.session.query(
            db.func.sum(Loan.amount)
        ).filter(Loan.status.in_(['active', 'overdue'])).scalar() or Decimal('0')
        
        total_remaining = db.session.query(
            db.func.sum(Loan.total_remaining)
        ).filter(Loan.status.in_(['active', 'overdue'])).scalar() or Decimal('0')
        
        return jsonify({
            'success': True,
            'data': {
                'active_loans': total_active_loans,
                'completed_loans': total_completed,
                'overdue_loans': total_overdue,
                'total_disbursed': float(total_amount),
                'total_remaining': float(total_remaining)
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
