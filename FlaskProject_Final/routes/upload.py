from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Student, Course, Result
import pandas as pd

bp = Blueprint("upload", __name__, url_prefix="/upload")

@bp.route("/", methods=["GET", "POST"])
@login_required
def upload_csv():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename.endswith(".csv"):
            flash("Lütfen bir CSV dosyası yükleyin.")
            return redirect(url_for("upload.upload_csv"))

        try:
            df = pd.read_csv(file)
            added, skipped = 0, 0

            for _, row in df.iterrows():
                student = Student.query.filter_by(number=str(row["student_number"])).first()
                course = Course.query.filter_by(code=row["course_code"]).first()

                if not student:
                    skipped += 1
                    continue
                if not course:
                    skipped += 1
                    continue
                if course.year >= student.grade:
                    skipped += 1
                    continue

                # kayıt varsa güncelle, yoksa ekle
                result = Result.query.filter_by(
                    student_id=student.id,
                    course_id=course.id,
                    exam_name=row["exam_name"]
                ).first()

                if result:
                    result.score = float(row["score"])
                else:
                    db.session.add(Result(
                        student_id=student.id,
                        course_id=course.id,
                        exam_name=row["exam_name"],
                        score=float(row["score"])
                    ))
                added += 1

            db.session.commit()
            flash(f"{added} not eklendi/güncellendi. {skipped} kayıt atlandı.")

        except Exception as e:
            flash(f"Hata oluştu: {e}")

        return redirect(url_for("upload.upload_csv"))

    return render_template("upload.html")
