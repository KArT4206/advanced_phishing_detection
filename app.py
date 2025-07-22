from flask import Flask, request, render_template, redirect, session, url_for, jsonify
import os
import auth_utils
from auth_utils import auth, store_login_info, get_client_ip, get_mac
from run_all_detectors import run_all_detectors

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define admin email
ADMIN_EMAIL = "karthikb0404@gmail.com"

# --- Home Redirect ---
@app.route("/")
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('manual_check'))

# --- Firebase User Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            ip = get_client_ip()
            mac = get_mac()
            store_login_info(email, ip, mac, password=password)
            return redirect('/manual-check')
        except Exception as e:
            return f"Login Failed: {str(e)}"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            auth.create_user_with_email_and_password(email, password)
            return redirect('/login')
        except Exception as e:
            return f"Registration Failed: {str(e)}"
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return f"Welcome, {session['user']}"

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/login')
    if session['user'] != ADMIN_EMAIL:
        return "Access Denied: You are not an admin."
    login_info = auth_utils.db.child("login_info").get().val()
    return render_template('admin_dashboard.html', login_data=login_info)

# --- Manual Check ---
@app.route("/manual-check", methods=["GET", "POST"])
def manual_check():
    if 'user' not in session:
        return redirect('/login')
    if request.method == "POST":
        url = request.form.get("url")
        result = run_all_detectors(url)
        return render_template(
            "result.html",
            result=result,
            url=result["url"],
            trust_score=result["trust_score"],
            verdict=result["verdict"],
            triggered_checks=result["triggered_checks"],
            nlp_intent=result["nlp_intent"],
            ocr_text=result["ocr_text"],
            visual_score=result["visual_score"],
            matched_brand=result.get("matched_brand", ""),
            screenshot_url=result["screenshot_url"],
            tls_result=result["tls_result"],
            domain_info=result["domain_info"],
            url_features=result["url_features"],
            js_flags=result["js_flags"],
            visual_flags=result["visual_flags"],
            dom_flags=result["dom_flags"]
        )
    return render_template("manual_check.html")

# --- Chrome Extension API ---
@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.get_json()
    url = data.get("url")
    result = run_all_detectors(url)
    return jsonify(result)

# --- Static Files (Screenshots etc) ---
@app.route("/static/<path:filename>")
def static_files(filename):
    return app.send_static_file(filename)

# --- Server Start ---
if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(debug=True, port=5000)
