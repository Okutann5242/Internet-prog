from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json,io,os
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Gelistirme_Anahtari'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///talep.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Kullanıcı Modeli
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    talepler = db.relationship('Talep', back_populates='kullanici')
    is_admin = db.Column(db.Boolean, default=False)
    reply = db.Column(db.Text, nullable=True) 

# Talep Modeli
class Talep(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(5000), nullable=False)
    reply = db.Column(db.String(5000), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="Açık")  # Durum (Açık, Çözüldü vb.)
    rating = db.Column(db.Integer, nullable=True)  # Memnuniyet puanı (1-5)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    kullanici = db.relationship('User', back_populates='talepler')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    from datetime import datetime
    simdi = datetime.now()
    bu_ay_talep = Talep.query.filter(
        db.extract("month", Talep.created_at) == simdi.month,
        db.extract("year", Talep.created_at) == simdi.year
    ).count()

    cozulmus_talep = Talep.query.filter_by(status="Çözüldü").count()

    return render_template(
        "index.html",
        bu_ay_talep=bu_ay_talep,
        cozulmus_talep=cozulmus_talep,
        memnuniyet_orani="91%"  # buraya sabit değer verdik
    )

    

from urllib.parse import urlparse, urljoin

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        next_page = request.form.get('next')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Hoşgeldin {user.name}!', 'success')

            if not next_page or not is_safe_url(next_page):
                next_page = url_for('dashboard')
            return redirect(next_page)
        else:
            flash('E-posta veya şifre hatalı!', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            flash('Tüm alanları doldurmalısınız.', 'warning')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Bu e-posta zaten kayıtlı!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Kayıt başarılı, hoş geldiniz!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route("/dashboard")
@login_required
def dashboard():
    user = {
        "name": current_user.name
    }

    # Başlangıç sorgusu: sadece kendi taleplerin
    query = Talep.query.filter_by(kullanici_id=current_user.id)

    # Filtre parametreleri
    priority = request.args.get("priority")
    status = request.args.get("status")   # Yeni eklenen durum filtresi
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Priority filtre uygula
    if priority:
        query = query.filter(Talep.priority == priority)

    # Status filtre uygula
    if status:
        query = query.filter(Talep.status == status)

    # Tarih filtreleri
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Talep.created_at >= start_date_obj)
        except ValueError:
            pass

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            # Gün sonuna ayarla (23:59:59)
            end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
            query = query.filter(Talep.created_at <= end_date_obj)
        except ValueError:
            pass

    # Sonuçları tarih azalan sırada getir
    talepler = query.order_by(Talep.created_at.desc()).all()

    return render_template("dashboard.html", user=user, talepler=talepler)


@app.route('/dashboard/create', methods=['GET', 'POST'])
@login_required
def create_talep():
    if request.method == 'POST':
        priority = request.form.get('priority')
        tags = request.form.get('tags')
        subject = request.form.get('subject')
        description = request.form.get('description')

        yeni_talep = Talep(
            priority=priority,
            tags=tags,
            subject=subject,
            description=description,
            kullanici_id=current_user.id
        )
        db.session.add(yeni_talep)
        db.session.commit()

        flash('Talep başarıyla kaydedildi!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Admin paneli talep listeleme
@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        return "Erişim reddedildi", 403
    talepler = Talep.query.order_by(Talep.created_at.desc()).all()
    return render_template("admin.html", talepler=talepler)

# Admin login
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if user.is_admin:
                login_user(user)
                flash('Admin girişi başarılı!', 'success')
                return redirect(url_for('admin_panel'))
            else:
                flash('Bu kullanıcı admin değil!', 'danger')
        else:
            flash('Geçersiz e-posta veya şifre!', 'danger')

    return render_template('admin-login.html')

# Admin talep yanıtla işlemi
@app.route('/admin/reply-talep', methods=['POST'])
@login_required
def reply_talep():
    if not current_user.is_admin:
        flash("Yetkisiz erişim!", "danger")
        return redirect(url_for('admin_panel'))

    talep_id = request.form.get('talep_id')
    reply = request.form.get('reply')
    status = request.form.get('status')

    talep = Talep.query.get(talep_id)
    if not talep:
        flash("Talep bulunamadı.", "danger")
        return redirect(url_for('admin_panel'))

    talep.reply = reply
    talep.status = status
    db.session.commit()

    flash("Talep başarıyla güncellendi.", "success")
    return redirect(url_for('admin_panel'))

from flask import send_file

@app.route('/admin/export-json')
@login_required
def export_json():
    if not current_user.is_admin:
        return "Erişim reddedildi", 403

    users = User.query.all()
    talepler = Talep.query.all()

    data = {
        "kullanicilar": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_admin": user.is_admin
            } for user in users
        ],
        "talepler": [
            {
                "id": talep.id,
                "subject": talep.subject,
                "description": talep.description,
                "priority": talep.priority,
                "tags": talep.tags,
                "reply": talep.reply,
                "kullanici_id": talep.kullanici_id,
                "created_at": talep.created_at.isoformat(),
                "updated_at": talep.updated_at.isoformat()
            } for talep in talepler
        ]
    }

    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    file_stream = io.BytesIO()
    file_stream.write(json_data.encode('utf-8'))
    file_stream.seek(0)

    return send_file(
        file_stream,
        mimetype='application/json',
        as_attachment=True,
        download_name='veritabani_yedek.json'
    )


@app.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        if not name or not email or not password:
            flash('Tüm alanları doldurun.', 'warning')
            return redirect(url_for('create_admin'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            existing_user.is_admin = True
            db.session.commit()
            login_user(existing_user)
            flash(f"{email} artık admin ve giriş yapıldı!", 'success')
            return redirect(url_for('admin_panel'))
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_admin = User(name=name, email=email, password=hashed_password, is_admin=True)
            db.session.add(new_admin)
            db.session.commit()
            login_user(new_admin)
            flash('Yeni admin oluşturuldu ve giriş yapıldı!', 'success')
            return redirect(url_for('admin_panel'))

    return '''
    <h2>Admin Oluştur</h2>
    <form method="post">
      <input type="text" name="name" placeholder="Ad Soyad"><br>
      <input type="email" name="email" placeholder="Email"><br>
      <input type="password" name="password" placeholder="Şifre"><br>
      <button type="submit">Admin Yap</button>
    </form>
    '''






    

@app.route('/kullanici-panel')
def kullanici_panel():
    return render_template('kullanici-panel.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    talep = Talep.query.get_or_404(id)

    if request.method == 'POST':
        talep.subject = request.form['subject']
        talep.description = request.form['description']
        talep.priority = request.form['priority']
        db.session.commit()
        flash("Talep başarıyla güncellendi", "success")
        return redirect(url_for('dashboard'))

    return render_template('edit.html', talep=talep)


__all__ = ['db', 'User', 'Talep', 'app']

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
