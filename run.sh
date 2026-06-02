#!/bin/bash
# Run script for Hamyari Fund Manager

echo "====================================="
echo "مدیریت صندوق همیاری - اجرا"
echo "====================================="

# رنگ‌ها
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# فعال‌سازی Virtual Environment
echo -e "${YELLOW}فعال‌سازی Virtual Environment...${NC}"
cd backend
source venv/bin/activate

echo -e "${GREEN}✓ Virtual Environment فعال شد${NC}"

# بررسی فایل .env
if [ ! -f .env ]; then
    echo -e "${RED}فایل .env یافت نشد. لطفاً install.sh را اجرا کنید.${NC}"
    exit 1
fi

# اجرای Backend
echo -e "${YELLOW}\nاجرای Backend...${NC}"
echo -e "${GREEN}سرور روی http://localhost:5000 اجرا می‌شود${NC}"
echo -e "${GREEN}Frontend را در http://localhost:8000 باز کنید${NC}"

python app.py
