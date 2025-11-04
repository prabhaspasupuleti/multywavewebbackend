from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Import your blueprints and database
from app.models import db
from app.contact import contact_bp

# Extensions
migrate = Migrate()
jwt = JWTManager()


def create_app():
    load_dotenv()  # ✅ Load .env for both local and Render

    app = Flask(
        __name__,
        static_folder="../frontend/dist",  # ✅ use correct React build folder
        static_url_path="/"
    )

    # ========= CONFIG =========
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'supersecretkey')

    # Handle Render PostgreSQL URLs (convert old scheme)
    if app.config['SQLALCHEMY_DATABASE_URI'] and app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

    # ========= Uploads =========
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ========= CORS =========
    allowed_origins = os.getenv(
        'ALLOWED_ORIGINS',
        'http://localhost:3000,http://localhost:5173,https://yourfrontendurl.com'
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

    # ========= Blueprints =========
    from app.auth import auth_bp
    from app.routes import article_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(article_bp, url_prefix="/api/articles")
    app.register_blueprint(contact_bp, url_prefix="/api")

    # ========= Serve uploaded media =========
    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # ========= React (static build serving) =========
    @app.route("/")
    def serve_react_root():
        index_path = os.path.join(app.static_folder, "index.html")
        return send_from_directory(app.static_folder, "index.html") if os.path.exists(index_path) else "Frontend not built yet."

    @app.route("/<path:path>")
    def serve_react_routes(path):
        file_path = os.path.join(app.static_folder, path)
        if os.path.exists(file_path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    return app
