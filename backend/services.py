"""Services برای منطق تجاری اپلیکیشن"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from models import (
    db, Member, MemberCharge, AnnualCharge, Loan, LoanPayment,
    LoanQueue, FundBalance, ActivityLog
)

class ChargeService:
    """سرویس مدیریت شارژ‌ها"""
    
    @staticmethod
    def create_annual_charges(year, charge_amount, effective_from=None):
        """
        ایجاد شارژ سالیانه و توزیع آن برای اعضا
        """
        if not effective_from:
            effective_from = date.today()
        
        # بررسی تکراری نبودن
        existing = AnnualCharge.query.filter_by(year=year).first()
        if existing:
            raise ValueError(f'شارژ سال {year} قبلاً تعریف شده است')
        
        # ایجاد شارژ سالیانه
        annual_charge = AnnualCharge(
            year=year,
            charge_amount=Decimal(str(charge_amount)),
            effective_from=effective_from
        )
        db.session.add(annual_charge)
        db.session.flush()
        
        # توزیع برای تمام اعضای فعال
        active_members = Member.query.filter_by(status='active').all()
        monthly_amount = Decimal(str(charge_amount)) / 12
        
        for member in active_members:
            for month in range(1, 13):
                # بررسی تکراری نبودن
                existing_charge = MemberCharge.query.filter_by(
                    member_id=member.id,
                    month=month,
                    year=year
                ).first()
                
                if not existing_charge:
                    member_charge = MemberCharge(
                        member_id=member.id,
                        month=month,
                        year=year,
                        amount=monthly_amount,
                        status='pending'
                    )
                    db.session.add(member_charge)
        
        db.session.commit()
        return annual_charge
    
    @staticmethod
    def record_charge_payment(member_id, month, year):
        """
        ثبت پرداخت شارژ
        """
        charge = MemberCharge.query.filter_by(
            member_id=member_id,
            month=month,
            year=year
        ).first()
        
        if not charge:
            raise ValueError('شارژ یافت نشد')
        
        if charge.status == 'paid':
            raise ValueError('این شارژ قبلاً پرداخت شده است')
        
        charge.status = 'paid'
        charge.payment_date = date.today()
        db.session.commit()
        
        return charge
    
    @staticmethod
    def get_member_balance(member_id):
        """
        محاسبه موجودی شارژ‌های پرداخت شده عضو
        """
        member = Member.query.get(member_id)
        if not member:
            raise ValueError('عضو یافت نشد')
        
        return member.get_total_balance()


class LoanService:
    """سرویس مدیریت وام‌ها"""
    
    @staticmethod
    def calculate_loan_amount(member_id):
        """
        محاسبه مبلغ وام بر اساس موجودی شارژ
        """
        member = Member.query.get(member_id)
        if not member:
            raise ValueError('عضو یافت نشد')
        
        # وام برابر موجودی شارژ‌های پرداخت شده
        balance = member.get_total_balance()
        return Decimal(str(balance))
    
    @staticmethod
    def create_loan(member_id, loan_amount, loan_date=None, queue_position=None):
        """
        ایجاد وام جدید
        """
        if not loan_date:
            loan_date = date.today()
        
        member = Member.query.get(member_id)
        if not member:
            raise ValueError('عضو یافت نشد')
        
        if member.status != 'active':
            raise ValueError('عضو فعال نیست')
        
        # بررسی اینکه عضو قبلاً وام فعال دارد
        active_loan = Loan.query.filter_by(
            member_id=member_id,
            status='active'
        ).first()
        if active_loan:
            raise ValueError('عضو قبلاً وام فعالی دارد')
        
        loan_amount = Decimal(str(loan_amount))
        
        # محاسبه تاریخ‌ها
        start_repayment = loan_date + timedelta(days=30)
        end_repayment = start_repayment + timedelta(days=24*30)
        monthly_payment = loan_amount / 24
        
        loan = Loan(
            member_id=member_id,
            amount=loan_amount,
            loan_date=loan_date,
            start_repayment=start_repayment,
            end_repayment=end_repayment,
            monthly_payment=monthly_payment,
            total_remaining=loan_amount,
            status='active',
            queue_position=queue_position or 1
        )
        
        db.session.add(loan)
        db.session.flush()
        
        # ایجاد 24 قسط
        for installment in range(1, 25):
            payment = LoanPayment(
                loan_id=loan.id,
                installment_number=installment,
                amount=monthly_payment,
                status='pending'
            )
            db.session.add(payment)
        
        db.session.commit()
        return loan
    
    @staticmethod
    def record_payment(payment_id, payment_date=None, payment_method='cash', notes=None):
        """
        ثبت پرداخت قسط
        """
        if not payment_date:
            payment_date = date.today()
        
        payment = LoanPayment.query.get(payment_id)
        if not payment:
            raise ValueError('قسط یافت نشد')
        
        if payment.status == 'paid':
            raise ValueError('این قسط قبلاً پرداخت شده است')
        
        payment.status = 'paid'
        payment.payment_date = payment_date
        payment.payment_method = payment_method
        payment.notes = notes
        
        # به‌روزرسانی وام
        loan = payment.loan
        loan.total_remaining = loan.total_remaining - Decimal(str(payment.amount))
        
        if loan.total_remaining <= 0:
            loan.status = 'completed'
        
        db.session.commit()
        return payment
    
    @staticmethod
    def get_next_queue_position():
        """
        دریافت آخرین موضع صف
        """
        last_queue = LoanQueue.query.order_by(
            LoanQueue.queue_position.desc()
        ).first()
        
        return (last_queue.queue_position + 1) if last_queue else 1
    
    @staticmethod
    def add_to_queue(member_id, requested_amount=None):
        """
        اضافه کردن عضو به صف انتظار وام
        """
        member = Member.query.get(member_id)
        if not member:
            raise ValueError('عضو یافت نشد')
        
        # بررسی اینکه قبلاً در صف نباشد
        existing = LoanQueue.query.filter_by(member_id=member_id).first()
        if existing:
            raise ValueError('عضو قبلاً در صف انتظار است')
        
        queue_position = LoanService.get_next_queue_position()
        
        queue_entry = LoanQueue(
            member_id=member_id,
            requested_amount=Decimal(str(requested_amount)) if requested_amount else None,
            queue_position=queue_position,
            request_date=date.today(),
            status='waiting'
        )
        
        db.session.add(queue_entry)
        db.session.commit()
        
        return queue_entry


class FundService:
    """سرویس مدیریت صندوق"""
    
    @staticmethod
    def calculate_fund_balance(balance_date=None):
        """
        محاسبه موجودی صندوق
        """
        if not balance_date:
            balance_date = date.today()
        
        # کل شارژ‌های پرداخت شده
        total_paid_charges = db.session.query(
            db.func.sum(MemberCharge.amount)
        ).filter(MemberCharge.status == 'paid').scalar() or Decimal('0')
        
        # کل وام‌های فعال و معوقه
        total_active_loans = db.session.query(
            db.func.sum(Loan.total_remaining)
        ).filter(Loan.status.in_(['active', 'overdue'])).scalar() or Decimal('0')
        
        # موجودی در دسترس
        available_balance = total_paid_charges - total_active_loans
        
        balance = FundBalance(
            date=balance_date,
            total_balance=total_paid_charges,
            total_charges=total_paid_charges,
            total_active_loans=total_active_loans,
            available_balance=available_balance
        )
        
        # ذخیره یا به‌روزرسانی
        existing = FundBalance.query.filter_by(date=balance_date).first()
        if existing:
            existing.total_balance = total_paid_charges
            existing.total_charges = total_paid_charges
            existing.total_active_loans = total_active_loans
            existing.available_balance = available_balance
        else:
            db.session.add(balance)
        
        db.session.commit()
        return balance
    
    @staticmethod
    def get_fund_statistics():
        """
        دریافت آمار صندوق
        """
        total_members = Member.query.count()
        active_members = Member.query.filter_by(status='active').count()
        
        total_paid_charges = db.session.query(
            db.func.sum(MemberCharge.amount)
        ).filter(MemberCharge.status == 'paid').scalar() or Decimal('0')
        
        total_active_loans = db.session.query(
            db.func.sum(Loan.total_remaining)
        ).filter(Loan.status.in_(['active', 'overdue'])).scalar() or Decimal('0')
        
        available_balance = total_paid_charges - total_active_loans
        
        active_loans = Loan.query.filter_by(status='active').count()
        completed_loans = Loan.query.filter_by(status='completed').count()
        
        return {
            'members': {
                'total': total_members,
                'active': active_members
            },
            'charges': {
                'total': float(total_paid_charges)
            },
            'loans': {
                'active': active_loans,
                'completed': completed_loans,
                'total_disbursed': float(
                    db.session.query(
                        db.func.sum(Loan.amount)
                    ).filter(Loan.status.in_(['active', 'completed', 'overdue'])).scalar() or Decimal('0')
                ),
                'total_remaining': float(total_active_loans)
            },
            'fund': {
                'total_balance': float(total_paid_charges),
                'available_balance': float(available_balance)
            }
        }


class ActivityService:
    """سرویس ثبت فعالیت‌ها"""
    
    @staticmethod
    def log_activity(user_id, action_type, entity_type, entity_id, 
                    old_value=None, new_value=None, description=None):
        """
        ثبت فعا��یت
        """
        log = ActivityLog(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            description=description
        )
        db.session.add(log)
        db.session.commit()
        return log
