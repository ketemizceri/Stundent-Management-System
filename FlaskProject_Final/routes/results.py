from flask import Blueprint, render_template
from flask_login import login_required
from models import Result, Student, Course, ProgramOutcome, CourseProgramOutcome

bp = Blueprint("results", __name__, url_prefix="/results")

@bp.route("/")
@login_required
def list_results():
    results = Result.query.all()
    return render_template("results.html", results=results)

@bp.route("/outcomes/<int:student_id>", endpoint="student_outcomes")
@login_required
def student_outcomes(student_id):
    student = Student.query.get_or_404(student_id)
    pcs = ProgramOutcome.query.order_by(ProgramOutcome.code).all()

    all_results = Result.query.filter_by(student_id=student_id).all()

    grades = {}
    for r in all_results:
        grades.setdefault(r.course_id, {})[r.exam_name.lower()] = r.score

    graded_course_ids = list(grades.keys())
    all_courses = Course.query.filter(Course.id.in_(graded_course_ids)).order_by(Course.code).all()

    passed_courses = []
    failed_course_ids = []
    for course in all_courses:
        g = grades.get(course.id, {})
        vize = g.get("vize")
        final = g.get("final")
        if vize is not None and final is not None:
            avg = (vize + final) / 2
            if avg >= 45 and final >= 45:
                passed_courses.append(course)
            else:
                failed_course_ids.append(course.id)

    # Öğrencinin katkı eşleşmeleri
    mapping = {course.id: {pc.id: 0 for pc in pcs} for course in passed_courses}
    for rel in CourseProgramOutcome.query.all():
        if rel.course_id in mapping:
            mapping[rel.course_id][rel.pc_id] = rel.contribution

    from collections import defaultdict

    student_scores = defaultdict(int)
    avg_scores_accumulated = defaultdict(float)
    avg_scores_student_count = defaultdict(int)

    # Aktif öğrencinin kendi katkıları
    for course_id, kazanims in mapping.items():
        for pc in pcs:
            kod = pc.code
            puan = kazanims.get(pc.id, 0)
            student_scores[kod] += puan

    # Tüm öğrenciler (aktif dahil) için ortalama katkılar
    all_students = Student.query.all()
    for s in all_students:
        s_results = Result.query.filter_by(student_id=s.id).all()
        g = {}
        for r in s_results:
            g.setdefault(r.course_id, {})[r.exam_name.lower()] = r.score

        graded_ids = list(g.keys())
        s_courses = Course.query.filter(Course.id.in_(graded_ids)).all()

        s_passed = []
        for c in s_courses:
            vize = g.get(c.id, {}).get("vize")
            final = g.get(c.id, {}).get("final")
            if vize is not None and final is not None and final >= 45 and (vize + final) / 2 >= 45:
                s_passed.append(c)

        # Kazanım eşleşmeleri
        s_mapping = {c.id: {pc.id: 0 for pc in pcs} for c in s_passed}
        for rel in CourseProgramOutcome.query.all():
            if rel.course_id in s_mapping:
                s_mapping[rel.course_id][rel.pc_id] = rel.contribution

        # Öğrencinin kazanım toplamları
        s_total_kazanims = defaultdict(int)
        for course_id, kazanims in s_mapping.items():
            for pc in pcs:
                kod = pc.code
                s_total_kazanims[kod] += kazanims.get(pc.id, 0)

        # Ortalamaya ekle
        for kod, toplam_puan in s_total_kazanims.items():
            avg_scores_accumulated[kod] += toplam_puan
            avg_scores_student_count[kod] += 1

    avg_scores_final = {
        kod: round(avg_scores_accumulated[kod] / avg_scores_student_count[kod], 2)
        if avg_scores_student_count[kod] > 0 else 0
        for kod in [pc.code for pc in pcs]
    }

    kazanim_kodlari = [pc.code for pc in pcs]

    return render_template(
        "student_outcomes.html",
        student=student,
        pcs=pcs,
        all_courses=all_courses,
        failed_course_ids=failed_course_ids,
        mapping=mapping,
        student_scores=dict(student_scores),
        avg_scores=dict(avg_scores_final),
        kazanim_kodlari=kazanim_kodlari
    )
