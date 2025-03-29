# Fichier principal de l'application Flask
from flask import Flask, redirect, url_for
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from models import db
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Initialisation de JWT
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    # Initialisation des extensions
    db.init_app(app)
    jwt.init_app(app)

    @app.context_processor
    def utility_processor():
        def is_authenticated():
            try:
                verify_jwt_in_request()
                return True
            except:
                return False
        return dict(is_authenticated=is_authenticated)

    # Route par défaut
    @app.route('/')
    def index():
        try:
            verify_jwt_in_request()
            return redirect(url_for('auth.profile'))
        except:
            return redirect(url_for('auth.login'))

    # Import et enregistrement des routes
    from routes import auth_bp
    app.register_blueprint(auth_bp)

    # Création des tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
