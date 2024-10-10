import telebot, time, json
from get_time import get_time

import db
from db import User

bot = telebot.TeleBot(token="API_TOKEN")

greet_message = "Hallo!🙋‍♂️ \nIch bin hier um errinern dir daran zu Deutsch zu lernen! Von jetzt an, werde ich dir hier Errinerungen senden"
error_message = "Etwas ist schiefgelaufen, aber der Entwickler arbeitet daran."

hours_message = "Bitte geben Sie die Uhrzeit ein, zu der Sie die Erinnerung erhalten möchten:"
text_message = "Bitte geben Sie den Text Ihrer Erinnerung ein:"

reminder_exists_message = "Für diese Stunde ist bereits eine Erinnerung eingestellt"

user_data = db.user_data

# Function to initialize user data if not present
def initialize_user_data(user_id, user_data):
    if user_id not in user_data:
        new_user = User(user_id)
        new_user.create_user()

# Sync data with json file
def sync():
    with open("db.json", "w") as f:
        f.write(json.dumps(user_data, indent=4))

# Get user's reminders
def get_reminders(user_id):
    user_reminders = user_data[user_id]["reminders"]
    return user_reminders

@bot.message_handler(commands=['start'])
def main(message):
    if message.chat.type == 'private':
        try:
            user_id = str(message.from_user.id)
            initialize_user_data(user_id, user_data)

            bot.send_message(message.chat.id, greet_message)

            while True:
                if str(get_time()[0]) in get_reminders(user_id).keys() and get_time()[1] == 52:
                    bot.send_message(message.chat.id, get_reminders(user_id)[str(get_time()[0])])
                time.sleep(60)
        except Exception as e:
            bot.send_message(message.chat.id, error_message)
            print(e)

@bot.message_handler(commands=['reminder'])
def set_reminder(message):
    if message.chat.type == 'private':
        try:
            user_id = str(message.from_user.id)
            initialize_user_data(user_id, user_data)

            bot.send_message(message.chat.id, hours_message)

            # Wait for the user to send the hour
            @bot.message_handler(func=lambda msg: True)
            def get_hours(msg):
                try:
                    hours = msg.text

                    if 1 <= int(hours) <= 23:
                        try:
                            if user_data[user_id]['reminders'][hours]:
                                bot.send_message(msg.chat.id, reminder_exists_message)
                        except KeyError:
                            # Store the hour temporarily and ask for the reminder text
                            user_data[user_id]['current_hour'] = hours
                            bot.send_message(msg.chat.id, text_message)
                            
                            # Move to the next step to get the reminder text
                            bot.register_next_step_handler(msg, get_text)
                    else:
                        bot.send_message(msg.chat.id, error_message)
                except ValueError:
                    bot.send_message(msg.chat.id, error_message)

        except Exception as e:
            bot.send_message(message.chat.id, error_message)
            print(e)

# Handler to capture the reminder text
def get_text(msg):
    try:
        user_id = str(msg.from_user.id)
        reminder_text = msg.text
        hours = user_data[user_id].get('current_hour')

        if hours is not None:
            # Save the reminder with the corresponding hour
            user_data[user_id]['reminders'][hours] = reminder_text
            sync()
        else:
            bot.send_message(msg.chat.id, error_message)

    except Exception as e:
        bot.send_message(msg.chat.id, error_message)
        print(e)

if __name__ == "__main__":
    bot.polling(non_stop=True)