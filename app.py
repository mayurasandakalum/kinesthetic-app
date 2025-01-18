from flask import Flask, render_template
from config import Config
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from quiz.models import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "login"

    from quiz.routes import quiz_blueprint

    app.register_blueprint(quiz_blueprint)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error_404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("error_500.html"), 500

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run()
