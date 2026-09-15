import ollama
import requests


class WeatherAiAssistant:

    def get_weather_data(self, latitude, longitude):
        url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code&forecast_days=1'
        print(url)
        weather_data = requests.get(url, timeout=5)
        if weather_data.status_code == 200:
            return weather_data.json()
        return None


    def filter_weather_data(self, weather_data):
        if weather_data is None:
            return None


        hourly_data = weather_data["hourly"]

        max_temp = max(hourly_data["temperature_2m"])
        min_temp = min(hourly_data["temperature_2m"])
        max_apparent_temp = max(hourly_data["apparent_temperature"])

        precipitation_numbers = hourly_data["precipitation"]
        precipitation_words = []

        for hour, precipitation in enumerate(precipitation_numbers):
            if precipitation <= 0.2:
                continue

            if precipitation <= 1:
                status = "мелкий дождь"
            elif precipitation <= 2:
                status = "обычный дождь"
            else:
                status = "ливень"

            precipitation_words.append(f"* в {hour}:00 — {status}")

        if precipitation_words:
            hourly_precipitation = "\n".join(precipitation_words)
            hourly_precipitation += "\n* В остальное время суток — сухо."
        else:
            hourly_precipitation = "Осадков не ожидается, весь день будет сухо."

        text_for_ai = (
            f"Погода: температура за сутки от {min_temp}°C до {max_temp}°C. "
            f"При этом максимальная дневная температура {max_temp}°C ощущается как {max_apparent_temp}°C.\n"
            f"График осадков на сегодня:\n{hourly_precipitation}"
        )
        return text_for_ai



    def get_ai_report(self, weather_data):
        ai_system_prompt = """
        Ты — обычный парень, который пишет другу простое сообщение в Telegram. Твоя задача — пересказать погоду простым живым языком.

        Правила:
        Запрещено использовать сложные книжные и канцелярские слова (не пиши: «субъективно», «достигнет максимума», «в пределах», «можно ожидать»). Напиши проще: «по ощущениям», «обещают», «будет».
        Текст должен быть в один короткий абзац (2-3 предложения) без списков и маркеров.

        ЕСЛИ ДАННЫХ НЕТ, ответь строго в таком стиле:
        Слушай, сервер с погодой не работает. Извини, попробуй позже.
        
        ЕСЛИ В СВОДКЕ НАПИСАНО «Осадков не ожидается», ответь строго в таком стиле:
        «Сегодня будет тепло, до 23°C, по ощущениям даже чуть теплее. Весь день будет сухо, так что зонт не понадобится, можно спокойно гулять.»
        
        ЕСЛИ В СВОДКЕ ЕСТЬ КОНКРЕТНЫЕ ЧАСЫ ОСАДКОВ, пиши точное время цифрами. Ориентируйся строго на этот пример ответа:
        «Днем будет тепло, до 23°C. В 12:00 и 13:00 обещают мелкий дождь, так что лучше взять зонт. В остальное время будет сухо.»
        """

        response = ollama.chat(
            model="qwen2.5:7b",
            messages=[
                {"role": "system", "content": ai_system_prompt},
                {"role": "user", "content": str(weather_data)},
            ]
        )
        return response["message"]["content"]
