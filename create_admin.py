from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    if not User.query.filter_by(username='admin').first():
        admin = User(
            nombre='Admin',
            apellido='Principal',
            ci='9999999',
            direccion='Oficina central',
            telefono='70000000',
            correo='admin@unpesito.com',
            username='admin',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuario admin creado correctamente.")
    else:
        print("⚠️ Ya existe un usuario admin.")
