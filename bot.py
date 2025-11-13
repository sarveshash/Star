from telethon import TelegramClient, events
from telethon.tl.custom.button import Button

API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8397651199:AAGPUiPNlr4AkgGoQK6BWAeyK4uCYL0knJ4"

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

VIDEO_URL = "https://files.catbox.moe/491yle.mp4"

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    try:
        await bot.send_file(
            event.chat_id,
            file=VIDEO_URL,
            force_document=False,
            allow_cache=False,
            buttons=[[Button.inline("Next", b"next")]]
        )
    except Exception as e:
        print("SEND ERROR:", e)
        await event.reply("⚠️ Failed to send media")

@bot.on(events.CallbackQuery(pattern=b"next"))
async def next_button(event):
    await event.answer("Button working!", alert=True)

print("Bot is running...")
bot.run_until_disconnected()
