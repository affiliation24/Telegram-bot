import requests
import time

# Замените на свой токен
BOT_TOKEN = '8043398659:AAEM1BPCJaXalx9mu8fF5u5rC-hXeR5VaGg'

def handle_update(update):
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        if text == '/start':
            send_message(chat_id, "Привет! Я готов помочь.")
        elif text.startswith('/'):
            process_command(chat_id, text)
        else:
            send_echo(chat_id, f"Повторяю ваше сообщение: {text}")

def send_message(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': chat_id, 'text': message}
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"Ошибка при отправке сообщения: {response.status_code}")

def send_echo(chat_id, message):
    """Отправка повторения сообщения."""
    send_message(chat_id, message)

def process_command(chat_id, command_text):
    """Обработка команд."""
    if command_text == '/help':
        send_message(chat_id, "Доступны следующие команды:\n/start\n/help")
    else:
        send_message(chat_id, "Неизвестная команда. Попробуйте /help.")

def get_and_handle_updates():
    offset = None
    empty_update_count = 0  # Счетчик для отслеживания пустых обновлений
    while True:
        try:
            params = {"offset": offset + 1} if offset is not None else {}
            response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", params=params)

            if response.status_code == 200:
                updates = response.json().get('result', [])
                
                if updates:
                    for update in updates:
                        handle_update(update)
                        offset = update["update_id"]
                    empty_update_count = 0  # Сброс счетчика пустых обновлений после получения данных
                else:
                    # Выводим сообщение только при первом пустом обновлении
                    if empty_update_count == 0:
                        print("Пустые обновления, ждём дальше...")
                    empty_update_count += 1

            else:
                print(f"Ошибка при получении обновлений: статус-код {response.status_code}. Ждем дальше...")

        except Exception as e:
            print(f"Произошла ошибка: {e}. Ждем дальше...")

        time.sleep(2)  # Увеличенная задержка между запросами

if __name__ == "__main__":
    get_and_handle_updates()