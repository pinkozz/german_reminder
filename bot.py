import sqlite3

import telebot
from telebot import types

from apscheduler.schedulers.background import BackgroundScheduler

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

user_data = {}
scheduler = BackgroundScheduler()

def get_db_connection():
    connection = sqlite3.connect("reminders.db")
    return connection

# Function to initialize user data if not present
def initialize_user_data(user_id: str):
    connection = get_db_connection()
    c = connection.cursor()

    # Check if the user is already in the database
    c.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()

    # If the user is not in the database, insert them with the default language
    if user is None:
        c.execute("INSERT INTO users (user_id, language, current_hour) VALUES (?, ?, ?)", (user_id, 'gb', '0'))
        user_data[user_id] = {
            "language": 'gb',  # Default language
            "reminders": {},
            "current_hour": "0"
        }
    else:
        # If the user exists, load their language from the database
        user_data[user_id] = {
            "language": user[0],  # Load the language from the database
            "reminders": get_reminders(user_id),
            "current_hour": get_current_hour(user_id)
        }

    connection.commit()
    connection.close()


# Get user's reminders
def get_reminders(user_id:str):
    connection = get_db_connection()
    c = connection.cursor()

    c.execute("SELECT hour, text FROM reminders WHERE user_id=?", (user_id,))
    reminders = {row[0]: row[1] for row in c.fetchall()}

    connection.close()
    return reminders

# Get user's language
def get_language(user_id:str):
    connection = get_db_connection()
    c = connection.cursor()

    c.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    print(result)

    connection.close()

    if result is not None:
        return result[0]  # Unpack the first value from the tuple
    return None


def get_current_hour(user_id:str):
    connection = get_db_connection()
    c = connection.cursor()

    c.execute("SELECT current_hour FROM users WHERE user_id=?", (user_id,))
    current_hour = c.fetchone()

    connection.close()
    
    if current_hour is not None:
        return current_hour[0]
    return None

# Get a reminder's text by hour
def get_text_by_hour(user_id:str, hour:str):
    connection = get_db_connection()
    c = connection.cursor()

    c.execute("SELECT text FROM reminders WHERE user_id=? AND hour=?", (user_id, hour,))
    reminder_text = c.fetchone()

    connection.close()
    
    if reminder_text is not None:
        return reminder_text[0]
    return None

# Get a reminder's hour by text
def get_hour_by_text(user_id:str, text:str):
    connection = get_db_connection()
    c = connection.cursor()

    c.execute("SELECT hour FROM reminders WHERE user_id=? AND text=?", (user_id, text,))
    reminder_hour = c.fetchone()

    connection.close()
    
    if reminder_hour is not None:
        return reminder_hour[0]
    return None

# Update user's language
def update_language(user_id:str, language:str):
    connection = get_db_connection()
    c = connection.cursor()

    c.execute("UPDATE users SET language=? WHERE user_id=?", (language, user_id,))

    connection.commit()
    connection.close()

# Update text by reminder's hour
def update_text(user_id:str, hour:str, new_text:str):
    connection = get_db_connection()
    c = connection.cursor()

    c.execute("UPDATE reminders SET text=? WHERE user_id=? AND hour=?", (new_text, user_id, hour,))

    connection.commit()
    connection.close()

# Update current_hour
def update_current_hour(user_id:str, new_current_hour:str):
    connection = get_db_connection()
    c = connection.cursor()

    c.execute("UPDATE users SET current_hour=? WHERE user_id=?", (new_current_hour, user_id,))
    
    connection.commit()
    connection.close()

# Remove a reminder by hour
def remove_by_hour(user_id:str, hour:str):
    connection = get_db_connection()
    c = connection.cursor()

    c.execute("DELETE FROM reminders WHERE user_id=? AND hour=?", (user_id, hour,))

    connection.commit()
    connection.close()

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

            user_reminders:dict = get_reminders(user_id)
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
            if get_text_by_hour(user_id, hours):
                bot.send_message(msg.chat.id, messages[user_data[user_id]["language"]]["reminder_exists_message"])
            else:
                # Store the hour temporarily and ask for the reminder text
                update_current_hour(user_id, hours)
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
        hours = get_current_hour(user_id)

        if hours:
            # Check if a reminder for this hour already exists
            existing_text = get_text_by_hour(user_id, hours)

            connection = get_db_connection()
            c = connection.cursor()

            if existing_text is None:
                # Insert the new reminder if it doesn't exist
                c.execute("INSERT INTO reminders (user_id, hour, text) VALUES (?, ?, ?)", (user_id, hours, reminder_text))
            else:
                # Update the existing reminder
                c.execute("UPDATE reminders SET text=? WHERE user_id=? AND hour=?", (reminder_text, user_id, hours))

            connection.commit()
            connection.close()

            bot.send_message(msg.chat.id, messages[user_data[user_id]["language"]]["reminder_created"])
        else:
            bot.send_message(msg.chat.id, messages[user_data[user_id]["language"]]["error_message"])

    except Exception as e:
        bot.send_message(msg.chat.id, messages[user_data[user_id]["language"]]["error_message"])
        print(e)

# Callbacks
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = str(call.from_user.id)
    user_reminders = get_reminders(user_id)
    hours = get_current_hour(user_id)

    if call.data == "gb":
        update_language(user_id, 'gb')
        user_data[user_id]['language'] = 'gb'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages['gb']["language_changed_message"])

    elif call.data == "de":
        update_language(user_id, 'de')
        user_data[user_id]['language'] = 'de'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages['de']["language_changed_message"])

    # Handle reminder operations
    for i, k in user_reminders.items():
        if call.data == i:
            markup = types.InlineKeyboardMarkup()

            edit = types.InlineKeyboardButton(messages[user_data[user_id]["language"]]["edit_button"], callback_data="edit")
            delete = types.InlineKeyboardButton(messages[user_data[user_id]["language"]]["delete_button"], callback_data="delete")

            markup.add(edit, delete)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{'00' if i == '24' else i}:00 – {k}", reply_markup=markup)
            
            update_current_hour(user_id, i)

    # Handle delete confirmation
    if call.data == "delete":
        markup = types.InlineKeyboardMarkup()

        yes = types.InlineKeyboardButton(messages[user_data[user_id]["language"]]["yes_button"], callback_data="yes")
        no = types.InlineKeyboardButton(messages[user_data[user_id]["language"]]["no_button"], callback_data="no")

        markup.add(yes, no)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[user_data[user_id]["language"]]["delete_confirmation_message"] + f"\"{user_reminders[hours]}\" for {'00' if hours == '24' else hours}:00?", reply_markup=markup)

    # If the user confirms deletion
    elif call.data == "yes":
        remove_by_hour(user_id, hours)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[user_data[user_id]["language"]]["deleted_message"])

    # If the user cancels the deletion
    elif call.data == "no":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[user_data[user_id]["language"]]["aborted_message"])

    # Handle edit reminder
    elif call.data == "edit":
        hour = get_current_hour(user_id)

        try:
            # Ask the user for new text to update the reminder
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[user_data[user_id]["language"]]["text_message"])
            bot.register_next_step_handler(call.message, get_text)  # Use get_text to update reminder text
        except Exception as e:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messages[user_data[user_id]["language"]]["error_message"])
            print(e)


# Schedule the reminder checker
scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()

if __name__ == "__main__":
    bot.polling(non_stop=True)
