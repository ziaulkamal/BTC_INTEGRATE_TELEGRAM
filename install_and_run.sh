#!/bin/bash

# 1. Membuat Virtual Environment
echo "Creating virtual environment..."
python3 -m venv venv

# Aktivasi virtual environment
source venv/bin/activate

# 2. Install dependensi dari requirements.txt
echo "Installing dependencies..."
pip install -r requirements.txt

# 3. Mengatur nama sesi server berdasarkan user Linux
SERVER_NAME=$(whoami)
echo "Server name is set to: $SERVER_NAME"

# Menyimpan nama server di dalam file environment (.env)
echo "SERVER_NAME=\"$SERVER_NAME\"" > .env

# 4. Menjalankan script btc.py
echo "Running btc.py..."
python btc.py
 