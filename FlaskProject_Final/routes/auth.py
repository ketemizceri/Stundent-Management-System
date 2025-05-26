from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import db, Admin
from werkzeug.security import check_password_hash

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = Admin.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Giriş başarılı!")
            return redirect(url_for("students.list_students"))
        flash("Kullanıcı adı veya şifre hatalı")
    return render_template("login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Çıkış yapıldı")
    return redirect(url_for("auth.login"))
