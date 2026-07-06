# Public entry point for running the Smart Insure application with ngrok tunnel.
import os
import shutil
from dotenv import load_dotenv
from pyngrok import ngrok, conf
from app import app

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # Retrieve port from env or default to 5000
    port = int(os.getenv("PORT", 5000))
    
    # Check if a system-wide ngrok binary is installed and use it
    # This prevents pyngrok from trying to download ngrok, which was timing out.
    system_ngrok = shutil.which("ngrok")
    if system_ngrok:
        conf.get_default().ngrok_path = system_ngrok
        print(f" * Using system ngrok binary at: {system_ngrok}")
    
    # Retrieve ngrok auth token from environment
    ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
    if ngrok_auth_token:
        ngrok.set_auth_token(ngrok_auth_token)
    else:
        print(" * WARNING: No NGROK_AUTH_TOKEN found in your .env file.")
        print(" * Modern ngrok (v3) requires a valid account and authtoken to start a session.")
        print(" * Please sign up / sign in at: https://dashboard.ngrok.com/")
        print(" * Retrieve your token from: https://dashboard.ngrok.com/get-started/your-authtoken")
        print(" * Then add it to your .env file as: NGROK_AUTH_TOKEN=your_token_here\n")
        
    # Prevent running ngrok twice when Flask debug reloader is active.
    # The parent process starts the tunnel, and the child process starts the server.
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        try:
            public_url = ngrok.connect(str(port))
            print(f"\n * Public ngrok tunnel active: {public_url.public_url}")
            print(" * You can access the InsureSmart platform using the link above.")
        except Exception as e:
            print(f"\n * Could not establish ngrok tunnel: {e}")
            print(" * Please double-check your NGROK_AUTH_TOKEN config.")
    else:
        print(" * Reloader active: skipping duplicate ngrok tunnel setup.")


    # Start Flask application
    app.run(port=port)
