# برنامه مدیریت صندوق همیاری

## 📋 معرفی

سیستم جامع و حرفه‌ای برای مدیریت صندوق کوچک‌اندیشی با 50 عضو، شامل:
- مدیریت اعضا
- سیستم شارژ ماهانه (سالیانه قابل تغییر)
- مدیریت وام بدون سود
- بازپرداخت 24 ماهه خودکار
- سیستم نوبت‌دهی
- گزارش‌های جامع

---

## 🎯 ویژگی‌های اصلی

### 👥 مدیریت اعضا
- ثبت و مدیریت 50 عضو
- اطلاعات شخصی کامل (نام، شناسه ملی، تماس)
- وضعیت عضو (فعال، غیرفعال، مسدود)
- تاریخ پیوستن
- محاسبه موجودی و وام‌ها به صورت خودکار

### 💰 سیستم شارژ‌ها
- تنظیم شارژ سالیانه توسط مدیر
- تقسیم خودکار به 12 قسط ماهانه
- ثبت پرداخت‌ها
- ردیابی شارژ‌های معوقه
- گزارش موجودی

### 📊 سیستم وام‌ها
- وام برابر موجودی شارژ صندوق
- قابلیت تنظیم مبلغ توسط مدیر
- بازپرداخت 24 قسط برابر بدون سود
- صف انتظار خودکار
- ردیابی وام‌های فعال و تکمیل‌شده
- تنبیه خودکار برای وام‌های معوقه

### 📈 گزارش‌گری
- موجودی صندوق
- تاریخچه شارژ‌ها
- تاریخچه وام‌ها
- برنامه پرداخت قسط‌ها
- آمار اعضا
- دانلود گزارش‌های PDF

### 🔐 امنیت
- احراز هویت کاربر (JWT)
- مدیریت نقش‌ها (ادمین، مدیر)
- رمزگذاری رمز عبور
- ثبت تمام فعالیت‌ها
- کنترل دسترسی

---

## 🛠️ تکنولوژی‌های استفاده‌شده

### Backend
- **Python 3.8+**
- **Flask** - وب‌فریمورک
- **Flask-SQLAlchemy** - ORM
- **Flask-JWT-Extended** - احراز هویت JWT
- **MySQL** - پایگاه داده
- **PyMySQL** - درایور MySQL

### Frontend
- **HTML5**
- **CSS3** - با پشتیبانی Responsive Design
- **JavaScript (Vanilla)**
- **Persian Language Support (RTL)**

### Database
- **MySQL 8.0+**

---

## 📦 نصب و راه‌اندازی

### پیش‌نیازها
```bash
- Python 3.8+
- MySQL Server 8.0+
- pip (Package manager)
- Git
```

### مراحل نصب

#### 1. Clone Repository
```bash
git clone https://github.com/omenaimir-glitch/hamyari-fund-manager.git
cd hamyari-fund-manager
```

#### 2. نصب وابستگی‌های Backend
```bash
cd backend
pip install -r requirements.txt
```

#### 3. تنظیم پایگاه داده

**الف) ایجاد پایگاه داده**
```bash
mysql -u root -p
```

```sql
CREATE DATABASE hamyari_fund CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hamyari_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON hamyari_fund.* TO 'hamyari_user'@'localhost';
FLUSH PRIVILEGES;
```

**ب) اجرای Schema**
```bash
mysql -u hamyari_user -p hamyari_fund < ../database/schema.sql
```

#### 4. تنظیم فایل Environment
```bash
cp .env.example .env
```

فایل `.env` را ویرایش کنید:
```env
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

MYSQL_HOST=localhost
MYSQL_USER=hamyari_user
MYSQL_PASSWORD=your_password
MYSQL_DB=hamyari_fund
MYSQL_PORT=3306

SERVER_HOST=0.0.0.0
SERVER_PORT=5000
```

#### 5. اجرای Backend
```bash
python app.py
```

سرور روی `http://localhost:5000` اجرا می‌شود.

#### 6. اجرای Frontend

**گزینه 1: استفاده از Live Server (VSCode)**
- فایل `index.html` را در VSCode باز کنید
- روی "Go Live" کلیک کنید (در صورت نصب Live Server extension)

**گزینه 2: استفاده از Python SimpleHTTPServer**
```bash
cd ../frontend
python -m http.server 8000
```

**گزینه 3: استفاده از Node.js http-server**
```bash
npx http-server frontend/
```

---

## 🚀 استفاده

### ورود به سیستم
1. به `http://localhost:8000` (یا پورت مربوط) بروید
2. ایمیل و رمز عبور خود را وارد کنید
3. در صورت عدم داشتن حساب، ابتدا باید توسط مدیر سیستم ثبت شوید

### ایجاد حساب مدیر (Bootstrap)

**اولین بار:**

```python
from app import create_app, db
from models import Manager

app = create_app()
with app.app_context():
    # ایجاد مدیر اول
    manager = Manager(
        name='مدیر سیستم',
        email='admin@example.com',
        phone='09xxxxxxxxx',
        role='admin'
    )
    manager.set_password('password123')
    db.session.add(manager)
    db.session.commit()
    print('مدیر ایجاد شد')
```

### استفاده از داشبورد

#### 1. داشبورد
- مشاهده تعداد اعضا
- موجودی صندوق
- وام‌های فعال
- شارژ‌های معوقه

#### 2. مدیریت اعضا
- افزودن عضو جدید
- ویرایش اطلاعات
- مشاهده موجودی و وام‌ها
- تغییر وضعیت عضو

#### 3. مدیریت شارژ‌ها
- تنظیم شارژ سالیانه
- ثبت پرداخت‌های ماهانه
- مشاهده شارژ‌های معوقه
- تولید گزارش

#### 4. مدیریت وام‌ها
- ایجاد وام جدید
- مشاهده برنامه قسط‌ها
- ثبت پرداخت‌های قسط
- ردیابی وام‌های معوقه

#### 5. گزارش‌ها
- موجودی صندوق
- گزارش شارژ‌ها
- گزارش وام‌ها
- برنامه پرداخت

---

## 📊 API Endpoints

### Authentication
```
POST   /api/auth/register      - ثبت‌نام کاربر جدید
POST   /api/auth/login         - ورود کاربر
POST   /api/auth/refresh       - تازه‌سازی توکن
GET    /api/auth/me            - اطلاعات کاربر فعلی
```

### Members
```
GET    /api/members                  - لیست اعضا
GET    /api/members/<id>             - اطلاعات یک عضو
POST   /api/members                  - ایجاد عضو جدید
PUT    /api/members/<id>             - ویرایش عضو
GET    /api/members/<id>/balance     - موجودی عضو
GET    /api/members/<id>/charges     - شارژ‌های عضو
GET    /api/members/count            - تعداد اعضا
```

### Charges
```
GET    /api/charges/annual                    - لیست شارژ‌های سالیانه
POST   /api/charges/annual                    - ایجاد شارژ سالیانه
PUT    /api/charges/annual/<year>             - ویرایش شارژ سالیانه
GET    /api/charges/member/<id>               - شارژ‌های عضو
POST   /api/charges/member/<id>/pay           - پرداخت شارژ
GET    /api/charges/summary                   - خلاصه شارژ‌ها
```

### Loans
```
GET    /api/loans                             - لیست وام‌ها
GET    /api/loans/<id>                        - اطلاعات وام
POST   /api/loans                             - ایجاد وام جدید
GET    /api/loans/<id>/payments               - قسط‌های وام
POST   /api/loans/payments/<id>/record        - ثبت پرداخت قسط
GET    /api/loans/summary                     - خلاصه وام‌ها
```

### Reports
```
GET    /api/reports/fund-balance              - موجودی صندوق
GET    /api/reports/dashboard                 - خلاصه داشبورد
GET    /api/reports/members-balance           - گزارش موجودی اعضا
GET    /api/reports/payments-schedule         - برنامه پرداخت
```

---

## 📁 ساختار پروژه

```
hamyari-fund-manager/
├── backend/
│   ├── app.py                  # فایل اصلی Flask
│   ├── config.py               # تنظیمات
│   ├── services.py             # منطق تجاری
│   ├── models/
│   │   ├── __init__.py
│   │   ├── manager.py
│   │   ├── member.py
│   │   ├── annual_charge.py
│   │   ├── member_charge.py
│   │   ├── loan.py
│   │   ├── loan_payment.py
│   │   ├── fund_balance.py
│   │   ├── activity_log.py
│   │   └── loan_queue.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── members.py
│   │   ├── charges.py
│   │   ├── loans.py
│   │   └── reports.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── css/
│   │   ├── style.css
│   │   └── responsive.css
│   └── js/
│       ├── config.js
│       └── app.js
├── database/
│   └── schema.sql
├── .gitignore
└── README.md
```

---

## 🔧 توسعه و نگهداری

### اضافه کردن ویژگی‌های جدید

1. ایجاد model جدید در `backend/models/`
2. ایجاد route جدید در `backend/routes/`
3. ایجاد service جدید در `backend/services.py`
4. ایجاد UI در `frontend/`
5. تست کامل

### اشکال‌زدایی

```bash
# Backend
FLASK_DEBUG=1 python app.py

# Frontend
# از DevTools مرورگر استفاده کنید (F12)
```

---

## 📝 ثبت تغییرات (Changelog)

### v1.0.0 (2026-06-02)
- ✅ نسخه اولیه
- ✅ مدیریت کامل اعضا
- ✅ سیستم شارژ‌های ماهانه
- ✅ سیستم وام بدون سود
- ✅ گزارش‌های جامع
- ✅ رابط کاربری واکنش‌پذیر

---

## 🐛 گزارش اشکالات

اگر اشکالی پیدا کردید، لطفاً یک issue در GitHub ایجاد کنید.

---

## 📞 تماس و پشتیبانی

- **ایمیل:** support@hamyari-fund.com
- **GitHub:** https://github.com/omenaimir-glitch/hamyari-fund-manager

---

## 📄 لایسنس

MIT License - بدون محدودیت برای استفاده تجاری

---

## 🙏 تشکر

تشکر از تمام کسانی که در توسعه این پروژه کمک کردند.

---

**نسخه:** 1.0.0  
**آخرین بروزرسانی:** 2026-06-02  
**نویسنده:** omenaimir-glitch
