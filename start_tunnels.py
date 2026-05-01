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
GIST_ID = "a7c05a2ca61b4646e1e641102b9cf2a8"

def update_cloud_urls():
    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN environment variable not set.")
        print("   Please create a .env file in this directory with GITHUB_TOKEN=ghp_your_token")
        return

    print("🚀 Starting Ngrok Gateway tunnel...")
    # Tunnel ONLY the Gateway port
    gateway_url = ngrok.connect(8005, bind_tls=True).public_url
    
    print(f"🌍 Gateway URL: {gateway_url}")
    print(f"✅ Symbol API: {gateway_url}/symbol")
    print(f"✅ Auth API:   {gateway_url}/auth")
    print(f"✅ Shape API:  {gateway_url}/shape")
    print(f"✅ Number API: {gateway_url}/number")

    print("☁️ Sending URLs to the cloud Gist...")
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "files": {
            "ganithamithura_urls.json": {
                "content": f'{{\n  "symbol_api": "{gateway_url}/symbol",\n  "auth_api": "{gateway_url}/auth",\n  "shape_api": "{gateway_url}/shape",\n  "number_api": "{gateway_url}/number",\n  "measurement_api": "{gateway_url}/measurement"\n}}'
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
