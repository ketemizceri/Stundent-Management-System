from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func
from models import db, Course, Result, CourseProgramOutcome

bp = Blueprint("courses", __name__, url_prefix="/courses")

@bp.route("/")
@login_required
def list_courses():
    year_param = request.args.get("year", "all")   # 'all', '1', '2', ...
    q          = request.args.get("q", "").strip()

    query = Course.query

    # ----- Sınıf filtresi -----
    if year_param and year_param != "all":
        try:
            query = query.filter_by(year=int(year_param))
        except ValueError:
            # Kullanıcı URL'ye hatalı değer yazarsa göz ardı et
            pass

    # ----- Arama filtresi -----
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            func.lower(Course.code).like(like) |
            func.lower(Course.name).like(like) |
            func.lower(Course.lecturer).like(like)
        )

    courses = query.order_by(Course.code).all()
    return render_template("courses.html", courses=courses,
                           year=year_param, q=q)


# ────────────────── DERS EKLE ──────────────────
@bp.route("/add", methods=["POST"])
@login_required
def add_course():
    # (değişmedi)
    code = request.form["code"].strip()
    name = request.form["name"].strip()
    credit = request.form["credit"].strip()
    lecturer = request.form["lecturer"].strip()
    year = request.form["year"].strip()

    if not code or not name:
        flash("Boş alan bıraktın 🤨")
    else:
        db.session.add(Course(
            code=code, name=name, credit=credit,
            lecturer=lecturer, year=int(year)
        ))
        db.session.commit()
        flash("Ders eklendi ✅")
    return redirect(url_for("courses.list_courses"))

# ────────────────── DERS SİL ──────────────────
@bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_course(id):
    course = Course.query.get_or_404(id)

    if request.form.get("confirm") != "yes":
        flash("Ders silinmedi. Onay gerekiyor ⚠️")
        return redirect(url_for("courses.list_courses"))

    # ilişkili kayıtları temizle
    Result.query.filter_by(course_id=course.id).delete()
    CourseProgramOutcome.query.filter_by(course_id=course.id).delete()

    db.session.delete(course)
    db.session.commit()
    flash("Ders ve ilişkili notlar silindi 🗑️")
    return redirect(url_for("courses.list_courses"))
