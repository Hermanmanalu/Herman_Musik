// ===== LOGIN & REGISTER LOGIC =====

const API_URL = 'http://localhost:5000/api';

// DOM Elements
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const loginTab = document.getElementById('login-tab');
const registerTab = document.getElementById('register-tab');
const tabContents = document.querySelectorAll('.login-tab-content');

// Tab Navigation
loginTab.addEventListener('click', () => switchTab('login'));
registerTab.addEventListener('click', () => switchTab('register'));

function switchTab(tab) {
    // Update tabs
    loginTab.classList.toggle('active', tab === 'login');
    registerTab.classList.toggle('active', tab === 'register');

    // Update content
    tabContents.forEach((content, index) => {
        if ((tab === 'login' && index === 0) || (tab === 'register' && index === 1)) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
}

// ===== LOGIN HANDLER =====
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username_or_email = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const rememberMe = document.getElementById('remember-me').checked;

    const errorDiv = document.getElementById('login-error');
    const loadingDiv = document.getElementById('login-loading');

    // Clear previous messages
    errorDiv.innerHTML = '';
    errorDiv.classList.remove('show');

    // Validasi basic
    if (!username_or_email || !password) {
        showError(errorDiv, 'Username/email dan password harus diisi');
        return;
    }

    try {
        loadingDiv.style.display = 'block';
        loadingDiv.classList.add('show');

        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username_or_email,
                password
            })
        });

        const data = await response.json();
        loadingDiv.style.display = 'none';
        loadingDiv.classList.remove('show');

        if (!response.ok) {
            throw new Error(data.error || 'Login gagal');
        }

        // Simpan token
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('user_role', data.role);
        localStorage.setItem('username', data.username);

        if (rememberMe) {
            localStorage.setItem('remember_username', username_or_email);
        }

        // Redirect berdasarkan role
        if (data.role === 'admin') {
            window.location.href = 'admin-dashboard.html';
        } else {
            window.location.href = 'index.html';
        }

    } catch (error) {
        loadingDiv.style.display = 'none';
        loadingDiv.classList.remove('show');
        showError(errorDiv, error.message);
    }
});

// ===== REGISTER HANDLER =====
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm').value;

    const errorDiv = document.getElementById('register-error');
    const successDiv = document.getElementById('register-success');
    const loadingDiv = document.getElementById('register-loading');

    // Clear previous messages
    errorDiv.innerHTML = '';
    errorDiv.classList.remove('show');
    successDiv.innerHTML = '';
    successDiv.classList.remove('show');

    // Validasi
    if (!username || !email || !password || !confirmPassword) {
        showError(errorDiv, 'Semua field harus diisi');
        return;
    }

    if (username.length < 3) {
        showError(errorDiv, 'Username minimal 3 karakter');
        return;
    }

    if (!isValidEmail(email)) {
        showError(errorDiv, 'Email tidak valid');
        return;
    }

    if (password !== confirmPassword) {
        showError(errorDiv, 'Password dan konfirmasi tidak cocok');
        return;
    }

    if (!isStrongPassword(password)) {
        showError(errorDiv, 'Password harus minimal 8 karakter dengan huruf besar, huruf kecil, dan angka');
        return;
    }

    try {
        loadingDiv.style.display = 'block';
        loadingDiv.classList.add('show');

        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                email,
                password,
                confirm_password: confirmPassword
            })
        });

        const data = await response.json();
        loadingDiv.style.display = 'none';
        loadingDiv.classList.remove('show');

        if (!response.ok) {
            throw new Error(data.error || 'Pendaftaran gagal');
        }

        // Reset form
        registerForm.reset();

        // Show success message
        successDiv.textContent = data.message;
        successDiv.classList.add('show');
        successDiv.style.display = 'block';

        // Switch to login tab after 2 seconds
        setTimeout(() => {
            switchTab('login');
            document.getElementById('login-username').value = username;
            document.getElementById('login-username').focus();
        }, 2000);

    } catch (error) {
        loadingDiv.style.display = 'none';
        loadingDiv.classList.remove('show');
        showError(errorDiv, error.message);
    }
});

// ===== HELPER FUNCTIONS =====

function showError(element, message) {
    element.textContent = message;
    element.classList.add('show');
    element.style.display = 'block';
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isStrongPassword(password) {
    if (password.length < 8) return false;
    if (!/[A-Z]/.test(password)) return false;  // Minimal satu huruf besar
    if (!/[a-z]/.test(password)) return false;  // Minimal satu huruf kecil
    if (!/[0-9]/.test(password)) return false;  // Minimal satu angka
    return true;
}

// ===== AUTO-LOAD USERNAME JIKA "REMEMBER ME" AKTIF =====
window.addEventListener('DOMContentLoaded', () => {
    const rememberedUsername = localStorage.getItem('remember_username');
    if (rememberedUsername) {
        document.getElementById('login-username').value = rememberedUsername;
        document.getElementById('remember-me').checked = true;
    }

    // Cek apakah sudah login
    const token = localStorage.getItem('auth_token');
    if (token) {
        verifyTokenAndRedirect();
    }
});

// ===== VERIFY TOKEN SAAT PAGE LOAD =====
async function verifyTokenAndRedirect() {
    try {
        const token = localStorage.getItem('auth_token');
        if (!token) return;

        const response = await fetch(`${API_URL}/verify-token`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            // Jika token valid, redirect ke dashboard sesuai role
            if (data.role === 'admin') {
                window.location.href = 'admin-dashboard.html';
            } else {
                window.location.href = 'index.html';
            }
        } else {
            // Token invalid/expired, hapus
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_role');
            localStorage.removeItem('username');
        }
    } catch (error) {
        console.error('Token verification error:', error);
    }
}
