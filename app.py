from flask import Flask, request, render_template_string, redirect, send_from_directory
import qrcode
import socket
import os

app = Flask(__name__)

# Setup secure directory to hold uploaded files from your phone
UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ==========================================
# 🔐 إعدادات كلمات المرور والتحكم (غيرها كما تشاء)
# ==========================================
STUDENT_PASSWORD = "1234"      # باسوورد الطلاب (عرض فقط)
TEACHER_PASSWORD = "admin"  # باسوورد الأستاذ (صلاحية الرفع والتعديل)
# ==========================================


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

SERVER_URL = f"http://{get_local_ip()}:5000/view"

@app.route('/view')
def login_page():
    html_login = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🔒 نظام الملفات الآمن</title>
        <style>
            body { font-family: sans-serif; text-align: center; margin-top: 100px; background: #f0f2f5; }
            .box { background: white; padding: 40px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 90%; max-width: 400px; }
            input, button { padding: 12px; font-size: 16px; margin: 10px 0; border-radius: 6px; border: 1px solid #ccc; width: 100%; box-sizing: border-box; }
            button { background: #007bff; color: white; border: none; cursor: pointer; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>🔒 محتوى محمي</h2>
            <form method="POST" action="/verify">
                <input type="password" name="password" placeholder="كلمة المرور" required><br>
                <button type="submit">دخول للملفات</button>
            </form>
            {% if error %}<p style="color:red;">❌ كلمة المرور خاطئة!</p>{% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_login, error=request.args.get('error'))

@app.route('/verify', methods=['POST'])
def verify():
    if request.form.get('password') == PASSWORD:
        return redirect('/dashboard')
    return redirect('/view?error=1')

@app.route('/dashboard')
def dashboard():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    html_dashboard = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📂 لوحة ملفاتي</title>
        <style>
            body { font-family: sans-serif; background: #f8f9fa; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
            .upload-section { background: #e9ecef; padding: 15px; border-radius: 6px; margin-bottom: 20px; text-align: center; }
            .file-link { display: block; padding: 12px; background: #fff; border: 1px solid #ddd; margin: 8px 0; border-radius: 6px; text-decoration: none; color: #007bff; font-weight: bold; }
            .file-link:hover { background: #f0f4f8; }
            input[type="file"] { margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📂 مستودع الملفات الذكي</h2>
            
            <div class="upload-section">
                <h3>📤 رفع ملف جديد من ذاكرة هذا الهاتف:</h3>
                <form method="POST" action="/upload" enctype="multipart/form-data">
                    <input type="file" name="file" required><br>
                    <button type="submit" style="padding:10px 20px; background:#28a745; color:#fff; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">ابدأ الرفع المباشر</button>
                </form>
            </div>

            <h3>📥 الملفات المخزنة المتاحة حالياً:</h3>
            {% if not files %}
                <p style="color: #666;">لا توجد ملفات مرفوعة حالياً. استخدم الزر أعلاه لإضافة أول ملف من جوالك.</p>
            {% endif %}
            {% for file in files %}
                <a href="/download/{{ file }}" target="_blank" class="file-link">📄 {{ file }}</a>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_dashboard, files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return redirect('/dashboard')
    file = request.files['file']
    if file.filename == '': return redirect('/dashboard')
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return redirect('/dashboard')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if os.path.exists("my_secure_permanent_qr.png"):
        os.remove("my_secure_permanent_qr.png")
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(SERVER_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("my_secure_permanent_qr.png")
    print(f"\n[+] SUCCESS: New QR code generated targeting: {SERVER_URL}")
    app.run(host='0.0.0.0', port=5000)
