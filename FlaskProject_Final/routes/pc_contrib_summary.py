# routes/pc_contrib_summary.py
from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func, case
from models import db, Result, ProgramOutcome, CourseProgramOutcome

bp = Blueprint("pc_contrib", __name__, url_prefix="/pc-contrib")

@bp.route("/")
@login_required
def summary():
    # ----- Final notu -----
    final_col = func.max(
        case((Result.exam_name == "Final", Result.score), else_=None)
    ).label("final_score")

    # ----- 1. Öğrenci-ders tablosu (vize/final ort, final) -----
    sub = (
        db.session.query(
            Result.student_id,
            Result.course_id,
            func.count(Result.exam_name).label("cnt"),
            func.avg(Result.score).label("avg_score"),
            final_col
        )
        .filter(Result.exam_name.in_(["Vize", "Final"]))
        .group_by(Result.student_id, Result.course_id)
    ).subquery()

    # Geçilen dersler
    passed_sub = (
        db.session.query(
            sub.c.student_id,
            sub.c.course_id
        )
        .filter(
            (sub.c.cnt == 2),                       # vize + final var
            (sub.c.avg_score >= 45),
            (sub.c.final_score >= 45)
        )
    ).subquery()

    # ----- PÇ → ders kümesi sözlüğü -----
    pc_courses = {}
    for rel in CourseProgramOutcome.query.all():
        pc_courses.setdefault(rel.pc_id, set()).add(rel.course_id)

    pcs = ProgramOutcome.query.order_by(ProgramOutcome.code).all()

    # ----- Potansiyel / Gerçek katkı hesapları -----
    summary = []
    for pc in pcs:
        courses = pc_courses.get(pc.id, set())
        if not courses:
            summary.append({"pc": pc, "potential": 0, "achieved": 0})
            continue

        # POTANSİYEL → öğrencinin dersi alması yeterli
        potential = (
            db.session.query(sub.c.student_id, sub.c.course_id)
            .filter(sub.c.course_id.in_(courses))
            .distinct()
            .count()
        )

        # GERÇEK → aynı öğrenci-ders çifti passed_sub’da
        achieved = (
            db.session.query(passed_sub.c.student_id, passed_sub.c.course_id)
            .filter(passed_sub.c.course_id.in_(courses))
            .distinct()
            .count()
        )

        summary.append({
            "pc": pc,
            "potential": potential,
            "achieved": achieved
        })

    return render_template("pc_contrib_summary.html", summary=summary)
