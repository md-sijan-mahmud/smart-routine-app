import requests

def send_telegram_message(message, task_id=None):
    TOKEN = "8754453213:AAGqnh-RGzADWs8CJnG65p4zyETR8PMurXA"
    CHAT_ID = "8648935327"  # Apnar chat ID
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    # Jodi task_id dewa thake, tahole interactive buttons (Mark as Done & Snooze) add korbe
    if task_id:
        payload["reply_markup"] = {
            "inline_keyboard": [
                [
                    {"text": "✅ Mark as Done", "callback_data": f"done_{task_id}"},
                    {"text": "⏰ Snooze 10m", "callback_data": f"snooze_{task_id}"}
                ]
            ]
        }
    
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None