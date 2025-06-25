# app/__init__.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def init_capital_general():
    from app.models.capital_general import CapitalGeneral
    
    capital = CapitalGeneral.query.first()
    if not capital:
        capital = CapitalGeneral(monto=10000000.0)
        db.session.add(capital)
        db.session.commit()
        print("✅ CapitalGeneral inicializado con Bs. 10000000.0")

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    #app.config.from_object('config.Config')
    app.config.from_pyfile('config.py', silent=True)
    app.config['SECRET_KEY'] = 'tu_secreto'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    migrate.init_app(app, db)

    with app.app_context():
        from app.models import User, Loan, LoanType, Transaction
        from app.models.capital_general import CapitalGeneral

        db.create_all()

        # Crear admin automáticamente si no existe
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            from werkzeug.security import generate_password_hash
            admin = User(
                nombre='Admin',
                apellido='Admin',
                ci='00000000',
                direccion='Admin',
                telefono='0000000000',
                correo='admin@example.com',
                username='admin',
                role='admin',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()

        # Inicializar capital general
        init_capital_general()

    # Registrar blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.user_controller import user_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.teller_controller import teller_bp
    from app.controllers.transfer_controller import transfer_bp
    

    app.register_blueprint(transfer_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teller_bp)

    @app.route('/')
    def index():
        return render_template('home.html')

    @app.errorhandler(404)
    def not_found(e):
        return "Página no encontrada", 404

    return app
