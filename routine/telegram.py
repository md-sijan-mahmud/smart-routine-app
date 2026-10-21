import requests

def send_telegram_message(message):
    TOKEN = "8754453213:AAGqnh-RGzADWs8CJnG65p4zyETR8PMurXA"
    CHAT_ID = "8648935327"  # Apnar photo theke pawa chat ID
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None