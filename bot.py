from pyrogram import Client, filters
import os
from PIL import Image

# --- YOUR CREDENTIALS (for testing only) ---
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8397651199:AAGPUiPNlr4AkgGoQK6BWAeyK4uCYL0knJ4"
# -------------------------------------------

# Initialize bot client
bot = Client("sticker_to_file_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Ensure folder exists
os.makedirs("downloads", exist_ok=True)

@bot.on_message(filters.sticker)
async def sticker_to_file(client, message):
    sticker = message.sticker
    msg = await message.reply_text("🔄 Converting sticker...")

    # Download sticker
    file_path = await client.download_media(sticker, file_name="downloads/")

    if sticker.is_animated:
        # Animated sticker (.tgs)
        new_name = file_path.replace(".tgs", ".json")
        os.rename(file_path, new_name)
        file_path = new_name
        caption = "🎞 Animated sticker (.tgs as .json)"
    elif sticker.is_video:
        # Video sticker (.webm)
        caption = "🎬 Video sticker (.webm)"
    else:
        # Static sticker (.webp → .png)
        img = Image.open(file_path).convert("RGBA")
        new_name = file_path.replace(".webp", ".png")
        img.save(new_name, "PNG")
        os.remove(file_path)
        file_path = new_name
        caption = "🖼 Static sticker (.png)"

    await msg.edit_text("✅ Done! Sending file...")
    await message.reply_document(file_path, caption=caption)
    os.remove(file_path)

print("🤖 Sticker to File Bot is running...")
bot.run()
