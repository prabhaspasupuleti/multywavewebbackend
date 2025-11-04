from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from app.models import NewsArticle, db
import os
import traceback

# Blueprint
article_bp = Blueprint("article_bp", __name__)

# Allowed file types
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_PDF_EXTENSIONS = {"pdf"}


# -------------------------------
# Helper Functions
# -------------------------------
def allowed_file(filename, allowed_exts):
    """Check if file has allowed extension"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_exts


def save_file(file, subfolder):
    """Save file to uploads/ subfolder"""
    if not file:
        return None

    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    return f"/uploads/{subfolder}/{filename}"


# -------------------------------
# Routes
# -------------------------------

@article_bp.route("/", methods=["GET"])
def get_articles():
    """Fetch all articles"""
    try:
        articles = NewsArticle.query.order_by(NewsArticle.created_at.desc()).all()

        return jsonify([
            {
                "id": a.id,
                "title": a.title or "",
                "content": a.content or "",
                "image_url": a.image_path or "",
                "pdf_url": a.pdf_path or "",
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in articles
        ]), 200

    except Exception as e:
        print("🔥 ERROR in GET /api/articles/:", e)
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


@article_bp.route("/", methods=["POST"])
@jwt_required()
def create_article():
    """Create new article"""
    try:
        title = request.form.get("title")
        content = request.form.get("content")
        image = request.files.get("image")
        pdf = request.files.get("pdf")

        if not title:
            return jsonify({"msg": "Title is required"}), 400
        if not content:
            return jsonify({"msg": "Content is required"}), 400

        # Validate file types
        if image and not allowed_file(image.filename, ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({"msg": "Invalid image format"}), 400
        if pdf and not allowed_file(pdf.filename, ALLOWED_PDF_EXTENSIONS):
            return jsonify({"msg": "Invalid PDF format"}), 400

        # Save files
        image_path = save_file(image, "images") if image else None
        pdf_path = save_file(pdf, "pdfs") if pdf else None

        # Create DB record
        article = NewsArticle(
            title=title,
            content=content,
            image_path=image_path,
            pdf_path=pdf_path,
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
                "created_at": article.created_at.isoformat() if article.created_at else None,
            },
        }), 201

    except Exception as e:
        print("🔥 ERROR in POST /api/articles/:", e)
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


@article_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_article(id):
    """Delete article by ID"""
    try:
        article = NewsArticle.query.get_or_404(id)
        db.session.delete(article)
        db.session.commit()
        return jsonify({"msg": "Article deleted successfully"}), 200

    except Exception as e:
        print(f"🔥 ERROR deleting article {id}:", e)
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": "Failed to delete article", "details": str(e)}), 500
