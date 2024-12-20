from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
import requests
from bs4 import BeautifulSoup
from typing import List, Union
import spacy
from collections import Counter
from config import TOKEN
import asyncio

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Загрузка модели spaCy для русского языка
nlp = spacy.load("ru_core_news_sm")


# Функция для извлечения текста с веб-сайта
def extract_text_from_url(url: str) -> Union[str, None]:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Извлечение только текста из тегов <p>
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

        # Проверяем, извлёкся ли текст
        return text if text else None
    except requests.exceptions.RequestException as e:
        return f"Ошибка при запросе к URL: {e}"
    except Exception as e:
        return f"Ошибка при обработке текста: {e}"


# Функция для создания резюме текста
def summarize_text(text: str, top_n: int = 10) -> Union[List[str], str]:
    try:
        doc = nlp(text)

        # Разбиваем текст на предложения
        sentences = [sent.text for sent in doc.sents]

        # Считаем частоту слов, исключая стоп-слова
        words = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]
        word_frequencies = Counter(words)

        # Вычисляем вес каждого предложения
        sentence_scores = {
            sent: sum(word_frequencies.get(word.lower(), 0) for word in sent.split())
            for sent in sentences
        }

        # Сортируем предложения по их весу
        ranked_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)

        # Возвращаем топ-N предложений
        return [sent[0] for sent in ranked_sentences[:top_n]]
    except Exception as e:
        return f"Ошибка при анализе текста: {e}"


# Хендлер команды /start
@dp.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    await message.reply(
        "Привет! Я бот для анализа научных статей. Отправьте мне ссылку на статью, и я создам краткое резюме для вас."
    )


# Хендлер для обработки URL
@dp.message()
async def process_url(message: Message):
    url = message.text.strip()
    await message.reply("Проверяю ссылку и извлекаю текст...")

    extracted_text = extract_text_from_url(url)
    if isinstance(extracted_text, str) and extracted_text.startswith("Ошибка"):
        await message.reply(extracted_text)
        return

    if not extracted_text:
        await message.reply("Не удалось извлечь текст с указанной страницы.")
        return

    await message.reply("Анализирую текст и создаю резюме...")

    summary = summarize_text(extracted_text)
    if isinstance(summary, str) and summary.startswith("Ошибка"):
        await message.reply(summary)
        return

    if summary:
        await message.reply("Резюме статьи:\n\n" + "\n\n".join(f"- {sent}" for sent in summary))
    else:
        await message.reply("Не удалось создать резюме статьи.")


# Основной цикл бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")