from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)

app.secret_key = "avanor_secret_key_2026"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///avanor.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    role = db.Column(db.String(50), default="admin")


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(300), default="بدون آدرس")


class Contractor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    job = db.Column(db.String(200), nullable=False)
    contract_image = db.Column(db.String(300), default="")


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey("contractor.id"), nullable=False)
    date = db.Column(db.String(20))
    description = db.Column(db.String(500))
    meterage = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Integer, default=0)
    total_price = db.Column(db.Integer, default=0)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey("contractor.id"), nullable=False)
    date = db.Column(db.String(20))
    description = db.Column(db.String(500))
    amount = db.Column(db.Integer, default=0)


HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<title>Avanor Group</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');

*{box-sizing:border-box;}

body{
    margin:0;
    font-family:'Vazirmatn', Tahoma, sans-serif;
    background:#eef2f7;
    color:#1f2937;
    font-size:14px;
}

.header{
    background:linear-gradient(135deg,#0f172a,#1e3a8a,#2563eb);
    color:white;
    padding:28px 20px;
    text-align:center;
    position:relative;
}

.header h1{
    margin:0;
    font-size:26px;
    font-weight:800;
}

.header p{
    margin:7px 0 0;
    font-size:13px;
    opacity:.88;
}

.logout-box{
    position:absolute;
    left:20px;
    top:20px;
}

.container{
    max-width:1200px;
    margin:auto;
    padding:24px;
}

.card{
    background:white;
    border:1px solid #e5e7eb;
    border-radius:18px;
    padding:20px;
    margin-bottom:16px;
    box-shadow:0 10px 30px rgba(15,23,42,.07);
}

.card h1{font-size:24px;margin:0 0 10px;}
.card h2{font-size:18px;margin:0 0 10px;color:#0f172a;}
.card h3{font-size:15px;margin:0 0 12px;color:#1e3a8a;}
.card p{margin:6px 0;font-size:13px;color:#64748b;}

input{
    width:100%;
    padding:11px 13px;
    margin:7px 0;
    border:1px solid #d1d5db;
    border-radius:12px;
    font-size:13px;
    font-family:'Vazirmatn', Tahoma, sans-serif;
    outline:none;
    background:#f9fafb;
}

input:focus{
    border-color:#2563eb;
    background:white;
    box-shadow:0 0 0 3px rgba(37,99,235,.12);
}

.hint{
    font-size:11px;
    color:#64748b;
    margin-top:-2px;
    margin-bottom:8px;
}

.btn{
    display:inline-block;
    background:#2563eb;
    color:white;
    padding:9px 16px;
    border-radius:11px;
    text-decoration:none;
    margin-top:8px;
    border:none;
    cursor:pointer;
    font-size:13px;
    font-family:'Vazirmatn', Tahoma, sans-serif;
    font-weight:600;
}

.btn:hover{background:#1d4ed8;}
.back{background:#475569;}
.back:hover{background:#334155;}
.delete-btn{background:#dc2626;}
.delete-btn:hover{background:#b91c1c;}
.edit-btn{background:#f59e0b;color:#111827;}
.edit-btn:hover{background:#d97706;color:white;}
.print-btn{background:#7c3aed;}
.print-btn:hover{background:#6d28d9;}
.logout-btn{background:#ef4444;padding:8px 14px;margin:0;}
.logout-btn:hover{background:#b91c1c;}

.project-item{
    background:#f8fafc;
    border:1px solid #e2e8f0;
    border-radius:15px;
    padding:15px;
    margin-bottom:10px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:12px;
}

.project-info h3{
    margin:0 0 5px;
    color:#0f172a;
    font-size:15px;
}

.project-info p{
    margin:0;
    color:#64748b;
    font-size:12px;
}

.menu{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
    gap:14px;
    margin-top:18px;
}

.menu a{
    background:white;
    text-align:center;
    padding:22px 14px;
    border-radius:16px;
    text-decoration:none;
    color:#1e3a8a;
    font-size:16px;
    font-weight:700;
    border:1px solid #e5e7eb;
    box-shadow:0 8px 22px rgba(15,23,42,.06);
}

.option-list a{
    display:block;
    background:#f8fafc;
    border:1px solid #e2e8f0;
    border-radius:14px;
    padding:14px;
    margin-bottom:10px;
    text-decoration:none;
    color:#1e3a8a;
    font-size:15px;
    font-weight:700;
}

table{
    width:100%;
    border-collapse:separate;
    border-spacing:0;
    background:white;
    margin-top:14px;
    overflow:hidden;
    border-radius:14px;
    border:1px solid #e5e7eb;
}

th,td{
    padding:12px;
    border-bottom:1px solid #e5e7eb;
    text-align:center;
    font-size:13px;
}

th{
    background:#f1f5f9;
    color:#0f172a;
    font-weight:700;
}

tr:last-child td{border-bottom:none;}

.total-row{
    background:#f8fafc;
    font-weight:800;
}

.checkbox-small{
    width:18px;
    height:18px;
    cursor:pointer;
}

.form-grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
    gap:10px;
}

.actions{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    align-items:center;
}

.edit-box{
    display:none;
    border:1px dashed #f59e0b;
    background:#fffbeb;
    border-radius:16px;
    padding:16px;
    margin-top:16px;
}

.contract-img{
    max-width:100%;
    border-radius:14px;
    margin-top:15px;
    border:1px solid #ddd;
}

.credit{
    color:#047857;
    font-weight:700;
}

.debit{
    color:#dc2626;
    font-weight:700;
}

.login-page{
    min-height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
    background:linear-gradient(135deg,#0f172a,#1e3a8a,#2563eb);
    padding:20px;
}

.login-card{
    width:380px;
    background:white;
    border-radius:22px;
    padding:28px;
    box-shadow:0 25px 70px rgba(0,0,0,.25);
}

.login-card h1{
    text-align:center;
    margin:0;
    color:#0f172a;
}

.login-card p{
    text-align:center;
    color:#64748b;
    font-size:13px;
    margin-bottom:20px;
}

.error{
    background:#fee2e2;
    color:#991b1b;
    padding:10px;
    border-radius:12px;
    margin-bottom:12px;
    text-align:center;
    font-size:13px;
}

@media print{
    .header, .no-print{
        display:none !important;
    }

    body{
        background:white;
    }

    .container{
        max-width:100%;
        padding:0;
    }

    .card{
        box-shadow:none;
        border:1px solid #ddd;
    }
}
</style>
</head>

<body>

<div class="header">
    <div class="logout-box no-print">
        <a class="btn logout-btn" href="/logout">خروج</a>
    </div>
    <h1>Avanor Group</h1>
    <p>سیستم مدیریت هوشمند پروژه‌های ساختمانی</p>
</div>

<div class="container">
    {{ content|safe }}
</div>

</body>
</html>
"""


LOGIN_HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<title>ورود به Avanor Group</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');
*{box-sizing:border-box;}
body{
    margin:0;
    font-family:'Vazirmatn', Tahoma, sans-serif;
}
.login-page{
    min-height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
    background:linear-gradient(135deg,#0f172a,#1e3a8a,#2563eb);
    padding:20px;
}
.login-card{
    width:380px;
    background:white;
    border-radius:22px;
    padding:28px;
    box-shadow:0 25px 70px rgba(0,0,0,.25);
}
.login-card h1{
    text-align:center;
    margin:0;
    color:#0f172a;
    font-size:25px;
}
.login-card p{
    text-align:center;
    color:#64748b;
    font-size:13px;
    margin-bottom:20px;
}
input{
    width:100%;
    padding:13px;
    margin:8px 0;
    border:1px solid #d1d5db;
    border-radius:13px;
    font-family:'Vazirmatn', Tahoma, sans-serif;
    font-size:14px;
    outline:none;
    background:#f9fafb;
}
input:focus{
    border-color:#2563eb;
    background:white;
    box-shadow:0 0 0 3px rgba(37,99,235,.12);
}
button{
    width:100%;
    padding:12px;
    border:none;
    border-radius:13px;
    background:#2563eb;
    color:white;
    font-family:'Vazirmatn', Tahoma, sans-serif;
    font-size:15px;
    font-weight:700;
    cursor:pointer;
    margin-top:10px;
}
button:hover{background:#1d4ed8;}
.error{
    background:#fee2e2;
    color:#991b1b;
    padding:10px;
    border-radius:12px;
    margin-bottom:12px;
    text-align:center;
    font-size:13px;
}
.info{
    background:#f1f5f9;
    color:#475569;
    padding:10px;
    border-radius:12px;
    margin-top:14px;
    text-align:center;
    font-size:12px;
    line-height:2;
}
</style>
</head>
<body>
<div class="login-page">
    <div class="login-card">
        <h1>Avanor Group</h1>
        <p>ورود به سیستم مدیریت پروژه</p>

        {{ error|safe }}

        <form method="POST">
            <input type="text" name="username" placeholder="نام کاربری">
            <input type="password" name="password" placeholder="رمز عبور">
            <button type="submit">ورود به سیستم</button>
        </form>

        <div class="info">
            نام کاربری پیش‌فرض: admin<br>
            رمز پیش‌فرض: 1234
        </div>
    </div>
</div>
</body>
</html>
"""


def page(content):
    return render_template_string(HTML, content=content)


def money_format(value):
    return f"{int(value):,}"


def clean_number(value):
    if not value:
        return 0
    return int(str(value).replace(",", "").replace("٬", "").strip() or 0)


def date_key(value):
    return value or ""


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("home"))

    error = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("home"))
        else:
            error = '<div class="error">نام کاربری یا رمز عبور اشتباه است.</div>'

    return render_template_string(LOGIN_HTML, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        project_name = request.form.get("project_name")
        project_location = request.form.get("project_location")

        if project_name:
            new_project = Project(
                name=project_name,
                location=project_location or "بدون آدرس"
            )
            db.session.add(new_project)
            db.session.commit()

        return redirect(url_for("home"))

    projects = Project.query.order_by(Project.id.desc()).all()

    project_list = ""

    if projects:
        for p in projects:
            project_list += f"""
            <div class="project-item">
                <div class="project-info">
                    <h3>{p.name}</h3>
                    <p>{p.location}</p>
                </div>
                <a class="btn" href="/project/{p.id}">ورود به پروژه</a>
            </div>
            """
    else:
        project_list = "<p>هنوز هیچ پروژه‌ای ایجاد نشده است.</p>"

    content = f"""
    <div class="card">
        <h2>انتخاب پروژه</h2>
        <p>برای شروع، پروژه جدید بساز یا وارد یکی از پروژه‌های ثبت‌شده شو.</p>
        <button class="btn" onclick="toggleProjectForm()">ایجاد پروژه جدید</button>
    </div>

    <div class="card" id="projectForm" style="display:none;">
        <h3>فرم ایجاد پروژه جدید</h3>
        <form method="POST">
            <input type="text" name="project_name" placeholder="نام پروژه">
            <input type="text" name="project_location" placeholder="آدرس / موقعیت پروژه">
            <button class="btn" type="submit">ثبت پروژه</button>
        </form>
    </div>

    <div class="card">
        <h2>لیست پروژه‌ها</h2>
        {project_list}
    </div>

    <script>
    function toggleProjectForm(){{
        var form = document.getElementById("projectForm");
        form.style.display = form.style.display === "none" ? "block" : "none";
    }}
    </script>
    """

    return page(content)


@app.route("/project/<int:project_id>")
@login_required
def project_dashboard(project_id):
    project = Project.query.get(project_id)

    if not project:
        return page("<h2>پروژه پیدا نشد</h2>")

    content = f"""
    <div class="card">
        <h2>{project.name}</h2>
        <p>{project.location}</p>
    </div>

    <div class="menu">
        <a href="/project/{project_id}/contractors">پیمانکاران</a>
        <a href="#">انبارداری</a>
        <a href="#">کارهای روزمره</a>
        <a href="#">گزارشات</a>
    </div>

    <br>
    <a class="btn back" href="/">بازگشت به لیست پروژه‌ها</a>
    """

    return page(content)


@app.route("/project/<int:project_id>/contractors", methods=["GET", "POST"])
@login_required
def project_contractors(project_id):
    project = Project.query.get(project_id)

    if not project:
        return page("<h2>پروژه پیدا نشد</h2>")

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        job = request.form.get("job")

        if name and phone and job:
            new_contractor = Contractor(
                project_id=project_id,
                name=name,
                phone=phone,
                job=job
            )
            db.session.add(new_contractor)
            db.session.commit()

        return redirect(url_for("project_contractors", project_id=project_id))

    contractors_list = Contractor.query.filter_by(project_id=project_id).order_by(Contractor.id.desc()).all()

    rows = ""

    for c in contractors_list:
        rows += f"""
        <tr>
            <td>{c.job}</td>
            <td>{c.name}</td>
            <td>{c.phone}</td>
            <td><a class="btn" href="/project/{project_id}/contractor/{c.id}">ورود</a></td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="4">هنوز پیمانکاری ثبت نشده است</td>
        </tr>
        """

    content = f"""
    <div class="card">
        <h2>پیمانکاران پروژه: {project.name}</h2>
        <button class="btn" onclick="toggleContractorForm()">ایجاد پیمانکار جدید</button>
    </div>

    <div class="card" id="contractorForm" style="display:none;">
        <h3>فرم ایجاد پیمانکار جدید</h3>
        <form method="POST">
            <input type="text" name="job" placeholder="تخصص">
            <input type="text" name="name" placeholder="نام پیمانکار">
            <input type="text" name="phone" placeholder="شماره تماس">
            <button class="btn" type="submit">ثبت پیمانکار</button>
        </form>
    </div>

    <div class="card">
        <h3>لیست پیمانکاران</h3>
        <table>
            <tr>
                <th>تخصص</th>
                <th>نام پیمانکار</th>
                <th>شماره تماس</th>
                <th>ورود</th>
            </tr>
            {rows}
        </table>
    </div>

    <a class="btn back" href="/project/{project_id}">بازگشت به پنل پروژه</a>

    <script>
    function toggleContractorForm(){{
        var form = document.getElementById("contractorForm");
        form.style.display = form.style.display === "none" ? "block" : "none";
    }}
    </script>
    """

    return page(content)


@app.route("/project/<int:project_id>/contractor/<int:contractor_id>")
@login_required
def contractor_page(project_id, contractor_id):
    project = Project.query.get(project_id)
    contractor = Contractor.query.filter_by(id=contractor_id, project_id=project_id).first()

    if not project or not contractor:
        return page("<h2>پیمانکار پیدا نشد</h2>")

    content = f"""
    <div class="card">
        <h1 style="color:#0f172a;font-weight:800;">{project.name}</h1>
        <h2>{contractor.job} - {contractor.name}</h2>
        <p>شماره تماس: {contractor.phone}</p>
    </div>

    <div class="card option-list">
        <a href="/project/{project_id}/contractor/{contractor_id}/contract">قرارداد</a>
        <a href="/project/{project_id}/contractor/{contractor_id}/finance">مالی</a>
        <a href="/project/{project_id}/contractor/{contractor_id}/statement">صورت وضعیت</a>
    </div>

    <a class="btn back" href="/project/{project_id}/contractors">بازگشت به پیمانکاران</a>
    """

    return page(content)


@app.route("/project/<int:project_id>/contractor/<int:contractor_id>/contract", methods=["GET", "POST"])
@login_required
def contractor_contract(project_id, contractor_id):
    project = Project.query.get(project_id)
    contractor = Contractor.query.filter_by(id=contractor_id, project_id=project_id).first()

    if not project or not contractor:
        return page("<h2>پیمانکار پیدا نشد</h2>")

    if request.method == "POST":
        file = request.files.get("contract_image")

        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            contractor.contract_image = filename
            db.session.commit()

        return redirect(url_for("contractor_contract", project_id=project_id, contractor_id=contractor_id))

    if contractor.contract_image:
        image_html = f"""
        <h3>عکس قرارداد ثبت‌شده</h3>
        <img class="contract-img" src="/static/uploads/{contractor.contract_image}">
        """
    else:
        image_html = "<p>هنوز عکس قراردادی ثبت نشده است.</p>"

    content = f"""
    <div class="card">
        <h1 style="color:#0f172a;font-weight:800;">{project.name}</h1>
        <h2>{contractor.job} - {contractor.name}</h2>
    </div>

    <div class="card">
        <h2>قرارداد</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="contract_image" accept="image/*">
            <button class="btn" type="submit">ثبت قرارداد</button>
        </form>
        {image_html}
    </div>

    <a class="btn back" href="/project/{project_id}/contractor/{contractor_id}">بازگشت به صفحه پیمانکار</a>
    """

    return page(content)


@app.route("/project/<int:project_id>/contractor/<int:contractor_id>/finance", methods=["GET", "POST"])
@login_required
def contractor_finance(project_id, contractor_id):
    project = Project.query.get(project_id)
    contractor = Contractor.query.filter_by(id=contractor_id, project_id=project_id).first()

    if not project or not contractor:
        return page("<h2>پیمانکار پیدا نشد</h2>")

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_activity":
            meterage = clean_number(request.form.get("meterage"))
            unit_price = clean_number(request.form.get("unit_price"))

            new_activity = Activity(
                contractor_id=contractor_id,
                date=request.form.get("date"),
                description=request.form.get("description"),
                meterage=meterage,
                unit_price=unit_price,
                total_price=meterage * unit_price
            )
            db.session.add(new_activity)
            db.session.commit()

        elif action == "delete_activity":
            selected_ids = [int(x) for x in request.form.getlist("selected_activity")]

            for row_id in selected_ids:
                activity = Activity.query.filter_by(id=row_id, contractor_id=contractor_id).first()
                if activity:
                    db.session.delete(activity)

            db.session.commit()

        elif action == "edit_activity":
            row_id = int(request.form.get("edit_activity_id"))
            activity = Activity.query.filter_by(id=row_id, contractor_id=contractor_id).first()

            if activity:
                meterage = clean_number(request.form.get("edit_meterage"))
                unit_price = clean_number(request.form.get("edit_unit_price"))

                activity.date = request.form.get("edit_date")
                activity.description = request.form.get("edit_description")
                activity.meterage = meterage
                activity.unit_price = unit_price
                activity.total_price = meterage * unit_price

                db.session.commit()

        elif action == "add_payment":
            amount = clean_number(request.form.get("payment_amount"))

            new_payment = Payment(
                contractor_id=contractor_id,
                date=request.form.get("payment_date"),
                description=request.form.get("payment_description"),
                amount=amount
            )
            db.session.add(new_payment)
            db.session.commit()

        elif action == "delete_payment":
            selected_ids = [int(x) for x in request.form.getlist("selected_payment")]

            for row_id in selected_ids:
                payment = Payment.query.filter_by(id=row_id, contractor_id=contractor_id).first()
                if payment:
                    db.session.delete(payment)

            db.session.commit()

        elif action == "edit_payment":
            row_id = int(request.form.get("edit_payment_id"))
            payment = Payment.query.filter_by(id=row_id, contractor_id=contractor_id).first()

            if payment:
                amount = clean_number(request.form.get("edit_payment_amount"))

                payment.date = request.form.get("edit_payment_date")
                payment.description = request.form.get("edit_payment_description")
                payment.amount = amount

                db.session.commit()

        return redirect(url_for("contractor_finance", project_id=project_id, contractor_id=contractor_id))

    finance_rows = Activity.query.filter_by(contractor_id=contractor_id).order_by(Activity.date.asc()).all()
    payment_rows_data = Payment.query.filter_by(contractor_id=contractor_id).order_by(Payment.date.asc()).all()

    activity_rows = ""

    for item in finance_rows:
        activity_rows += f"""
        <tr
            data-id="{item.id}"
            data-date="{item.date}"
            data-description="{item.description}"
            data-meterage="{item.meterage}"
            data-unitprice="{item.unit_price}"
        >
            <td><input class="checkbox-small activity-check" type="checkbox" name="selected_activity" value="{item.id}"></td>
            <td>{item.date}</td>
            <td>{item.description}</td>
            <td>{money_format(item.meterage)}</td>
            <td>{money_format(item.unit_price)}</td>
            <td>{money_format(item.total_price)}</td>
        </tr>
        """

    if not activity_rows:
        activity_rows = """
        <tr>
            <td colspan="6">هنوز فعالیتی ثبت نشده است</td>
        </tr>
        """

    payment_rows = ""

    for item in payment_rows_data:
        payment_rows += f"""
        <tr
            data-id="{item.id}"
            data-date="{item.date}"
            data-description="{item.description}"
            data-amount="{item.amount}"
        >
            <td><input class="checkbox-small payment-check" type="checkbox" name="selected_payment" value="{item.id}"></td>
            <td>{item.date}</td>
            <td>{item.description}</td>
            <td>{money_format(item.amount)}</td>
        </tr>
        """

    if not payment_rows:
        payment_rows = """
        <tr>
            <td colspan="4">هنوز پرداختی ثبت نشده است</td>
        </tr>
        """

    content = f"""
    <div class="card">
        <h1 style="color:#0f172a;font-weight:800;">{project.name}</h1>
        <h2>{contractor.job} - {contractor.name}</h2>
    </div>

    <div class="card">
        <h2>فعالیت پیمانکار</h2>

        <h3>ثبت فعالیت جدید</h3>

        <form method="POST">
            <input type="hidden" name="action" value="add_activity">

            <div class="form-grid">
                <div>
                    <input type="text" name="date" placeholder="مثال: 1403/03/28" pattern="[0-9]{{4}}/[0-9]{{2}}/[0-9]{{2}}" title="تاریخ را به صورت شمسی وارد کنید. مثال: 1403/03/28">
                    <div class="hint">فرمت تاریخ شمسی: 1403/03/28</div>
                </div>

                <input type="text" name="description" placeholder="شرح فعالیت">
                <input type="text" name="meterage" class="number-format" placeholder="متراژ">

                <div>
                    <input type="text" name="unit_price" class="number-format" placeholder="فی ریال">
                    <div class="hint">اعداد هنگام تایپ سه‌رقمی جدا می‌شوند.</div>
                </div>
            </div>

            <button class="btn" type="submit">ثبت فعالیت</button>
        </form>

        <hr style="border:none;border-top:1px solid #e5e7eb;margin:22px 0;">

        <h3>وضعیت فعالیت پیمانکار</h3>

        <form method="POST" id="activityForm" onsubmit="return confirmDeleteActivity();">
            <input type="hidden" name="action" value="delete_activity">

            <table>
                <tr>
                    <th>تیک زدن</th>
                    <th>تاریخ</th>
                    <th>شرح فعالیت</th>
                    <th>متراژ</th>
                    <th>فی ریال</th>
                    <th>مبلغ کل ریال</th>
                </tr>
                {activity_rows}
            </table>

            <div class="actions">
                <button class="btn delete-btn" type="submit">حذف</button>
                <button class="btn edit-btn" type="button" onclick="openActivityEdit()">ویرایش</button>
            </div>
        </form>

        <div class="edit-box" id="activityEditBox">
            <h3>ویرایش فعالیت انتخاب‌شده</h3>

            <form method="POST" onsubmit="return confirm('آیا از ثبت ویرایش مطمئن هستید؟');">
                <input type="hidden" name="action" value="edit_activity">
                <input type="hidden" name="edit_activity_id" id="edit_activity_id">

                <div class="form-grid">
                    <input type="text" name="edit_date" id="edit_activity_date" placeholder="تاریخ">
                    <input type="text" name="edit_description" id="edit_activity_description" placeholder="شرح فعالیت">
                    <input type="text" name="edit_meterage" id="edit_activity_meterage" class="number-format" placeholder="متراژ">
                    <input type="text" name="edit_unit_price" id="edit_activity_unit_price" class="number-format" placeholder="فی ریال">
                </div>

                <button class="btn edit-btn" type="submit">ثبت ویرایش</button>
            </form>
        </div>
    </div>

    <div class="card">
        <h2>پرداختی های پیمانکار</h2>

        <h3>ثبت پرداخت جدید</h3>

        <form method="POST">
            <input type="hidden" name="action" value="add_payment">

            <div class="form-grid">
                <div>
                    <input type="text" name="payment_date" placeholder="مثال: 1403/03/28" pattern="[0-9]{{4}}/[0-9]{{2}}/[0-9]{{2}}" title="تاریخ را به صورت شمسی وارد کنید. مثال: 1403/03/28">
                    <div class="hint">فرمت تاریخ شمسی: 1403/03/28</div>
                </div>

                <input type="text" name="payment_description" placeholder="شرح پرداختی">

                <div>
                    <input type="text" name="payment_amount" class="number-format" placeholder="مبلغ پرداختی به ریال">
                    <div class="hint">اعداد هنگام تایپ سه‌رقمی جدا می‌شوند.</div>
                </div>
            </div>

            <button class="btn" type="submit">ثبت پرداخت</button>
        </form>

        <hr style="border:none;border-top:1px solid #e5e7eb;margin:22px 0;">

        <h3>جدول پرداختی ها به پیمانکار</h3>

        <form method="POST" id="paymentForm" onsubmit="return confirmDeletePayment();">
            <input type="hidden" name="action" value="delete_payment">

            <table>
                <tr>
                    <th>تیک زدن</th>
                    <th>تاریخ</th>
                    <th>شرح پرداختی</th>
                    <th>مبلغ پرداختی ریال</th>
                </tr>
                {payment_rows}
            </table>

            <div class="actions">
                <button class="btn delete-btn" type="submit">حذف</button>
                <button class="btn edit-btn" type="button" onclick="openPaymentEdit()">ویرایش</button>
            </div>
        </form>

        <div class="edit-box" id="paymentEditBox">
            <h3>ویرایش پرداخت انتخاب‌شده</h3>

            <form method="POST" onsubmit="return confirm('آیا از ثبت ویرایش مطمئن هستید؟');">
                <input type="hidden" name="action" value="edit_payment">
                <input type="hidden" name="edit_payment_id" id="edit_payment_id">

                <div class="form-grid">
                    <input type="text" name="edit_payment_date" id="edit_payment_date" placeholder="تاریخ">
                    <input type="text" name="edit_payment_description" id="edit_payment_description" placeholder="شرح پرداختی">
                    <input type="text" name="edit_payment_amount" id="edit_payment_amount" class="number-format" placeholder="مبلغ پرداختی ریال">
                </div>

                <button class="btn edit-btn" type="submit">ثبت ویرایش</button>
            </form>
        </div>
    </div>

    <a class="btn back" href="/project/{project_id}/contractor/{contractor_id}">بازگشت به صفحه پیمانکار</a>

    <script>
    function formatNumber(value){{
        value = value.replace(/,/g, '');
        value = value.replace(/[^0-9]/g, '');
        return value.replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ',');
    }}

    document.querySelectorAll('.number-format').forEach(function(input){{
        input.addEventListener('input', function(){{
            this.value = formatNumber(this.value);
        }});
    }});

    function confirmDeleteActivity(){{
        var checked = document.querySelectorAll('.activity-check:checked');

        if(checked.length === 0){{
            alert("لطفاً حداقل یک فعالیت را انتخاب کنید.");
            return false;
        }}

        return confirm("آیا از حذف فعالیت انتخاب شده مطمئن هستید؟");
    }}

    function confirmDeletePayment(){{
        var checked = document.querySelectorAll('.payment-check:checked');

        if(checked.length === 0){{
            alert("لطفاً حداقل یک پرداختی را انتخاب کنید.");
            return false;
        }}

        return confirm("آیا از حذف پرداختی انتخاب شده مطمئن هستید؟");
    }}

    function openActivityEdit(){{
        var checked = document.querySelectorAll('.activity-check:checked');

        if(checked.length !== 1){{
            alert("برای ویرایش فقط یک فعالیت را انتخاب کنید.");
            return;
        }}

        var row = checked[0].closest('tr');

        document.getElementById("edit_activity_id").value = row.dataset.id;
        document.getElementById("edit_activity_date").value = row.dataset.date;
        document.getElementById("edit_activity_description").value = row.dataset.description;
        document.getElementById("edit_activity_meterage").value = formatNumber(row.dataset.meterage);
        document.getElementById("edit_activity_unit_price").value = formatNumber(row.dataset.unitprice);

        document.getElementById("activityEditBox").style.display = "block";
    }}

    function openPaymentEdit(){{
        var checked = document.querySelectorAll('.payment-check:checked');

        if(checked.length !== 1){{
            alert("برای ویرایش فقط یک پرداختی را انتخاب کنید.");
            return;
        }}

        var row = checked[0].closest('tr');

        document.getElementById("edit_payment_id").value = row.dataset.id;
        document.getElementById("edit_payment_date").value = row.dataset.date;
        document.getElementById("edit_payment_description").value = row.dataset.description;
        document.getElementById("edit_payment_amount").value = formatNumber(row.dataset.amount);

        document.getElementById("paymentEditBox").style.display = "block";
    }}
    </script>
    """

    return page(content)


@app.route("/project/<int:project_id>/contractor/<int:contractor_id>/statement")
@login_required
def contractor_statement(project_id, contractor_id):
    project = Project.query.get(project_id)
    contractor = Contractor.query.filter_by(id=contractor_id, project_id=project_id).first()

    if not project or not contractor:
        return page("<h2>پیمانکار پیدا نشد</h2>")

    finance_rows = Activity.query.filter_by(contractor_id=contractor_id).all()
    payment_rows = Payment.query.filter_by(contractor_id=contractor_id).all()

    statement_items = []

    for row in finance_rows:
        statement_items.append({
            "date": row.date,
            "description": row.description,
            "credit": row.total_price,
            "debit": 0
        })

    for row in payment_rows:
        statement_items.append({
            "date": row.date,
            "description": row.description,
            "credit": 0,
            "debit": row.amount
        })

    statement_items = sorted(statement_items, key=lambda x: date_key(x["date"]))

    rows = ""
    total_credit = 0
    total_debit = 0
    balance = 0
    row_number = 1

    for item in statement_items:
        total_credit += item["credit"]
        total_debit += item["debit"]
        balance += item["credit"] - item["debit"]

        rows += f"""
        <tr>
            <td>{row_number}</td>
            <td>{item['date']}</td>
            <td>{item['description']}</td>
            <td class="debit">{money_format(item['debit']) if item['debit'] else "-"}</td>
            <td class="credit">{money_format(item['credit']) if item['credit'] else "-"}</td>
            <td>{money_format(balance)}</td>
        </tr>
        """

        row_number += 1

    if not rows:
        rows = """
        <tr>
            <td colspan="6">هنوز اطلاعاتی برای صورت وضعیت ثبت نشده است</td>
        </tr>
        """

    content = f"""
    <div class="card">
        <h1 style="color:#0f172a;font-weight:800;">{project.name}</h1>
        <h2>{contractor.job} - {contractor.name}</h2>
    </div>

    <div class="card">
        <div class="actions no-print">
            <button class="btn print-btn" onclick="window.print()">چاپ</button>
        </div>

        <h2>صورت وضعیت پیمانکار</h2>

        <table>
            <tr>
                <th>ردیف</th>
                <th>تاریخ</th>
                <th>شرح</th>
                <th>بدهکار ریال</th>
                <th>بستانکار ریال</th>
                <th>مانده حساب</th>
            </tr>

            {rows}

            <tr class="total-row">
                <td colspan="3">جمع</td>
                <td class="debit">{money_format(total_debit)} ریال</td>
                <td class="credit">{money_format(total_credit)} ریال</td>
                <td>{money_format(balance)} ریال</td>
            </tr>
        </table>
    </div>

    <a class="btn back no-print" href="/project/{project_id}/contractor/{contractor_id}">بازگشت به صفحه پیمانکار</a>
    """

    return page(content)


with app.app_context():
    db.create_all()

    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            password_hash=generate_password_hash("1234"),
            role="admin"
        )
        db.session.add(admin_user)
        db.session.commit()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
