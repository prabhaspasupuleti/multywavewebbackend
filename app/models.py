# backend/app/models.py
from flask_sqlalchemy import SQLAlchemy

# Define SQLAlchemy instance
db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'adminuser'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)  # Storing plain password (Not secure, for testing only)

class NewsArticle(db.Model):
    __tablename__ = 'newsarticles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)  # ✅ change this from description → content
    image_path = db.Column(db.Text)
    pdf_path = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

