#!/bin/bash
# Install script for Hamyari Fund Manager

echo "====================================="
echo "مدیریت صندوق همیاری - اسکریپت نصب"
echo "====================================="

# رنگ‌ها برای output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# بررسی نیازمندی‌ها
echo -e "${YELLOW}بررسی نیازمندی‌ها...${NC}"

# بررسی Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 نصب نشده است. لطفاً Python 3.8+ را نصب کنید.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python پیدا شد$(python3 --version)${NC}"

# بررسی MySQL
if ! command -v mysql &> /dev/null; then
    echo -e "${RED}MySQL نصب نشده است. لطفاً MySQL 8.0+ را نصب کنید.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ MySQL پیدا شد${NC}"

# ایجاد Virtual Environment
echo -e "${YELLOW}\nایجاد Virtual Environment...${NC}"
cd backend
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}✓ Virtual Environment ایجاد شد${NC}"

# نصب وابستگی‌ها
echo -e "${YELLOW}\nنصب وابستگی‌ها...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✓ وابستگی‌ها نصب شدند${NC}"

# تنظیم .env
echo -e "${YELLOW}\nتنظیم فایل .env...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}لطفاً فایل .env را ویرایش کنید و اطلاعات پایگاه داده را وارد کنید.${NC}"
fi

echo -e "${GREEN}✓ فایل .env آماده است${NC}"

echo -e "\n${GREEN}=====================================${NC}"
echo -e "${GREEN}نصب تکمیل شد! 🎉${NC}"
echo -e "${GREEN}=====================================${NC}"

echo -e "\n${YELLOW}مراحل بعدی:${NC}"
echo "1. فایل .env را ویرایش کنید و اطلاعات پایگاه داده را وارد کنید"
echo "2. پایگاه داده را ایجاد کنید: mysql -u root -p < ../database/schema.sql"
echo "3. Backend را اجرا کنید: python app.py"
echo "4. Frontend را در مرورگر باز کنید: http://localhost:8000"
