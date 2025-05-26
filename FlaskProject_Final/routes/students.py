from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Student, Course, Result
from sqlalchemy import func
from flask_login import login_required

bp = Blueprint("students", __name__, url_prefix="/students")

# Öğrenci listesi
# Öğrenci listesi + arama
@bp.route("/")
@login_required
def list_students():
    q = request.args.get("q", "").strip()           # ?q=Ali

    query = Student.query
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            func.lower(Student.name.like(like))     |        # isim
            func.lower(Student.surname.like(like))  |        # soyisim
            func.lower(Student.number.like(like))            # numara
        )

    students = query.order_by(Student.number.asc()).all()
    return render_template("students.html", students=students, q=q)


# Yeni öğrenci ekleme
@bp.route("/add", methods=["POST"])
@login_required
def add_student():
    number       = request.form["number"].strip()
    name         = request.form["name"].strip()
    surname      = request.form["surname"].strip()
    phone_number = request.form["phone_number"].strip()
    grade        = request.form["grade"].strip()

    if not number or not name or not surname or not phone_number:
        flash("Tüm alanları doldurmalısın 🤨")
    elif not number.isdigit():
        flash("Öğrenci numarası sadece sayılardan oluşmalı 🔢")
    elif not phone_number.isdigit():
        flash("Telefon numarası sadece sayılardan oluşmalı ☎️")
    elif Student.query.filter_by(number=number).first():
        flash("Bu öğrenci numarası zaten kayıtlı ❌")
    elif Student.query.filter_by(phone_number=phone_number).first():
        flash("Bu telefon numarası zaten kayıtlı ❌")
    else:
        db.session.add(Student(
            number=number,
            name=name,
            surname=surname,
            phone_number=int(phone_number),
            grade=int(grade)
        ))
        db.session.commit()
        flash("Öğrenci eklendi ✅")

    return redirect(url_for("students.list_students"))

# Öğrenci silme (notlarla birlikte)
@bp.route("/delete/<int:id>")
@login_required
def delete_student(id):
    s = Student.query.get_or_404(id)
    for result in s.results:
        db.session.delete(result)
    db.session.delete(s)
    db.session.commit()
    flash("Öğrenci ve notları silindi 🗑️")
    return redirect(url_for("students.list_students"))

# Öğrenci detay sayfası: bilgi güncelleme + not ekleme
@bp.route("/<int:id>", methods=["GET", "POST"])
@login_required
def view_student(id):
    student = Student.query.get_or_404(id)
    available_courses = Course.query.filter(Course.year <= student.grade).all()
    original_grade = student.grade

    selected_course_id = None
    exam_name = None

    if request.method == "POST":
        if "grade_form" in request.form:
            # NOT GİRİŞİ
            course_id = int(request.form["course_id"])
            exam_name = request.form["exam_name"]
            score     = float(request.form["score"])

            selected_course_id = str(course_id)

            result = Result.query.filter_by(
                student_id=student.id,
                course_id=course_id,
                exam_name=exam_name
            ).first()

            if result:
                result.score = score
                flash("Not güncellendi ✏️")
            else:
                db.session.add(Result(
                    student_id=student.id,
                    course_id=course_id,
                    exam_name=exam_name,
                    score=score
                ))
                flash("Not başarıyla eklendi ✅")

            db.session.commit()

            # 🔁 Burada yeniden not listesini çekiyoruz çünkü yeni not eklendi
            results = Result.query.filter_by(student_id=student.id).join(Course).order_by(Course.code, Result.exam_name).all()

            return render_template(
                "student_detail.html",
                student=student,
                courses=available_courses,
                results=results,
                selected_course_id=selected_course_id,
                exam_name=exam_name
            )

        else:
            # ÖĞRENCİ BİLGİLERİ GÜNCELLEME
            new_grade = int(request.form["grade"].strip())

            if new_grade < student.grade:
                Result.query.filter_by(student_id=student.id).delete()
                flash("Sınıf düşürüldü, tüm notlar silindi 🗑️")

            student.name         = request.form["name"].strip()
            student.surname      = request.form["surname"].strip()
            student.phone_number = int(request.form["phone_number"].strip())
            student.grade        = new_grade

            db.session.commit()
            flash("Öğrenci bilgileri güncellendi ✅")
            return redirect(url_for("students.view_student", id=student.id))

    results = Result.query.filter_by(student_id=student.id).join(Course).order_by(Course.code, Result.exam_name).all()

    return render_template(
        "student_detail.html",
        student=student,
        courses=available_courses,
        results=results,
        selected_course_id=selected_course_id,
        exam_name=exam_name
    )
