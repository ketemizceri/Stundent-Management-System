from flask import Blueprint, render_template
from flask_login import login_required
from models import Course, ProgramOutcome, CourseProgramOutcome

bp = Blueprint("view_mapping", __name__, url_prefix="/pc-view")

@bp.route("/")
@login_required
def pc_matrix():
    courses = Course.query.order_by(Course.code).all()
    pcs = ProgramOutcome.query.order_by(ProgramOutcome.code).all()

    # course_id → { pc_id → contribution }
    mapping = {}
    for course in courses:
        mapping[course.id] = {pc.id: 0 for pc in pcs}

    for rel in CourseProgramOutcome.query.all():
        mapping[rel.course_id][rel.pc_id] = rel.contribution

    return render_template("pc_matrix.html", courses=courses, pcs=pcs, mapping=mapping)
