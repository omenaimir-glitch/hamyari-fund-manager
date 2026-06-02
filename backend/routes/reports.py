from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, date
from decimal import Decimal
from models import db, FundBalance, MemberCharge, Loan, Member

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@reports_bp.route('/fund-balance', methods=['GET'])
@jwt_required()
def get_fund_balance():
    """دریافت موجودی صندوق"""
    try:
        balance_date = request.args.get('date')
        if balance_date:
            balance_date = datetime.strptime(balance_date, '%Y-%m-%d').date()
        else:
            balance_date = date.today()
        
        # محاسبه موجودی
        total_paid_charges = db.session.query(
            db.func.sum(MemberCharge.amount)
        ).filter(MemberCharge.status == 'paid').scalar() or Decimal('0')
        
        total_active_loans = db.session.query(
            db.func.sum(Loan.total_remaining)
        ).filter(Loan.status.in_(['active', 'overdue'])).scalar() or Decimal('0')
        
        available_balance = total_paid_charges - total_active_loans
        
        fund_balance = FundBalance(
            date=balance_date,
            total_balance=total_paid_charges,
            total_charges=total_paid_charges,
            total_active_loans=total_active_loans,
            available_balance=available_balance
        )
        
        return jsonify({
            'success': True,
            'data': fund_balance.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@reports_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_summary():
    """دریافت خلاصه داشبورد"""
    try:
        # تعداد اعضا
        total_members = Member.query.count()
        active_members = Member.query.filter_by(status='active').count()
        
        # شارژ‌ها
        total_paid_charges = db.session.query(
            db.func.sum(MemberCharge.amount)
        ).filter(MemberCharge.status == 'paid').scalar() or Decimal('0')
        
        pending_charges = db.session.query(
            db.func.sum(MemberCharge.amount)
        ).filter(MemberCharge.status == 'pending').scalar() or Decimal('0')
        
        overdue_charges = db.session.query(
            db.func.sum(MemberCharge.amount)
        ).filter(MemberCharge.status == 'overdue').scalar() or Decimal('0')
        
        # وام‌ها
        active_loans = Loan.query.filter_by(status='active').count()
        completed_loans = Loan.query.filter_by(status='completed').count()
        
        total_disbursed = db.session.query(
            db.func.sum(Loan.amount)
        ).filter(Loan.status.in_(['active', 'completed', 'overdue'])).scalar() or Decimal('0')
        
        total_remaining = db.session.query(
            db.func.sum(Loan.total_remaining)
        ).filter(Loan.status.in_(['active', 'overdue'])).scalar() or Decimal('0')
        
        # موجودی
        available_balance = total_paid_charges - total_remaining
        
        return jsonify({
            'success': True,
            'data': {
                'members': {
                    'total': total_members,
                    'active': active_members
                },
                'charges': {
                    'paid': float(total_paid_charges),
                    'pending': float(pending_charges),
                    'overdue': float(overdue_charges)
                },
                'loans': {
                    'active': active_loans,
                    'completed': completed_loans,
                    'total_disbursed': float(total_disbursed),
                    'total_remaining': float(total_remaining)
                },
                'fund': {
                    'total_balance': float(total_paid_charges),
                    'available_balance': float(available_balance)
                }
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@reports_bp.route('/members-balance', methods=['GET'])
@jwt_required()
def get_members_balance_report():
    """گزارش موجودی اعضا"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = Member.query.paginate(page=page, per_page=per_page)
        members_data = []
        
        for member in pagination.items:
            members_data.append({
                'id': member.id,
                'name': member.name,
                'national_id': member.national_id,
                'total_balance': member.get_total_balance(),
                'total_owed': member.get_total_owed_charges(),
                'active_loans': member.get_total_loan_amount(),
                'status': member.status
            })
        
        return jsonify({
            'success': True,
            'data': members_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@reports_bp.route('/payments-schedule', methods=['GET'])
@jwt_required()
def get_payments_schedule():
    """برنامه پرداخت قسط‌ها"""
    try:
        from models import LoanPayment
        
        status = request.args.get('status', 'pending')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = LoanPayment.query.filter_by(status=status).order_by(LoanPayment.id)
        pagination = query.paginate(page=page, per_page=per_page)
        
        payments_data = []
        for payment in pagination.items:
            loan = payment.loan
            member = loan.member
            payments_data.append({
                'payment_id': payment.id,
                'member_id': member.id,
                'member_name': member.name,
                'installment': payment.installment_number,
                'amount': float(payment.amount),
                'status': payment.status,
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else None
            })
        
        return jsonify({
            'success': True,
            'data': payments_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
