# models/__init__.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class Student(db.Model):
    id     = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)
    name   = db.Column(db.String(120), nullable=False)
    surname   = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    
    
    results = db.relationship("Result", backref="student", lazy=True)

    def __repr__(self):
        return f"<Student {self.number} – {self.name} – {self.surname} – {self.phone_number} – {self.grade}>"


class Course(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    credit = db.Column(db.Double, nullable=False)
    lecturer = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer,nullable=False)

    results = db.relationship("Result", backref="course", lazy=True)
   


    def __repr__(self):
        return f"<Course {self.code} – {self.name} – {self.credit} – {self.lecturer} – {self.year}>"
    
class Admin(db.Model,UserMixin):
    id  =   db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Result(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    course_id  = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    exam_name  = db.Column(db.String(50), nullable=False)
    score      = db.Column(db.Float, nullable=False)

class ProgramOutcome(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    code  = db.Column(db.String(10), unique=True, nullable=False) 
    label = db.Column(db.String(255), nullable=False)


class CourseProgramOutcome(db.Model):
    __tablename__ = "course_pc"
    __table_args__ = (
        db.PrimaryKeyConstraint('course_id', 'pc_id', name='pk_course_pc'),
    )

    course_id = db.Column(db.Integer, db.ForeignKey("course.id", ondelete="CASCADE"), nullable=False)
    pc_id     = db.Column(db.Integer, db.ForeignKey("program_outcome.id", ondelete="CASCADE"), nullable=False)
    contribution = db.Column(db.Integer, nullable=False)

    course = db.relationship("Course", backref="pc_relations")
    pc     = db.relationship("ProgramOutcome", backref="course_relations")


