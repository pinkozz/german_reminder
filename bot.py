import telebot, time

bot = telebot.TeleBot(token="TOKEN")

lehrbuch = "Zeit für eine Seite von Lehrbuch!📕"
worter = "Zeit für die Wörter Überarbeitung!🌐"
video = "Zeit für eine Deutsche Video!📹"
podcast = "Zeit für eine Deutsche Podcast!🎧"

@bot.message_handler(commands=['start'])
def greet(message):
  if message.chat.type == 'private':
    bot.send_message(message.chat.id, f"Hallo!🙋‍♂️ \nIch bin hier um errinern dir daran zu Deutsch zu lernen! Von jetzt an, werde ich dir hier Errinerungen senden")

  while True:
    if time.gmtime().tm_hour == 6 and time.gmtime().tm_min == 0 and time.gmtime().tm_sec == 0:
       bot.send_message(message.chat.id, worter)
       time.sleep(60)
    ...

if __name__ == "__main__":
    bot.polling(non_stop=True)