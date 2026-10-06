import telebot
import random
import string
import json
import os
from datetime import datetime

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN)

ACCOUNTS_FILE = "carx_mod_accounts.json"

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=4)

def generate_username():
    return "modcx_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits + "@#", k=12))

def generate_ingame_email():
    domains = ["carx.mod", "cxstreet.mod", "mod.carx", "streetmod.local"]
    return generate_username() + "@" + random.choice(domains)

@bot.message_handler(commands=['start'])
def start(message):
    text = "🚗 CarX Street Mod Account Bot\n\nCommand:\n/create - Buat akun mod baru\n/list - Lihat semua akun\n/export - Export semua akun\n/setmod <id> - Tandai sudah di-mod\n/setinject <id> - Tandai sudah di-inject\n/status - Lihat status"
    bot.reply_to(message, text)

@bot.message_handler(commands=['create'])
def create_mod_account(message):
    username = generate_username()
    password = generate_password()
    email = generate_ingame_email()
    accounts = load_accounts()
    acc_id = len(accounts) + 1
    account = {
        "id": acc_id,
        "username": username,
        "password": password,
        "email": email,
        "type": "mod_account",
        "mod_status": "belum",
        "inject_status": "belum",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": "Email in-game only"
    }
    accounts.append(account)
    save_accounts(accounts)
    text = f"✅ Akun Mod berhasil dibuat\n\nID: {acc_id}\nUsername: {username}\nPassword: {password}\nEmail: {email}\n\nStatus Mod: belum\nStatus Inject: belum"
    bot.reply_to(message, text)

@bot.message_handler(commands=['list'])
def list_accounts(message):
    accounts = load_accounts()
    if not accounts:
        bot.reply_to(message, "Belum ada akun.")
        return
    text = f"Total akun: {len(accounts)}\n\n"
    for acc in accounts[-15:]:
        text += f"ID {acc['id']} | {acc['username']} | Mod: {acc['mod_status']} | Inject: {acc['inject_status']}\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=['export'])
def export_accounts(message):
    accounts = load_accounts()
    if not accounts:
        bot.reply_to(message, "Belum ada akun.")
        return
    filename = "carx_mod_accounts.txt"
    with open(filename, "w") as f:
        for acc in accounts:
            f.write(f"{acc['id']}|{acc['username']}|{acc['password']}|{acc['email']}|{acc['mod_status']}|{acc['inject_status']}\n")
    with open(filename, "rb") as f:
        bot.send_document(message.chat.id, f, caption="Export Akun Mod")

@bot.message_handler(commands=['setmod'])
def set_mod(message):
    try:
        acc_id = int(message.text.split()[1])
    except:
        bot.reply_to(message, "Format: /setmod <id>")
        return
    accounts = load_accounts()
    for acc in accounts:
        if acc["id"] == acc_id:
            acc["mod_status"] = "sudah"
            save_accounts(accounts)
            bot.reply_to(message, f"✅ ID {acc_id} sudah ditandai di-mod.")
            return
    bot.reply_to(message, "ID tidak ditemukan.")

@bot.message_handler(commands=['setinject'])
def set_inject(message):
    try:
        acc_id = int(message.text.split()[1])
    except:
        bot.reply_to(message, "Format: /setinject <id>")
        return
    accounts = load_accounts()
    for acc in accounts:
        if acc["id"] == acc_id:
            acc["inject_status"] = "sudah"
            save_accounts(accounts)
            bot.reply_to(message, f"✅ ID {acc_id} sudah ditandai di-inject.")
            return
    bot.reply_to(message, "ID tidak ditemukan.")

@bot.message_handler(commands=['status'])
def status(message):
    accounts = load_accounts()
    if not accounts:
        bot.reply_to(message, "Belum ada akun.")
        return
    total = len(accounts)
    modded = len([a for a in accounts if a["mod_status"] == "sudah"])
    injected = len([a for a in accounts if a["inject_status"] == "sudah"])
    text = f"📊 Status\n\nTotal Akun: {total}\nSudah di-Mod: {modded}\nSudah di-Inject: {injected}\nBelum: {total - modded}"
    bot.reply_to(message, text)

print("Bot berjalan...")
bot.infinity_polling()
