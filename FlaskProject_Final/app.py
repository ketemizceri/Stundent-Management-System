from flask import Flask, render_template
from config import Config
from models import db, Admin
from flask_login import LoginManager
from routes.students import bp as students_bp
from routes.auth import bp as auth_bp
from routes.upload import bp as upload_bp
from routes.courses import bp as courses_bp
from routes.results import bp as results_bp
from routes.pc_mapping import bp as pc_mapping_bp
from routes.view_mapping import bp as view_mapping_bp
from routes.course_stats import bp as course_stats_bp
from routes.pc_contrib_summary import bp as pc_contrib_bp



login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    
    db.init_app(app)

    login_manager.init_app(app)

    # Blueprint kayıtları
    app.register_blueprint(course_stats_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(pc_mapping_bp)
    app.register_blueprint(view_mapping_bp)
    app.register_blueprint(pc_contrib_bp)

    # Geliştirme için tablo oluştur (prod ortamda migrate kullanılmalı)
    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    @app.route("/")
    def index():
        return render_template("index.html", title="Yönetim Paneli")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
