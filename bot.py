import json

import telebot
from telebot import types

from apscheduler.schedulers.background import BackgroundScheduler

import db
from db import User

from get_time import get_time

bot = telebot.TeleBot(token="API_TOKEN")

messages:dict = {
    "de": {
        "greet_message": "Hallo!🙋‍♂️ \nIch bin hier um errinern dir daran zu Deutsch zu lernen! Von jetzt an, werde ich dir hier Errinerungen senden. \n\nBitte wählen Sie Ihre Sprache:",
        "hours_message": "Bitte geben Sie die Uhrzeit ein, zu der Sie die Erinnerung erhalten möchten:",
        "text_message": "Bitte geben Sie den Text Ihrer Erinnerung ein:",
        "reminder_created": "Erinnerung wurde gespeichert.",
        "my_reminders_message": "Deine Erinnerungen:",
        "language_changed_message": "Die Spreche ist auf Deutsch geändert.",
        "delete_confirmation_message": "Bist du sicher, dass du möchtest diese Erinnerung löschen: ",
        "deleted_message": "Die Erinnerung ist gelöscht.",
        "aborted_message": "Aktion abgebrochen.",

        "yes_button": "Ja",
        "no_button": "Nein",
        "edit_button": "Bearbeiten",
        "delete_button": "Löschen",

        "no_reminders_message": "Du hast keine Erinnerungen.",
        "error_message": "Etwas ist schiefgelaufen, aber der Entwickler arbeitet daran.",
        "reminder_exists_message": "Für diese Stunde ist bereits eine Erinnerung eingestellt.",
    },
    "gb": {
        "greet_message": "Hello!🙋‍♂️ \nI am here to remind you to learn German! From now on, I will be sending you reminders. \n\nPlease choose your language:",
        "hours_message": "Please specify the hour when you want to receive a reminder:",
        "text_message": "Please specify the message of the reminder:",
        "reminder_created": "Reminder has been created.",
        "my_reminders_message": "Your reminders:",
        "language_changed_message": "The language has been changed to English.",
        "delete_confirmation_message": "Are you sure that you want to delete this reminder: ",
        "deleted_message": "The reminder is deleted.",
        "aborted_message": "Action aborted.",

        "yes_button": "Yes",
        "no_button": "No",
        "edit_button": "Edit",
        "delete_button": "Delete",

        "no_reminders_message": "You have no reminders.",
        "error_message": "Something went wrong, but the developer works on it.",
        "reminder_exists_message": "There is already a reminder for this hour.",
    }
}

user_data:dict = db.user_data
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

            markup = types.InlineKeyboardMarkup()

            german = types.InlineKeyboardButton("🇩🇪", callback_data="de")
            english = types.InlineKeyboardButton("🇬🇧/🇺🇸", callback_data="gb")

            markup.add(german, english)

            bot.send_message(message.chat.id, messages[user_data[user_id]["language"]]["greet_message"], reply_markup=markup)

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

@bot.message_handler(commands=['my_reminders'])
def my_reminders(message):
    if message.chat.type == 'private':
        try:
            user_id = str(message.from_user.id)
            initialize_user_data(user_id)

            user_reminders:dict = user_data[user_id]["reminders"]
            reminders = []

            num = 1

            markup = types.InlineKeyboardMarkup()

            for i, k in user_reminders.items():
                reminders.append(f"{num}. {"00" if i == "24" else i}:00 – {k}")
                button = types.InlineKeyboardButton("\n".join(f"{num}. {"00" if i == "24" else i}:00 – {k}"), callback_data=f"{i}")
                markup.add(button)
                num+=1

            if len(user_reminders) > 0:
                bot.send_message(message.chat.id, f"{messages[user_data[user_id]["language"]]["my_reminders_message"]}\n\n" + "\n".join(reminders), reply_markup=markup)
            else:
                bot.send_message(message.chat.id, messages[user_data[user_id]["language"]]["no_reminders_message"])
        except Exception as e:
            bot.send_message(message.chat.id, messages[user_data[user_id]["language"]]["error_message"])
            print(e)

def get_hours(msg):
    try:
        user_id:str = str(msg.from_user.id)
        hours:str = msg.text

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
        user_id:str = str(msg.from_user.id)
        reminder_text:str = msg.text
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

# Callbacks
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id:str = str(call.from_user.id)
    user_reminders:dict = user_data[user_id]["reminders"]
    hours = user_data[user_id].get('current_hour')

    if call.data == "gb":
        user_data[user_id]["language"] = "gb"
        sync()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[call.data]["language_changed_message"])
    elif call.data == "de":
        user_data[user_id]["language"] = "de"
        sync()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[call.data]["language_changed_message"])

    for i, k in user_reminders.items():
        if call.data == i:
            markup = types.InlineKeyboardMarkup()

            edit = types.InlineKeyboardButton(messages[user_data[user_id]["language"]]["edit_button"], callback_data="edit")
            delete = types.InlineKeyboardButton(messages[user_data[user_id]["language"]]["delete_button"], callback_data="delete")

            markup.add(edit, delete)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{"00" if i == "24" else i}:00 – {k}", reply_markup=markup)
            
            user_data[user_id]['current_hour'] = i
            sync()

    if call.data == "delete":
        markup = types.InlineKeyboardMarkup()

        yes = types.InlineKeyboardButton(messages[user_data[user_id]["language"]]["yes_button"], callback_data="yes")
        no = types.InlineKeyboardButton(messages[user_data[user_id]["language"]]["no_button"], callback_data="no")

        markup.add(yes, no)
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[user_data[user_id]["language"]]["delete_confirmation_message"] + f"\"{user_data[user_id]["reminders"][hours]}\" for {"00" if hours == "24" else hours}:00?", reply_markup=markup)
    
    elif call.data == "edit":
        hour = user_data[user_id]["current_hour"]
        del user_data[user_id]["reminders"][hour]

        if 1 <= int(hour) <= 24:
            if user_data[user_id]['reminders'].get(hour):
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[user_data[user_id]["language"]]["reminder_exists_message"])
            else:
                # Store the hour temporarily and ask for the reminder text
                user_data[user_id]['current_hour'] = hour
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[user_data[user_id]["language"]]["text_message"])
                bot.register_next_step_handler(call.message, get_text)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[user_data[user_id]["language"]]["error_message"])

    elif call.data == "yes":
        del user_data[user_id]["reminders"][hours]
        sync()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[user_data[user_id]["language"]]["deleted_message"])

    elif call.data == "no":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[user_data[user_id]["language"]]["aborted_message"])


# Schedule the reminder checker
scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()

if __name__ == "__main__":
    bot.polling(non_stop=True)
