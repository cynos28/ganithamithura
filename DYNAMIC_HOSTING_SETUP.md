# 🚀 Ganitha Mithura: Seamless Local Development Setup

This guide explains how to set up and use the dynamic local development environment. By following this guide, you will **never have to manually change your local IP address again** in `config.dart` when testing the Flutter app on physical devices or sharing with teammates.

## 🌟 The Problem this Solves
Previously, you had to manually update your laptop's local IP address (e.g., `192.168.x.x`) in the Flutter code every time you switched Wi-Fi networks. 

This new setup handles this completely automatically:
1. It launches **Ngrok** tunnels to expose your local Python backends (Auth & Symbol) to the public internet securely with temporarily generated URLs.
2. It automatically writes these URLs to a static **GitHub Gist**.
3. When the **Flutter app** launches, it silently reads this Gist to discover the live URLs and connects to your laptop dynamically!

---

## 🛠 Prerequisites (One-Time Setup)

You only need to do this setup once per computer.

### 1. Install Necessary Python Libraries
You need to install the tools that power the tunnel automation into the `symbol-service` virtual environment:
```bash
cd ganithamithura
source symbol-service/venv/bin/activate
pip install pyngrok requests python-dotenv
```

### 2. Set Up Your Ngrok Account
Ngrok requires a free account to generate public URLs.
1. Sign up for a free account at [dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup).
2. Once logged in, go to the **"Your Authtoken"** menu on the left side.
3. Copy your specific Authtoken.
4. Open your terminal and run to authenticate your computer:
   ```bash
   ngrok config add-authtoken <YOUR_COPIED_TOKEN_HERE>
   ```

### 3. Set Up Your GitHub Token
The script needs permission to automatically edit the cloud JSON file on your behalf.
1. Go to [GitHub Tokens (Classic)](https://github.com/settings/tokens/new).
2. Set **Note:** `Ngrok Auto-Updater`
3. Set **Expiration:** `No expiration`
4. Under **Select scopes**, explicitly check the box for **`gist`**.
5. Click **Generate token** at the bottom and copy the green `ghp_...` string.
6. Create a `.env` file right inside the root `/ganithamithura/` backend folder (next to `start_all.sh`).
7. Paste your token inside it exactly like this:
   ```env
   GITHUB_TOKEN=ghp_your_secret_token_here
   ```

---

## 🚀 Daily Development Workflow

Whenever you sit down to work on the project, you no longer need multiple terminal tabs or manual IP changes.

### 1. Start the Backend
Open a single terminal inside your `ganithamithura` backend folder and run:
```bash
./start_all.sh
```

**That's it!** The master script will automatically:
1. Start the Auth Service (`8001`) in the background.
2. Start the Symbol Service (`8000`) in the background.
3. Start the Ngrok tunnels.
4. Auto-update the GitHub Gist with the live URLs.

### 2. Start the Flutter App
Just run your mobile app normally:
```bash
cd gmfrontend
flutter run
```
The app will dynamically fetch the live URLs from the cloud and connect instantly!

---

## 🛑 How to Shut Down
To elegantly stop all Python servers and close the Cloud tunnels, simply press **`Ctrl + C`** in the terminal where `./start_all.sh` is running. The script handles the graceful shutdown of all processes.
