#!/usr/bin/env python3
# pokemon_bot_mega_4gb.py - Telethon + REAL Mega.nz Folder Download + Progress

import asyncio
import os
from datetime import timedelta
from telethon import TelegramClient, events, Button
from mega import Mega  # pip install mega.py

# === CREDENTIALS ===
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8474337967:AAH_mbpp4z1nOTDGyoJrM5r0Rii-b_TUcvA"

# === MEGA CONFIG ===
MEGA_EMAIL = "your_email@example.com"  # Your Mega account (optional, for private)
MEGA_PASSWORD = "your_password"         # Optional
MEGA_API_KEY = "your_mega_api_key"      # Get free at mega.io (required for public)
MEGA_FOLDER_URL = "https://mega.nz/folder/ikIETQ6a#dsmQzxLeXyK-DIVpR-ZAOg"  # Your link
CHUNK_SIZE = 1024 * 1024  # 1 MB
TEMP_FILE = "temp_mega_folder.zip"

# === Bot ===
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id

    # --- Login to Mega ---
    mega = Mega()
    try:
        m_api = mega.login(MEGA_EMAIL, MEGA_PASSWORD) if MEGA_EMAIL else Mega({'api_key': MEGA_API_KEY})
    except Exception as e:
        await event.reply(f"Mega login failed: {e}. Check credentials.")
        return

    # --- Get folder info & estimate size ---
    total_size = 0
    try:
        folder = m_api.get_public_folder(MEGA_FOLDER_URL)  # For public; use get_folder for private
        for file in folder.get_files():
            total_size += file.size
    except Exception as e:
        await event.reply(f"Folder access failed: {e}. Is it public?")
        return

    if total_size == 0:
        await event.reply("Folder empty or inaccessible.")
        return

    # --- Start message ---
    msg = await event.reply(
        f"Downloading **{format_bytes(total_size)}** Mega Folder (Pokémon Clips)...\n"
        "```[          ] 0.00% | 0 B / 4.00 GB | 0 B/s | ETA: --```",
        buttons=Button.inline("Cancel", b"cancel_mega")
    )

    downloaded = 0
    start_time = asyncio.get_event_loop().time()
    cancel_flag = asyncio.Event()

    # --- Cancel ---
    @bot.on(events.CallbackQuery(data=b"cancel_mega"))
    async def cancel_mega(cb):
        if cb.sender_id != user_id:
            return
        cancel_flag.set()
        await cb.answer("Cancelled.")
        await msg.edit("Download **cancelled**.")

    # --- Download folder ---
    try:
        # Download all files (progress per file)
        for file_attr in folder.get_files():
            if cancel_flag.is_set():
                break

            file_name = file_attr.name
            await msg.edit(f"Downloading **{file_name}** from folder...")

            # Download single file
            file_path = m_api.download(file_attr, dest_filename=f"temp_{file_name}")
            
            # Simulate progress (Mega.py doesn't have built-in; wrap with callback if needed)
            # For real progress, use mega.download with progress hook (advanced)
            # Here: Simple size-based update
            downloaded += file_attr.size
            now = asyncio.get_event_loop().time()
            if now - start_time >= 1.0:
                await update_progress(msg, downloaded, total_size, start_time)
                start_time = now

        # --- Zip folder if multiple files ---
        import zipfile
        zip_path = TEMP_FILE
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_attr in folder.get_files():
                zipf.write(f"temp_{file_attr.name}", file_attr.name)
                os.remove(f"temp_{file_attr.name}")  # Cleanup

        # --- Upload ---
        final_size = os.path.getsize(zip_path)
        await msg.edit(f"Download **complete** ({format_bytes(final_size)})! Uploading...")
        if final_size > 2 * 1024**3:
            await event.reply("Folder too big for Telegram (2GB limit). Saved as ZIP locally!")
        else:
            await bot.send_file(
                event.chat_id,
                zip_path,
                caption="Your Pokémon Mega folder (clips/ROMs) is here! 🌟",
                reply_to=event.id
            )
        await msg.delete()

    except Exception as e:
        await msg.edit(f"Error: {e}")
    finally:
        # Cleanup temps
        for f in os.listdir('.'):
            if f.startswith('temp_') and f != TEMP_FILE:
                os.remove(f)
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)


# === Update Progress ===
async def update_progress(msg, downloaded: int, total: int, start_time: float):
    percent = (downloaded / total * 100) if total > 0 else 0
    bar = "█" * int(10 * (percent / 100)) + "░" * (10 - int(10 * (percent / 100)))
    elapsed = asyncio.get_event_loop().time() - start_time
    speed = downloaded / elapsed if elapsed > 0 else 0
    eta = (total - downloaded) / speed if speed > 0 and total > downloaded else 0
    eta_str = str(timedelta(seconds=int(eta))) if eta > 0 else "Done!"

    text = (
        f"Downloading **Mega Folder** (Pokémon Pack)...\n"
        f"```{bar} {percent:6.2f}% | "
        f"{format_bytes(downloaded)} / {format_bytes(total)} | "
        f"{format_bytes(speed)}/s | ETA: {eta_str}```"
    )
    try:
        await msg.edit(text, buttons=Button.inline("Cancel", b"cancel_mega"))
    except:
        pass


# === Format Bytes ===
def format_bytes(b):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024:
            return f"{b:.2f} {unit}"
        b /= 1024
    return f"{b:.2f} PB"


# === Run ===
if __name__ == "__main__":
    print("Bot running... /start = REAL Mega.nz folder download (~4GB)")
    bot.run_until_disconnected()
