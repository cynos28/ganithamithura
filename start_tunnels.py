import os
import requests
import time
from pyngrok import ngrok

# You must set your GITHUB_TOKEN environment variable or put it in a .env file next to this script.
# e.g., create a .env file in the ganithamithura directory with: GITHUB_TOKEN=ghp_...
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GIST_ID = "a03d59a6c3a4e84f0688591151f6fd30"

def update_cloud_urls():
    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN environment variable not set.")
        print("   Please create a .env file in this directory with GITHUB_TOKEN=ghp_your_token")
        return

    print("🚀 Starting Ngrok tunnels...")
    # Port 8000 (Symbol) and Port 8001 (Auth)
    symbol_url = ngrok.connect(8000, bind_tls=True).public_url
    auth_url = ngrok.connect(8001, bind_tls=True).public_url
    
    print(f"✅ Symbol API: {symbol_url}")
    print(f"✅ Auth API:   {auth_url}")

    print("☁️ Sending URLs to the cloud Gist...")
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "files": {
            "ganithamithura_urls.json": {
                "content": f'{{\n  "symbol_api": "{symbol_url}",\n  "auth_api": "{auth_url}"\n}}'
            }
        }
    }
    
    response = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=data)
    
    if response.status_code == 200:
        print("✅ Success! Your Flutter app will automatically fetch these URLs on startup.")
    else:
        print("❌ Failed to update Gist:", response.status_code, response.text)

    print("\nPress Ctrl+C to stop tunnels and exit.")
    
    try:
        # Keep tunnels open
        ngrok.get_ngrok_process().proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down ngrok...")
        ngrok.kill()

if __name__ == "__main__":
    update_cloud_urls()
