from telethon import TelegramClient, events
import requests, os

API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8397651199:AAGPUiPNlr4AkgGoQK6BWAeyK4uCYL0knJ4"

bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

VIDEO_URL = "https://files.catbox.moe/491yle.mp4"
VIDEO_NAME = "491yle.mp4"


# 🔥 Download only ONCE — then reuse the file instantly
def download_once():
    if os.path.isfile(VIDEO_NAME) and os.path.getsize(VIDEO_NAME) > 0:
        print("File already downloaded. Skipping download.")
        return

    print("Downloading video from Catbox…")

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
    }

    with requests.get(VIDEO_URL, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(VIDEO_NAME, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):  # 1MB chunks = faster
                if chunk:
                    f.write(chunk)

    print("Video saved:", VIDEO_NAME)


download_once()  # Preload at startup — only once


@bot.on(events.NewMessage(pattern="^/start$"))
async def send_fast(event):

    await event.respond("Sending video… 🚀")

    # ⚡ Fastest upload mode using threads
    await bot.send_file(
        event.chat_id,
        VIDEO_NAME,
        caption="Here is your video!",
        force_document=False,   # True sends as file, False sends as video
        use_cache=True,         # Reuse upload cache for speed
        supports_streaming=True # Allows quick playback
    )


print("Bot is running…")
bot.run_until_disconnected()
