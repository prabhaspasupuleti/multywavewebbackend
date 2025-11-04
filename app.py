from app import create_app
import os
import platform

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    system = platform.system().lower()

    if system == "windows":
        from waitress import serve
        print(f"🚀 Running with Waitress on http://127.0.0.1:{port}")
        serve(app, host="0.0.0.0", port=port)
    else:
        from waitress import serve
        print(f"🚀 Running in production mode on {system}")
        serve(app, host="0.0.0.0", port=port)
