import telebot, time, json
from get_time import get_time

import db
from db import User

bot = telebot.TeleBot(token="API_KEY")

# lehrbuch = "Zeit für eine Seite von Lehrbuch!📕"
# worter = "Zeit für die Wörter Überarbeitung!🌐"
# video = "Zeit für eine Deutsche Video!📹"
# podcast = "Zeit für eine Deutsche Podcast!🎧"
# unterricht = "Zeit für ein Paar Schulunterrichts!🏫"

# reminders = {
#     7: podcast,
#     10: unterricht,
#     12: video,
#     14: lehrbuch,
#     17: worter
# }

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

            bot.send_message(message.chat.id, f"Hallo!🙋‍♂️ \nIch bin hier um errinern dir daran zu Deutsch zu lernen! Von jetzt an, werde ich dir hier Errinerungen senden")

            while True:
                if str(get_time()[0]) in get_reminders(user_id).keys() and get_time()[1] == 0:
                    bot.send_message(message.chat.id, get_reminders(user_id)[str(get_time()[0])])
                time.sleep(60)
        except Exception as e:
            bot.send_message(message.chat.id, "Etwas ist schiefgelaufen, aber der Entwickler arbeitet daran.")
            print(e)

if __name__ == "__main__":
    bot.polling(non_stop=True)