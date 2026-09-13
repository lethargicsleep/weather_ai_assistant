import pandas as pd
import ollama
import requests


class WeatherAiAssistant:

    def get_weather_data(self, latitude, longitude):
        url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code&forecast_days=1'
        print(url)
        weather_data = requests.get(url, timeout=5)
        return weather_data.json()

    def filter_weather_data(self, weather_data):
        hourly_data = weather_data["hourly"]

        weather_df = pd.DataFrame({
            "Время": hourly_data["time"],
            "Температура (°C)": hourly_data["temperature_2m"],
            "Ощущается как (°С)": hourly_data["apparent_temperature"],
            "Влажность (%)": hourly_data["relative_humidity_2m"],
            "Осадки (мм)": hourly_data["precipitation"],
        })

        weather_df["Spacer"] = "Время"
        weather_df["Время"] = pd.to_datetime(weather_df["Время"]).dt.strftime("%Y-%m-%d %H:%M")

        max_temp = weather_df["Температура (°C)"].max()
        min_temp = weather_df["Температура (°C)"].min()
        max_apparent_temp = weather_df["Ощущается как (°С)"].max()

        precipitation_numbers = weather_df["Осадки (мм)"]
        precipitation_words = []

        for precipitation in precipitation_numbers:
            if precipitation <= 0.2:
                precipitation_words.append("Сухо")
            elif precipitation <= 1:
                precipitation_words.append("мелкий дождь")
            elif precipitation <= 2:
                precipitation_words.append("обычный дождь")
            else:
                precipitation_words.append("ливень")

        hourly_precipitation = ", ".join(precipitation_words)

        text_for_ai = (
            f"Погода: температура за сутки от {min_temp}°C до {max_temp}°C. "
            f"При этом максимальная дневная температура {max_temp}°C ощущается как {max_apparent_temp}°C. "
            f"Статус осадков по часам (начиная с 00:00 до 23:00): {hourly_precipitation}."
        )
        return text_for_ai

    def get_ai_report(self, weather_data):
        ai_system_prompt = """
Ты — обычный русский парень, который пишет другу простое сообщение в Telegram. Твоя задача — пересказать погоду простым живым языком.

Правила:
1. Запрещено использовать сложные книжные и канцелярские слова (не пиши: «субъективно», «достигнет максимума», «в пределах», «можно ожидать»). Напиши проще: «по ощущениям», «обещают», «будет».
2. Пиши строго на русском языке без китайских иероглифов.
3. Текст должен быть в один короткий абзац (2-3 предложения) без списков и маркеров.

Ориентируйся на этот живой стиль:
«Сегодня за окном кайфовые +20°C, по ощущениям почти так же, так что смело выходи в легкой куртке или худи. Весь день будет сухо, но часам к девяти вечера обещают мелкий дождик, так что на позднюю прогулку лучше захватить зонт.»
"""
        response = ollama.chat(
            model="qwen2.5:7b",
            messages=[
                {"role": "system", "content": ai_system_prompt},
                {"role": "user", "content": str(weather_data)},
            ]
        )
        return response["message"]["content"]


if __name__ == "__main__":
    a = WeatherAiAssistant()
    raw_weather_data = a.get_weather_data(44.63,41.94)
    weather_text = a.filter_weather_data(raw_weather_data)
    print(a.get_ai_report(weather_text))