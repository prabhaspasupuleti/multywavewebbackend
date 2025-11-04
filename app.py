# backend/app.py

from app import create_app

# ✅ Create the Flask app instance from the factory
app = create_app()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
