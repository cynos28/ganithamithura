#!/bin/bash
# ================================================================
#  GANITHAMITHURA — Full Setup & Start Script
#  Installs ALL dependencies first, then starts all services.
#  Safe to run on a fresh clone or after adding new packages.
# ================================================================

set -e  # Exit immediately if any install command fails

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Move to the script's directory (ganithamithura/)
cd "$(dirname "$0")"
BASE_DIR="$(pwd)"

# Helper: print a section header
section() {
  echo ""
  echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
  echo -e "${YELLOW}  $1${NC}"
  echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
}

ok()   { echo -e "  ${GREEN}✅ $1${NC}"; }
info() { echo -e "  ${CYAN}ℹ️  $1${NC}"; }
warn() { echo -e "  ${YELLOW}⚠️  $1${NC}"; }
err()  { echo -e "  ${RED}❌ $1${NC}"; }

# =================================================================
#  PHASE 1 — INSTALL DEPENDENCIES
# =================================================================
section "PHASE 1 — Installing dependencies for all services"

# ── Helper: create venv + install requirements.txt ──
install_service() {
  local name="$1"
  local dir="$2"
  local venv_name="${3:-.venv}"          # default venv folder name
  local requirements="${4:-requirements.txt}"

  info "[$name] Setting up environment in $dir..."
  cd "$BASE_DIR/$dir"

  # Create venv if it doesn't exist
  if [ ! -d "$venv_name" ]; then
    info "[$name] Creating virtual environment ($venv_name)..."
    /usr/bin/python3 -m venv "$venv_name"
    ok "[$name] Virtual environment created."
  else
    info "[$name] Virtual environment already exists — skipping creation."
  fi

  # Install / upgrade requirements
  if [ -f "$requirements" ]; then
    info "[$name] Installing packages from $requirements..."
    "$venv_name/bin/pip" install --upgrade pip -q
    "$venv_name/bin/pip" install -r "$requirements" -q
    ok "[$name] Packages installed successfully."
  else
    warn "[$name] No $requirements found — skipping pip install."
  fi

  cd "$BASE_DIR"
}

# ── Helper: install with uv/pyproject.toml (shape_service uses uv) ──
install_service_uv() {
  local name="$1"
  local dir="$2"

  info "[$name] Setting up environment in $dir (using pip + pyproject.toml)..."
  cd "$BASE_DIR/$dir"

  # Create venv if it doesn't exist
  if [ ! -d ".venv" ]; then
    info "[$name] Creating virtual environment (.venv)..."
    /usr/bin/python3 -m venv .venv
    ok "[$name] Virtual environment created."
  else
    info "[$name] Virtual environment already exists — skipping creation."
  fi

  # Install from pyproject.toml using pip
  info "[$name] Installing packages from pyproject.toml..."
  .venv/bin/pip install --upgrade pip -q

  if [ -f "pyproject.toml" ]; then
    .venv/bin/pip install -e ".[dev]" -q 2>/dev/null || .venv/bin/pip install -e . -q
    ok "[$name] Packages installed successfully."
  else
    warn "[$name] No pyproject.toml found."
  fi

  cd "$BASE_DIR"
}

# ── Helper: install gateway requirements into symbol-service venv ──
install_gateway() {
  info "[Gateway] Installing gateway packages into symbol-service venv..."
  cd "$BASE_DIR"
  symbol-service/venv/bin/pip install fastapi uvicorn httpx websockets pyngrok requests python-dotenv -q
  ok "[Gateway] Gateway packages installed."
}

# ─── Install each service ───────────────────────────────────────
install_service  "Auth Service"     "auth_service"    ".venv"  "requirements.txt"
install_service  "Symbol Service"   "symbol-service"  "venv"   "requirements.txt"
install_service_uv "Shape Service"  "shape_service"
install_service  "Number Service"   "number-service"  ".venv"  "requirements.txt"
install_service  "Unit RAG Service" "unit-rag-service" "venv"  "requirements.txt"
install_gateway

ok "All dependencies installed!"

# =================================================================
#  PHASE 2 — KILL ANY ORPHAN PROCESSES
# =================================================================
section "PHASE 2 — Cleaning up orphaned processes"
lsof -ti:8000,8001,8002,8003,8004,8005,4040 | xargs kill -9 2>/dev/null || true
killall ngrok 2>/dev/null || true
sleep 1
ok "Ports cleared."

# =================================================================
#  PHASE 3 — START ALL SERVICES
# =================================================================
section "PHASE 3 — Starting all backend services"

# ── 1. Auth Service (port 8001) ──────────────────────────────────
echo -e "${GREEN}[1/6] Starting Auth Service (port 8001)...${NC}"
cd "$BASE_DIR/auth_service"
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001 &
AUTH_PID=$!
deactivate 2>/dev/null || true
cd "$BASE_DIR"
sleep 1

# ── 2. Symbol Service (port 8000) ───────────────────────────────
echo -e "${GREEN}[2/6] Starting Symbol Service (port 8000)...${NC}"
cd "$BASE_DIR/symbol-service"
source venv/bin/activate
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000 &
SYMBOL_PID=$!
deactivate 2>/dev/null || true
cd "$BASE_DIR"
sleep 1

# ── 3. Shape Service (port 8003) ────────────────────────────────
echo -e "${GREEN}[3/6] Starting Shape Service (port 8003)...${NC}"
cd "$BASE_DIR/shape_service"
export PYTHONPATH="$BASE_DIR:$PYTHONPATH"
source .venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload &
SHAPE_PID=$!
deactivate 2>/dev/null || true
cd "$BASE_DIR"
sleep 1

# ── 4. Number Service (port 8004) ───────────────────────────────
echo -e "${GREEN}[4/6] Starting Number Service (port 8004)...${NC}"
cd "$BASE_DIR/number-service"
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8004 &
NUMBER_PID=$!
deactivate 2>/dev/null || true
cd "$BASE_DIR"
sleep 1

# ── 5. Unit RAG Service (port 8002) ─────────────────────────────
echo -e "${GREEN}[5/6] Starting Unit RAG Service (port 8002)...${NC}"
cd "$BASE_DIR/unit-rag-service"
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload &
UNIT_PID=$!
deactivate 2>/dev/null || true
cd "$BASE_DIR"
sleep 1

# ── 6. Gateway (port 8005) ──────────────────────────────────────
echo -e "${GREEN}[6/6] Starting API Gateway (port 8005)...${NC}"
source "$BASE_DIR/symbol-service/venv/bin/activate"
python gateway.py &
GATEWAY_PID=$!
sleep 2

# =================================================================
#  PHASE 4 — START NGROK & UPDATE GIST
# =================================================================
section "PHASE 4 — Starting Ngrok & updating GitHub Gist"
source "$BASE_DIR/symbol-service/venv/bin/activate"
python start_tunnels.py

# =================================================================
#  CLEANUP TRAP
# =================================================================
function cleanup() {
  echo ""
  echo -e "${RED}🛑 Shutting down all services...${NC}"
  kill "$AUTH_PID"   2>/dev/null
  kill "$SYMBOL_PID" 2>/dev/null
  kill "$SHAPE_PID"  2>/dev/null
  kill "$NUMBER_PID" 2>/dev/null
  kill "$UNIT_PID"   2>/dev/null
  kill "$GATEWAY_PID" 2>/dev/null
  echo -e "${GREEN}👋 Goodbye!${NC}"
  exit 0
}
trap cleanup SIGINT SIGTERM

# Keep alive while all background services run
wait
