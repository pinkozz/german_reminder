import telebot, time
from get_time import get_time

bot = telebot.TeleBot(token="API_TOKEN")

lehrbuch = "Zeit für eine Seite von Lehrbuch!📕"
worter = "Zeit für die Wörter Überarbeitung!🌐"
video = "Zeit für eine Deutsche Video!📹"
podcast = "Zeit für eine Deutsche Podcast!🎧"
unterricht = "Zeit für ein Paar Schulunterrichts!🏫"

reminders = {
    7: podcast,
    10: unterricht,
    12: video,
    14: lehrbuch,
    17: worter
}

@bot.message_handler(commands=['start'])
def greet(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, f"Hallo!🙋‍♂️ \nIch bin hier um errinern dir daran zu Deutsch zu lernen! Von jetzt an, werde ich dir hier Errinerungen senden")

    while True:
        if get_time()[0] in reminders.keys() and get_time()[1] == 0:
            bot.send_message(message.chat.id, reminders[get_time()[0]])
            time.sleep(60)

if __name__ == "__main__":
    bot.polling(non_stop=True)