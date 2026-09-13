import os
import telebot
import assistant
from telebot import types
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
ai_assistant = assistant.WeatherAiAssistant()


@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    geolocation_button = types.KeyboardButton(
        text="📍 Отправить мою геолокацию", request_location=True
    )
    markup.add(geolocation_button)

    bot.send_message(
        message.chat.id,
        "«Привет! Нажми на кнопку ниже, чтобы поделиться геолокацией. Это нужно для того, чтобы программа смогла запросить данные о погоде именно в твоей точке и передать их нейросети для составления прогноза погоды.»",
        reply_markup=markup,
    )


@bot.message_handler(content_types=["location"])
def handle_location(message):
    latitude = message.location.latitude
    longitude = message.location.longitude

    try:
        bot.send_message(
            message.chat.id,
            "Секунду, считываю GPS и отправляю запрос нейросети...",
        )

        raw_weather = ai_assistant.get_weather_data(latitude, longitude)
        weather_summary = ai_assistant.filter_weather_data(raw_weather)
        final_report = ai_assistant.get_ai_report(weather_summary)

        bot.send_message(message.chat.id, final_report)

    except Exception as e:
        bot.send_message(
            message.chat.id, f"Произошла ошибка при генерации отчета: {e}"
        )


if __name__ == "__main__":
    bot.polling(none_stop=True)
