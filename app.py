from flask import Flask, request, render_template_string, redirect, send_from_directory
import os

app = Flask(__name__)

# مجلد الحفظ التلقائي للمستندات
UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 🔐 كلمات المرور
STUDENT_PASSWORD = "1234"      # باسوورد الطلاب
TEACHER_PASSWORD = "zedzed"     # باسوورد الأستاذ

# 1. صفحة الدخول الموحدة التي تفتح عبر الرابط مباشرة
@app.route('/')
@app.route('/view')
def login_page():
    html_login = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📚 منصة الدروس الخصوصية الآمنة</title>
        <style>
            body { font-family: sans-serif; text-align: center; margin-top: 80px; background: #f0f2f5; }
            .box { background: white; padding: 40px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 90%; max-width: 400px; }
            input, button { padding: 12px; font-size: 16px; margin: 10px 0; border-radius: 6px; border: 1px solid #ccc; width: 100%; box-sizing: border-box; }
            button { background: #007bff; color: white; border: none; cursor: pointer; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>📚 بوابة الدخول للمنصة</h2>
            <p>يرجى إدخال رمز المرور الخاص بك للدخول.</p>
            <form method="POST" action="/verify">
                <input type="password" name="password" placeholder="أدخل رمز المرور هنا" required><br>
                <button type="submit">تسجيل الدخول</button>
            </form>
            {% if error %}<p style="color:red; font-weight:bold;">❌ رمز المرور غير صحيح!</p>{% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_login, error=request.args.get('error'))

# 2. التحقق من الصلاحيات
@app.route('/verify', methods=['POST'])
def verify():
    pwd = request.form.get('password')
    if pwd == TEACHER_PASSWORD:
        return redirect('/teacher_dashboard')
    elif pwd == STUDENT_PASSWORD:
        return redirect('/student_dashboard')
    return redirect('/view?error=1')

# 3. لوحة الطلاب
@app.route('/student_dashboard')
def student_dashboard():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    html_student = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📂 مكتبة الدروس</title>
        <style>
            body { font-family: sans-serif; background: #f8f9fa; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
            .file-link { display: block; padding: 15px; background: #fff; border: 1px solid #ddd; margin: 8px 0; border-radius: 6px; text-decoration: none; color: #17a2b8; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🎓 لوحة الطلاب</h2>
            <hr>
            <h3>📥 الدروس والمستندات المتوفرة:</h3>
            {% if not files %}
                <p style="color: #666;">لا توجد دروس مرفوعة حالياً.</p>
            {% endif %}
            {% for file in files %}
                <a href="/download/{{ file }}" target="_blank" class="file-link">📖 تحميل الدرس: {{ file }}</a>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_student, files=files)

# 4. لوحة الأستاذ السرية
@app.route('/teacher_dashboard')
def teacher_dashboard():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    html_teacher = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>⚙️ لوحة تحكم الأستاذ</title>
        <style>
            body { font-family: sans-serif; background: #f4f6f9; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 25px; border-radius: 10px; }
            .upload-box { background: #e9ecef; padding: 15px; border-radius: 6px; text-align: center; margin-bottom:20px; }
            .file-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>⚙️ لوحة تحكم الأستاذ</h2>
            <div class="upload-box">
                <form method="POST" action="/upload" enctype="multipart/form-data">
                    <input type="file" name="file" required><br><br>
                    <button type="submit" style="padding:10px 20px; background:#28a745; color:#fff; border:none; border-radius:4px;">نشر الدرس الآن</button>
                </form>
            </div>
            <h3>📋 الدروس المنشورة:</h3>
            {% for file in files %}
                <div class="file-item">
                    <span>📄 {{ file }}</span>
                    <a href="/delete/{{ file }}" style="color:red;">❌ حذف</a>
                </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_teacher, files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return redirect('/teacher_dashboard')
    file = request.files['file']
    if file.filename == '': return redirect('/teacher_dashboard')
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return redirect('/teacher_dashboard')

@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path): os.remove(file_path)
    return redirect('/teacher_dashboard')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# الربط الديناميكي الإجباري لخوادم الإنترنت العالمية ⚠️
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
