# ===== FRONTEND ROUTES =====
@app.route("/login", methods=["GET"])
def login_page():
    return send_from_directory(FRONTEND_DIR, "login.html")

@app.route("/", methods=["GET"])
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/favicon.ico")
def favicon():
    return "", 204