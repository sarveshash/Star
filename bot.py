from telethon import TelegramClient, events
import requests
import os

# ⚠️ PUT YOUR REAL API VALUES HERE (ONLY ON YOUR PC)
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8397651199:AAGPUiPNlr4AkgGoQK6BWAeyK4uCYL0knJ4"

bot = TelegramClient("bochct", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

VIDEO_URL = "https://files.catbox.moe/491yle.mp4"
VIDEO_NAME = "491yle.mp4"

def download_video():
    if os.path.exists(VIDEO_NAME):
        return

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0 Safari/537.36"
        )
    }

    print("Downloading video...")
    with requests.get(VIDEO_URL, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(VIDEO_NAME, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)

    print("Download completed:", VIDEO_NAME)


@bot.on(events.NewMessage(pattern=r"^/start$"))
async def start(event):
    await event.respond("Downloading video… Please wait…")

    download_video()

    await event.respond("Sending video…")
    await bot.send_file(event.chat_id, VIDEO_NAME)


print("Bot started…")
bot.run_until_disconnected()
