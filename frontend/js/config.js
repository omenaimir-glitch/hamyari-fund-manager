// تنظیمات API
const API_BASE_URL = 'http://localhost:5000/api';
let authToken = localStorage.getItem('authToken') || null;
let currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');

// معادل‌سازی localStorage
function saveToken(token) {
    authToken = token;
    localStorage.setItem('authToken', token);
}

function saveUser(user) {
    currentUser = user;
    localStorage.setItem('currentUser', JSON.stringify(user));
}

function clearAuth() {
    authToken = null;
    currentUser = {};
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
}

// تابع کمکی برای درخواست‌های HTTP
async function apiCall(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (authToken) {
        options.headers['Authorization'] = `Bearer ${authToken}`;
    }

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        const result = await response.json();

        if (response.status === 401) {
            clearAuth();
            window.location.href = 'login.html';
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: 'خطا در ارتباط با سرور' };
    }
}

// API Functions
const API = {
    // Auth
    register: (data) => apiCall('/auth/register', 'POST', data),
    login: (data) => apiCall('/auth/login', 'POST', data),
    getCurrentUser: () => apiCall('/auth/me'),

    // Members
    getMembers: (page = 1, perPage = 10) => apiCall(`/members?page=${page}&per_page=${perPage}`),
    getMember: (id) => apiCall(`/members/${id}`),
    createMember: (data) => apiCall('/members', 'POST', data),
    updateMember: (id, data) => apiCall(`/members/${id}`, 'PUT', data),
    getMemberBalance: (id) => apiCall(`/members/${id}/balance`),
    getMembersCount: () => apiCall('/members/count'),

    // Charges
    getAnnualCharges: () => apiCall('/charges/annual'),
    createAnnualCharge: (data) => apiCall('/charges/annual', 'POST', data),
    updateAnnualCharge: (year, data) => apiCall(`/charges/annual/${year}`, 'PUT', data),
    getMemberCharges: (id, year = null) => apiCall(`/charges/member/${id}${year ? `?year=${year}` : ''}`),
    payCharge: (id, data) => apiCall(`/charges/member/${id}/pay`, 'POST', data),
    getChargesSummary: () => apiCall('/charges/summary'),

    // Loans
    getLoans: (page = 1, status = null) => apiCall(`/loans?page=${page}${status ? `&status=${status}` : ''}`),
    getLoan: (id) => apiCall(`/loans/${id}`),
    createLoan: (data) => apiCall('/loans', 'POST', data),
    getLoanPayments: (id) => apiCall(`/loans/${id}/payments`),
    recordPayment: (id, data) => apiCall(`/loans/payments/${id}/record`, 'POST', data),
    getLoansSummary: () => apiCall('/loans/summary'),

    // Reports
    getFundBalance: () => apiCall('/reports/fund-balance'),
    getDashboardSummary: () => apiCall('/reports/dashboard'),
    getMembersBalanceReport: (page = 1) => apiCall(`/reports/members-balance?page=${page}`),
    getPaymentSchedule: (page = 1, status = 'pending') => apiCall(`/reports/payments-schedule?page=${page}&status=${status}`)
};
