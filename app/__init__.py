from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.contact import contact_bp


from dotenv import load_dotenv
import os

# Import database
from app.models import db

# Extensions
migrate = Migrate()
jwt = JWTManager()


def create_app():
    load_dotenv()

    app = Flask(
        __name__,
        static_folder="../frontend/dist",     # ✅ update if needed
        static_url_path="/"
    )

    # ========= CONFIG =========
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    # Upload folder
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ========= CORS =========
    allowed_origins = os.getenv(
        'ALLOWED_ORIGINS',
        'http://localhost:3000,http://localhost:5173,http://localhost:50239'
    ).split(',')

    CORS(
        app,
        supports_credentials=True,
        origins=allowed_origins,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # ========= Init extensions =========
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # ========= Blueprint register =========
    from app.auth import auth_bp
    from app.routes import article_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(article_bp, url_prefix="/api/articles")
    app.register_blueprint(contact_bp, url_prefix="/api")


    # ========= Serve uploaded media =========
    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # ========= React support =========
    @app.route("/")
    def serve_react_root():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:path>")
    def serve_react_routes(path):
        file_path = os.path.join(app.static_folder, path)

        # If file exists serve it
        if os.path.exists(file_path):
            return send_from_directory(app.static_folder, path)

        # Else serve index.html -> React Router fallback
        return send_from_directory(app.static_folder, "index.html")

    return app
