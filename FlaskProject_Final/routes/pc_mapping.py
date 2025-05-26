from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Course, ProgramOutcome, CourseProgramOutcome

bp = Blueprint("pc_mapping", __name__, url_prefix="/pc-map")

@bp.route("/", methods=["GET", "POST"])
@login_required
def map_pc():
    courses = Course.query.all()
    pcs = ProgramOutcome.query.all()

    if request.method == "POST":
        course_id = int(request.form["course_id"])
        # eski eşlemeleri sil
        CourseProgramOutcome.query.filter_by(course_id=course_id).delete()

        for pc in pcs:
            val = int(request.form.get(f"pc_{pc.id}", 0))
            if val > 0:
                db.session.add(CourseProgramOutcome(
                    course_id=course_id,
                    pc_id=pc.id,
                    contribution=val
                ))
        db.session.commit()
        flash("Katkı eşlemesi kaydedildi ✅")
        return redirect(url_for("pc_mapping.map_pc"))

    return render_template("pc_map.html", courses=courses, pcs=pcs)
