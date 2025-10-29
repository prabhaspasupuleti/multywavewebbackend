from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from app.models import NewsArticle, db
import os

article_bp = Blueprint('article', __name__)

# Allowed extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}


# --- Helper Functions ---
def allowed_file(filename, allowed_exts):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts


def save_file(file, subfolder):
    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return f"/uploads/{subfolder}/{filename}"


# --- Routes ---
@article_bp.route('/', methods=['GET'])
def get_articles():
    articles = NewsArticle.query.order_by(NewsArticle.created_at.desc()).all()
    return jsonify([
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,  # ✅ fixed
            "image_url": a.image_path,
            "pdf_url": a.pdf_path,
            "created_at": a.created_at.isoformat() if a.created_at else None
        } for a in articles
    ]), 200


@article_bp.route('/', methods=['POST'])
@jwt_required()
def create_article():
    title = request.form.get('title')
    content = request.form.get('content')  # ✅ get from frontend
    image = request.files.get('image')
    pdf = request.files.get('pdf')

    if not title:
        return jsonify({"msg": "Title is required"}), 400
    if not content:
        return jsonify({"msg": "Content is required"}), 400

    if image and not allowed_file(image.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({"msg": "Invalid image format"}), 400
    if pdf and not allowed_file(pdf.filename, ALLOWED_PDF_EXTENSIONS):
        return jsonify({"msg": "Invalid PDF format"}), 400

    image_path = save_file(image, 'images') if image else None
    pdf_path = save_file(pdf, 'pdfs') if pdf else None

    article = NewsArticle(
        title=title,
        content=content,  # ✅ correct field name
        image_path=image_path,
        pdf_path=pdf_path
    )

    db.session.add(article)
    db.session.commit()

    return jsonify({
        "msg": "Article created successfully",
        "article": {
            "id": article.id,
            "title": article.title,
            "content": article.content,
            "image_url": article.image_path,
            "pdf_url": article.pdf_path,
            "created_at": article.created_at.isoformat() if article.created_at else None
        }
    }), 201


@article_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_article(id):
    article = NewsArticle.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    return jsonify({"msg": "Article deleted successfully"}), 200
