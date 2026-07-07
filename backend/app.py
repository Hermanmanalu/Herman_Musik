# ===== HERMAN MUSIK - BACKEND API (Flask) + LOGIN SYSTEM =====
# Install: pip install -r requirements.txt

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import mysql.connector
import os
from datetime import datetime, timedelta
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import re

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)  # Izinkan request dari frontend

# ===== KONFIGURASI =====
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-env")  # GANTI DI .env!
JWT_EXPIRATION_HOURS = 24

# ===== KONEKSI DATABASE =====
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "herman_musik")
    )


# ===== HELPER: VALIDASI TOKEN & EKSTRAK USER INFO =====
def get_token_from_request():
    """Ekstrak JWT token dari Authorization header"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header[7:]  # Hapus "Bearer " prefix


def verify_token(token):
    """Verifikasi & decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ===== DECORATOR: @login_required =====
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({"error": "Token tidak ditemukan. Silakan login terlebih dahulu"}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Token invalid atau expired"}), 401
        
        # Simpan user info di request context
        request.user_id = payload.get("user_id")
        request.username = payload.get("username")
        request.role = payload.get("role")
        
        return f(*args, **kwargs)
    return decorated_function


# ===== DECORATOR: @admin_required =====
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if request.role != "admin":
            return jsonify({"error": "Akses ditolak. Hanya admin yang dapat mengakses"}), 403
        return f(*args, **kwargs)
    return decorated_function


# ===== VALIDASI =====
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_strong_password(password):
    """Password minimal 8 karakter, ada huruf besar, huruf kecil, angka"""
    if len(password) < 8:
        return False, "Password minimal 8 karakter"
    if not any(c.isupper() for c in password):
        return False, "Password harus ada huruf besar"
    if not any(c.islower() for c in password):
        return False, "Password harus ada huruf kecil"
    if not any(c.isdigit() for c in password):
        return False, "Password harus ada angka"
    return True, "OK"


# ===== FRONTEND ROUTES =====
@app.route("/", methods=["GET"])
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/login", methods=["GET"])
def login_page():
    return send_from_directory(FRONTEND_DIR, "login.html")


@app.route("/favicon.ico")
def favicon():
    return "", 204


# ===== ENDPOINT: HEALTH CHECK =====
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Herman Musik API aktif"})


# ===== ENDPOINT: REGISTER (USER ROLE ONLY) =====
@app.route("/api/register", methods=["POST"])
def register():
    """Pendaftaran user baru (role: user)"""
    data = request.get_json()
    
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    confirm_password = data.get("confirm_password", "").strip()
    
    # Validasi input
    if not username or not email or not password:
        return jsonify({"error": "Username, email, dan password wajib diisi"}), 400
    
    if len(username) < 3:
        return jsonify({"error": "Username minimal 3 karakter"}), 400
    
    if not is_valid_email(email):
        return jsonify({"error": "Email tidak valid"}), 400
    
    if password != confirm_password:
        return jsonify({"error": "Password dan konfirmasi tidak cocok"}), 400
    
    is_strong, msg = is_strong_password(password)
    if not is_strong:
        return jsonify({"error": msg}), 400
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Cek username atau email sudah ada
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({"error": "Username atau email sudah terdaftar"}), 409
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Insert user baru dengan role 'user'
        cursor.execute("""
            INSERT INTO users (username, email, password, role)
            VALUES (%s, %s, %s, 'user')
        """, (username, email, password_hash))
        db.commit()
        
        cursor.close()
        db.close()
        
        return jsonify({"success": True, "message": "Pendaftaran berhasil. Silakan login"}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== ENDPOINT: LOGIN =====
@app.route("/api/login", methods=["POST"])
def login():
    """Login dengan username/email + password"""
    data = request.get_json()
    
    username_or_email = data.get("username_or_email", "").strip()
    password = data.get("password", "").strip()
    
    if not username_or_email or not password:
        return jsonify({"error": "Username/email dan password wajib diisi"}), 400
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Cari user berdasarkan username atau email
        cursor.execute("""
            SELECT id, username, email, password, role FROM users 
            WHERE username = %s OR email = %s
        """, (username_or_email, username_or_email))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not user:
            return jsonify({"error": "Username/email atau password salah"}), 401
        
        # Verifikasi password
        if not check_password_hash(user["password"], password):
            return jsonify({"error": "Username/email atau password salah"}), 401
        
        # Generate JWT token
        payload = {
            "user_id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            "success": True,
            "message": f"Login berhasil. Selamat datang {user['username']}",
            "token": token,
            "role": user["role"],
            "username": user["username"]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== ENDPOINT: LOGOUT =====
@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    """Logout user - token dihapus di frontend (localStorage)"""
    return jsonify({
        "success": True,
        "message": f"Logout berhasil. Terima kasih {request.username}"
    }), 200


# ===== ENDPOINT: VERIFY TOKEN & GET CURRENT USER =====
@app.route("/api/verify-token", methods=["GET"])
@login_required
def verify_token_endpoint():
    """Cek apakah token masih valid dan ambil info user"""
    return jsonify({
        "success": True,
        "user_id": request.user_id,
        "username": request.username,
        "role": request.role
    }), 200


# ===== ENDPOINT: SIMPAN PERMINTAAN (dari form kontak) =====
@app.route("/api/permintaan", methods=["POST"])
def tambah_permintaan():
    data = request.get_json()

    nama    = data.get("nama", "").strip()
    wa      = data.get("wa", "").strip()
    tanggal = data.get("tanggal", None)
    tamu    = data.get("tamu", "")
    jenis   = data.get("jenis", "")
    pesan   = data.get("pesan", "")

    if not nama or not wa:
        return jsonify({"error": "Nama dan WhatsApp wajib diisi"}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO permintaan (nama, no_wa, tanggal_acara, jumlah_tamu, jenis_acara, pesan, dibuat_pada)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nama, wa, tanggal or None, tamu, jenis, pesan, datetime.now()))
        db.commit()
        permintaan_id = cursor.lastrowid
        cursor.close()
        db.close()

        return jsonify({
            "success": True,
            "message": "Permintaan berhasil disimpan",
            "id": permintaan_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== ENDPOINT: AMBIL SEMUA PERMINTAAN (admin only) =====
@app.route("/api/permintaan", methods=["GET"])
@admin_required
def get_permintaan():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM permintaan ORDER BY dibuat_pada DESC")
        rows = cursor.fetchall()
        # Konversi datetime ke string agar bisa di-JSON-kan
        for row in rows:
            if row.get("dibuat_pada"):
                row["dibuat_pada"] = str(row["dibuat_pada"])
            if row.get("tanggal_acara"):
                row["tanggal_acara"] = str(row["tanggal_acara"])
        cursor.close()
        db.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== ENDPOINT: AMBIL SEMUA PRODUK =====
@app.route("/api/produk", methods=["GET"])
def get_produk():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produk WHERE aktif = 1 ORDER BY id ASC")
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== ENDPOINT: AMBIL SEMUA PAKET =====
@app.route("/api/paket", methods=["GET"])
def get_paket():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM paket ORDER BY harga ASC")
        rows = cursor.fetchall()
        # Ambil item tiap paket
        for paket in rows:
            cursor2 = db.cursor(dictionary=True)
            cursor2.execute("SELECT item FROM paket_item WHERE paket_id = %s", (paket["id"],))
            paket["items"] = [r["item"] for r in cursor2.fetchall()]
            cursor2.close()
        cursor.close()
        db.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== ENDPOINT: AMBIL SEMUA TESTIMONI =====
@app.route("/api/testimoni", methods=["GET"])
def get_testimoni():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM testimoni WHERE tampilkan = 1 ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== ENDPOINT: TAMBAH TESTIMONI =====
@app.route("/api/testimoni", methods=["POST"])
def tambah_testimoni():
    data = request.get_json()
    nama    = data.get("nama", "").strip()
    lokasi  = data.get("lokasi", "").strip()
    teks    = data.get("teks", "").strip()
    bintang = data.get("bintang", 5)

    if not nama or not teks:
        return jsonify({"error": "Nama dan teks testimoni wajib diisi"}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO testimoni (nama, lokasi, teks, bintang, tampilkan)
            VALUES (%s, %s, %s, %s, 0)
        """, (nama, lokasi, teks, bintang))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"success": True, "message": "Testimoni dikirim, menunggu persetujuan"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
