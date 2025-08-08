import requests
import difflib
from datetime import datetime
import os

# ======= Cấu hình ========
TELEGRAM_BOT_TOKEN = '7271422281:AAGoto1nz1yobV_mlmvJyIIz9qI35RWLJgI'
CHAT_ID = '-1002700925034'
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ======= Gửi tin nhắn Telegram ========
def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")

# ======= Lấy nội dung file raw từ GitHub ========
def get_file_content(raw_url: str) -> str:
    response = requests.get(raw_url, headers=HEADERS)
    response.raise_for_status()
    return response.text

# ======= So sánh nội dung cũ/mới ========
def detect_changes(old_content, new_content):
    return list(difflib.unified_diff(old_content.splitlines(), new_content.splitlines()))

# ======= Trích xuất dòng bảng được thêm mới ========
def extract_telegram_info(diff_lines):
    results = []
    for line in diff_lines:
        if line.startswith('+|') and not line.startswith('+++') and not line.startswith('+|---'):
            try:
                parts = line[1:].strip().split('|')
                if len(parts) >= 3:
                    telegram = parts[1].strip()
                    status = parts[2].strip()
                    name = parts[3].strip() if len(parts) > 3 else "Unknown"
                    results.append({
                        'telegram': telegram,
                        'status': status,
                        'name': name
                    })
            except Exception as e:
                print(f"[ERROR] Failed to parse line: {line}\n{e}")
    return results

# ======= Xử lý từng file ========
def process_file(raw_url, local_path, category):
    print(f"Checking file: {raw_url}")
    try:
        new_content = get_file_content(raw_url)
    except Exception as e:
        print(f"[ERROR] Could not fetch file: {e}")
        return

    old_content = ""
    if os.path.exists(local_path):
        with open(local_path, 'r', encoding='utf-8') as f:
            old_content = f.read()

    if new_content != old_content:
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        diff = detect_changes(old_content, new_content)
        entries = extract_telegram_info(diff)

        for entry in entries:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = (
                f"🔔 Update Threat Actor\n"
                f"Category: #{category}\n"
                f"Time : {now}\n"
                f"--------------------------------------\n"
                f"Name : {entry.get('name', 'Unknown')}\n"
                f"Telegram: {entry.get('telegram', 'None')}\n"
                f"Status: {entry.get('status', 'None')}\n"
                f"--------------------------------------\n"
                f"deepdarkCTI Monitoring"
            )
            send_telegram_message(message)
    else:
        print("No changes detected.")

# ======= Main ========
if __name__ == "__main__":
    process_file(
        raw_url="https://raw.githubusercontent.com/tcvbabybash1337/deepdarkCTI/main/telegram_infostealer.md",
        local_path="infostealer_backup.md",
        category="telegram_infostealer"
    )

    process_file(
        raw_url="https://raw.githubusercontent.com/tcvbabybash1337/deepdarkCTI/main/telegram_threat_actors.md",
        local_path="threat_actor_backup.md",
        category="telegram_threat_actors"
    )
