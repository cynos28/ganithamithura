# 🚀 Ganithamithura Backend — Setup & Run Guide

This guide explains how to set up and run the entire Ganithamithura backend from scratch using the **`setup_and_start.sh`** script.

> **Use this script** when you are running the project for the first time, after pulling new code, or after adding new packages to any service.  
> If everything is already installed and you just want to start services, use the existing `start_all.sh`.

---

## 📋 Prerequisites

Before running the script, make sure the following are installed on your machine:

| Tool | Version | How to check |
|------|---------|--------------|
| **Python 3** | 3.10+ | `python3 --version` |
| **pip** | latest | `pip3 --version` |
| **MongoDB** | 5.0+ (or Atlas URI in `.env`) | `mongod --version` |
| **Ngrok** | any | `ngrok --version` |
| **GitHub Token** | — | Set in `ganithamithura/.env` |

---

## 🗂️ Project Structure

```
ganithamithura/
├── auth_service/           # Authentication — Port 8001
│   ├── .env                # MONGODB_URL, DB_NAME
│   └── requirements.txt
├── symbol-service/         # Symbol Tutor — Port 8000
│   └── requirements.txt
├── shape_service/          # Shape Games — Port 8003
│   └── pyproject.toml      # (uses pip editable install)
├── number-service/         # Number Activities — Port 8004
│   └── requirements.txt
├── unit-rag-service/       # Measurement & RAG — Port 8002
│   └── requirements.txt
├── gateway.py              # API Gateway — Port 8005
├── start_tunnels.py        # Ngrok + GitHub Gist updater
├── setup_and_start.sh      # ← THIS SCRIPT (install + start)
├── start_all.sh            # Quick start (no install)
└── .env                    # GITHUB_TOKEN (required for Gist)
```

---

## ⚙️ Environment Variables (Required)

### `ganithamithura/.env`
```env
GITHUB_TOKEN=ghp_your_personal_access_token_here
```
> This token is used to update the GitHub Gist that the Flutter app reads to discover the current Ngrok tunnel URL.

### `ganithamithura/auth_service/.env`
```env
MONGODB_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
DB_NAME=ganithamithura
```

### `ganithamithura/unit-rag-service/.env`
```env
OPENAI_API_KEY=sk-...
MONGODB_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/
MONGODB_DB_NAME=ganithamithura_rag
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8002
```

---

## 🚦 Running the Backend

### Step 1 — Make the script executable (first time only)
```bash
chmod +x setup_and_start.sh
```

### Step 2 — Run the setup & start script
```bash
./setup_and_start.sh
```

That's it! The script will automatically:

---

## 🔄 What the Script Does (Step by Step)

### Phase 1 — Install Dependencies
For each service the script:
1. **Creates a Python virtual environment** (`.venv` or `venv`) if one doesn't already exist
2. **Upgrades pip** to the latest version
3. **Installs all packages** from `requirements.txt` (or `pyproject.toml` for the Shape Service)

| # | Service | Install Method | Virtual Env |
|---|---------|----------------|------------|
| 1 | Auth Service | `pip install -r requirements.txt` | `auth_service/.venv` |
| 2 | Symbol Service | `pip install -r requirements.txt` | `symbol-service/venv` |
| 3 | Shape Service | `pip install -e .` (pyproject.toml) | `shape_service/.venv` |
| 4 | Number Service | `pip install -r requirements.txt` | `number-service/.venv` |
| 5 | Unit RAG Service | `pip install -r requirements.txt` | `unit-rag-service/venv` |
| 6 | Gateway | fastapi, uvicorn, httpx, websockets, pyngrok | `symbol-service/venv` |

> ✅ If the virtualenv already exists, creation is **skipped** — only packages are upgraded.

---

### Phase 2 — Kill Orphaned Processes
Clears any leftover processes on ports **8000–8005** and **4040** (Ngrok) from a previous run.

---

### Phase 3 — Start All Services
Starts each service as a background process in order:

| # | Service | Port |
|---|---------|------|
| 1 | Auth Service | 8001 |
| 2 | Symbol Service (AI Tutor) | 8000 |
| 3 | Shape Service | 8003 |
| 4 | Number Service | 8004 |
| 5 | Unit RAG / Measurement Service | 8002 |
| 6 | API Gateway | 8005 |

---

### Phase 4 — Start Ngrok & Update Gist
- Opens a single **Ngrok HTTPS tunnel** pointing to the Gateway (port 8005)
- Sends the new public URL to a **GitHub Gist** so the Flutter app always discovers the correct backend address automatically

---

## 🛑 Stopping the Backend

Press **`Ctrl+C`** in the terminal where the script is running.

The script will gracefully shut down **all 6 services** automatically.

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| `No module named uvicorn` | Run `./setup_and_start.sh` again — it will install missing packages |
| `Port already in use` | The script auto-kills orphaned processes on startup |
| `GITHUB_TOKEN not set` | Add `GITHUB_TOKEN=ghp_...` to `ganithamithura/.env` |
| `Ngrok tunnel not updating` | Check your Ngrok account is logged in: `ngrok config check` |
| `MongoDB connection failed` | Check the `MONGODB_URL` in each service's `.env` file |
| Flutter app using old URL | Tap **Sign In** — the app always fetches the latest URL from the Gist before signing in |

---

## 🔁 Difference between `setup_and_start.sh` and `start_all.sh`

| | `setup_and_start.sh` | `start_all.sh` |
|---|---|---|
| Creates virtual environments | ✅ Yes | ❌ No |
| Installs dependencies | ✅ Yes | ❌ No |
| Kills orphaned processes | ✅ Yes | ✅ Yes |
| Starts all services | ✅ Yes | ✅ Yes |
| Starts Ngrok & updates Gist | ✅ Yes | ✅ Yes |
| **When to use** | First run / new packages | Daily use (already set up) |

---

*Made with ❤️ by the Ganithamithura Team*
