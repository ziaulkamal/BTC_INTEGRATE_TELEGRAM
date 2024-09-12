#!/bin/bash

# Ambil direktori saat ini
CURRENT_DIR=$(pwd)

# 1. Membuat Virtual Environment di direktori saat ini
echo "Creating virtual environment in $CURRENT_DIR/venv..."
python3 -m venv "$CURRENT_DIR/venv"

# 2. Aktivasi virtual environment
source "$CURRENT_DIR/venv/bin/activate"

# 3. Install dependensi dari requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r "$CURRENT_DIR/requirements.txt"

# 4. Mengatur nama sesi server berdasarkan user Linux
SERVER_NAME=$(whoami)
echo "Server name is set to: $SERVER_NAME"

# Simpan nama server di dalam file environment (.env) di direktori saat ini
echo "SERVER_NAME=\"$SERVER_NAME\"" > "$CURRENT_DIR/.env"

# 5. Menjalankan script btc.py di direktori saat ini
echo "Running btc.py in $CURRENT_DIR..."
python "$CURRENT_DIR/btc.py"
