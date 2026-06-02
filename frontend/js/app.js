// توابع کمکی
function formatCurrency(value) {
    return new Intl.NumberFormat('fa-IR', {
        style: 'currency',
        currency: 'IRR'
    }).format(value);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
}

function getStatusBadge(status) {
    const badges = {
        'active': '<span class="badge badge-success">فعال</span>',
        'inactive': '<span class="badge badge-warning">غیرفعال</span>',
        'blocked': '<span class="badge badge-danger">مسدود</span>',
        'paid': '<span class="badge badge-success">پرداخت شده</span>',
        'pending': '<span class="badge badge-pending">معلق</span>',
        'overdue': '<span class="badge badge-danger">معوقه</span>',
        'completed': '<span class="badge badge-success">تکمیل شده</span>'
    };
    return badges[status] || `<span class="badge">${status}</span>`;
}

function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.main-content');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

// Navigation
function navigate(section) {
    // حذف active class از تمام sections
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    
    // اضافه کردن active class به section و nav-link مربوطه
    document.getElementById(`${section}-section`).classList.add('active');
    event.target.classList.add('active');
    
    // بارگذاری داده‌ها
    loadSectionData(section);
}

function loadSectionData(section) {
    switch(section) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'members':
            loadMembers();
            break;
        case 'charges':
            loadCharges();
            break;
        case 'loans':
            loadLoans();
            break;
        case 'reports':
            loadReports();
            break;
    }
}

// Logout
async function logout() {
    if (confirm('آیا مطمئن هستید؟')) {
        clearAuth();
        window.location.href = 'login.html';
    }
}

// Dashboard
async function loadDashboard() {
    const response = await API.getDashboardSummary();
    
    if (response.success) {
        const data = response.data;
        
        document.getElementById('total-members').textContent = data.members.total;
        document.getElementById('active-members').textContent = data.members.active;
        document.getElementById('fund-balance').textContent = formatCurrency(data.fund.total_balance);
        document.getElementById('active-loans').textContent = data.loans.active;
        document.getElementById('overdue-charges').textContent = formatCurrency(data.charges.overdue);
    }
}

// Members
async function loadMembers(page = 1) {
    const response = await API.getMembers(page);
    
    if (response.success) {
        const tbody = document.getElementById('members-tbody');
        tbody.innerHTML = '';
        
        response.data.forEach(member => {
            const row = `
                <tr>
                    <td>${member.name}</td>
                    <td>${member.national_id}</td>
                    <td>${member.phone}</td>
                    <td>${formatCurrency(member.total_balance)}</td>
                    <td>${formatCurrency(member.active_loans)}</td>
                    <td>${getStatusBadge(member.status)}</td>
                    <td>
                        <button class="btn btn-small btn-primary" onclick="editMember(${member.id})">ویرایش</button>
                        <button class="btn btn-small btn-secondary" onclick="viewMemberDetails(${member.id})">جزئیات</button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    }
}

// Member Modal Functions
function openAddMemberModal() {
    document.getElementById('member-form').reset();
    document.getElementById('member-modal').classList.add('active');
}

function closeMemberModal() {
    document.getElementById('member-modal').classList.remove('active');
}

async function saveMember(event) {
    event.preventDefault();
    
    const data = {
        name: document.getElementById('member-name').value,
        national_id: document.getElementById('member-national-id').value,
        phone: document.getElementById('member-phone').value,
        email: document.getElementById('member-email').value
    };
    
    const response = await API.createMember(data);
    
    if (response.success) {
        showAlert('عضو با موفقیت ایجاد شد');
        closeMemberModal();
        loadMembers();
    } else {
        showAlert(response.error, 'error');
    }
}

// Charges
async function loadCharges() {
    const response = await API.getChargesSummary();
    
    if (response.success) {
        const data = response.data;
        console.log('Charges Summary:', data);
        // نمایش داده‌ها در جدول
    }
}

// Charge Modal Functions
function openAddChargeModal() {
    document.getElementById('charge-form').reset();
    document.getElementById('charge-year').value = new Date().getFullYear();
    document.getElementById('charge-modal').classList.add('active');
}

function closeChargeModal() {
    document.getElementById('charge-modal').classList.remove('active');
}

async function saveCharge(event) {
    event.preventDefault();
    
    const data = {
        year: parseInt(document.getElementById('charge-year').value),
        charge_amount: parseFloat(document.getElementById('charge-amount').value),
        effective_from: document.getElementById('charge-effective-from').value || new Date().toISOString().split('T')[0]
    };
    
    const response = await API.createAnnualCharge(data);
    
    if (response.success) {
        showAlert('شارژ سالیانه با موفقیت ایجاد شد');
        closeChargeModal();
        loadCharges();
    } else {
        showAlert(response.error, 'error');
    }
}

// Loans
async function loadLoans() {
    const response = await API.getLoans();
    
    if (response.success) {
        const tbody = document.getElementById('loans-tbody');
        tbody.innerHTML = '';
        
        response.data.forEach(loan => {
            const member = loan.member || { name: 'نامشخص' };
            const row = `
                <tr>
                    <td>${member.name}</td>
                    <td>${formatCurrency(loan.amount)}</td>
                    <td>${formatDate(loan.loan_date)}</td>
                    <td>${formatCurrency(loan.monthly_payment)}</td>
                    <td>${formatCurrency(loan.total_remaining)}</td>
                    <td>${getStatusBadge(loan.status)}</td>
                    <td>
                        <button class="btn btn-small btn-secondary" onclick="viewLoanDetails(${loan.id})">جزئیات</button>
                    </td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    }
}

// Loan Modal Functions
function openAddLoanModal() {
    document.getElementById('loan-form').reset();
    document.getElementById('loan-date').valueAsDate = new Date();
    document.getElementById('loan-modal').classList.add('active');
}

function closeLoanModal() {
    document.getElementById('loan-modal').classList.remove('active');
}

async function saveLoan(event) {
    event.preventDefault();
    
    const memberId = parseInt(document.getElementById('loan-member-id').value);
    const amount = parseFloat(document.getElementById('loan-amount').value);
    const loanDate = document.getElementById('loan-date').value;
    
    const data = {
        member_id: memberId,
        amount: amount,
        loan_date: loanDate
    };
    
    const response = await API.createLoan(data);
    
    if (response.success) {
        showAlert('وام با موفقیت ایجاد شد');
        closeLoanModal();
        loadLoans();
    } else {
        showAlert(response.error, 'error');
    }
}

// Reports
async function loadReports() {
    const response = await API.getFundBalance();
    
    if (response.success) {
        document.getElementById('report-fund-balance').textContent = formatCurrency(response.data.available_balance);
    }
}

// Initialization
document.addEventListener('DOMContentLoaded', async () => {
    // بررسی احراز هویت
    if (!authToken) {
        window.location.href = 'login.html';
        return;
    }
    
    // بارگذاری اطلاعات کاربر
    const userResponse = await API.getCurrentUser();
    if (userResponse.success) {
        saveUser(userResponse.data);
    }
    
    // بارگذاری داشبورد
    loadDashboard();
});
