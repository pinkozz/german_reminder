import telebot
import time
import json
from get_time import get_time
from apscheduler.schedulers.background import BackgroundScheduler

import db
from db import User

bot = telebot.TeleBot(token="7863666634:AAE0DOEbD6_17PZM0ZDG6tF6cRQV8yvc_iA")

messages = {
    "de": {
        "greet_message": "Hallo!🙋‍♂️ \nIch bin hier um errinern dir daran zu Deutsch zu lernen! Von jetzt an, werde ich dir hier Errinerungen senden.",
        "hours_message": "Bitte geben Sie die Uhrzeit ein, zu der Sie die Erinnerung erhalten möchten:",
        "text_message": "Bitte geben Sie den Text Ihrer Erinnerung ein:",
        "reminder_created": "Erinnerung wurde gespeichert.",
        "error_message": "Etwas ist schiefgelaufen, aber der Entwickler arbeitet daran.",
        "reminder_exists_message": "Für diese Stunde ist bereits eine Erinnerung eingestellt.",

    },
    "gb": {
        "greet_message": "Hello!🙋‍♂️ \nI am here to remind you to learn German! From now on, I will be sending you reminders.",
        "hours_message": "Please specify the hour when you want to receive a reminder:",
        "text_message": "Please specify the message of the reminder:",
        "reminder_created": "Reminder has been created.",
        "error_message": "Something went wrong, but the developer works on it.",
        "reminder_exists_message": "There is already a reminder for this hour.",
    }
}

user_data = db.user_data
scheduler = BackgroundScheduler()

# Function to initialize user data if not present
def initialize_user_data(user_id):
    if user_id not in user_data:
        new_user = User(user_id)
        new_user.create_user()

# Sync data with json file
def sync():
    with open("db.json", "w") as f:
        f.write(json.dumps(user_data, indent=4))

# Get user's reminders
def get_reminders(user_id):
    return user_data.get(user_id, {}).get("reminders", {})

# Function to send reminder if the time matches
def check_reminders():
    for user_id in user_data:
        reminders = get_reminders(user_id)
        current_hour, current_minute = get_time()
        if str(current_hour) in reminders and current_minute == 0:
            bot.send_message(user_id, reminders[str(current_hour)])

# Command to start the bot
@bot.message_handler(commands=['start'])
def main(message):
    if message.chat.type == 'private':
        try:
            user_id = str(message.from_user.id)
            initialize_user_data(user_id)

            bot.send_message(message.chat.id, messages[user_data[user_id]["language"]]["greet_message"])

        except Exception as e:
            bot.send_message(message.chat.id, messages[user_data[user_id]["language"]]["error_message"])
            print(e)

# Command to set a reminder
@bot.message_handler(commands=['reminder'])
def set_reminder(message):
    if message.chat.type == 'private':
        try:
            user_id = str(message.from_user.id)
            initialize_user_data(user_id)

            bot.send_message(message.chat.id, messages[user_data[user_id]["language"]]["hours_message"])

            # Wait for the user to send the hour
            bot.register_next_step_handler(message, get_hours)

        except Exception as e:
            bot.send_message(message.chat.id, messages[user_data[user_id]["language"]]["error_message"])
            print(e)

def get_hours(msg):
    try:
        user_id = str(msg.from_user.id)
        hours = msg.text

        if 1 <= int(hours) <= 24:
            if user_data[user_id]['reminders'].get(hours):
                bot.send_message(msg.chat.id, messages[user_data[user_id]["language"]]["reminder_exists_message"])
            else:
                # Store the hour temporarily and ask for the reminder text
                user_data[user_id]['current_hour'] = hours
                bot.send_message(msg.chat.id, messages[user_data[user_id]["language"]]["text_message"])
                bot.register_next_step_handler(msg, get_text)
        else:
            bot.send_message(msg.chat.id, messages[user_data[user_id]["language"]]["error_message"])

    except ValueError:
        bot.send_message(msg.chat.id, messages[user_data[user_id]["language"]]["error_message"])

def get_text(msg):
    try:
        user_id = str(msg.from_user.id)
        reminder_text = msg.text
        hours = user_data[user_id].get('current_hour')

        if hours:
            # Save the reminder with the corresponding hour
            user_data[user_id]['reminders'][hours] = reminder_text
            sync()
            bot.send_message(msg.chat.id, messages[user_data[user_id]["language"]]["reminder_created"])
        else:
            bot.send_message(msg.chat.id, messages[user_data[user_id]["language"]]["error_message"])

    except Exception as e:
        bot.send_message(msg.chat.id, messages[user_data[user_id]["language"]]["error_message"])
        print(e)

# Schedule the reminder checker
scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()

if __name__ == "__main__":
    bot.polling(non_stop=True)
