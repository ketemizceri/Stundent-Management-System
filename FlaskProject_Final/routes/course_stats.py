# routes/course_stats.py
from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from models import db, Course, Result, Student

bp = Blueprint("course_stats", __name__, url_prefix="/course-stats")

@bp.route("/")
@login_required
def summary():
    # ➊  Tüm dersleri çek
    courses = Course.query.order_by(Course.code).all()

    stats = []  # her ders için istatistik listesi
    for crs in courses:
        # ➋  Dersi alan öğrencilerin vize+final notlarını çek
        #    sadece vize+final ikisi de girilmiş öğrenciler hesaba katılır
        sub = (
            db.session.query(
                Result.student_id,
                func.avg(Result.score).label("avg_score")
            )
            .filter(Result.course_id == crs.id,
                    Result.exam_name.in_(["Vize", "Final"]))
            .group_by(Result.student_id)
            .having(func.count(Result.exam_name) == 2)  # vize+final ikisi de var
            .subquery()
        )

        # sınıf ortalaması
        course_avg = db.session.query(func.avg(sub.c.avg_score)).scalar()
        course_avg = round(course_avg or 0, 2)

        # Geçen / kalan sayıları
        passed = failed = 0
        for row in db.session.query(sub).all():
            if row.avg_score >= course_avg:
                passed += 1
            else:
                failed += 1

        stats.append({
            "course": crs,
            "avg": course_avg,
            "total": passed + failed,
            "passed": passed,
            "failed": failed
        })

    return render_template("course_stats.html", stats=stats)
