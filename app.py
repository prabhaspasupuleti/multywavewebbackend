# backend/app.py
from app import create_app

app = create_app()  # expose for Gunicorn

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
