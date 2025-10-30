#!/usr/bin/env python3
# pokemon_bot.py - Single file: Telethon + Real Download Progress + Upload

import asyncio
import aiohttp
import os
from datetime import timedelta
from telethon import TelegramClient, events, Button

# === YOUR CREDENTIALS (CHANGE LATER!) ===
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8474337967:AAH_mbpp4z1nOTDGyoJrM5r0Rii-b_TUcvA"

# === CONFIG ===
DOWNLOAD_URL = "https://example.com/your-8gb-file.iso"  # CHANGE THIS!
CHUNK_SIZE = 1024 * 1024  # 1 MB
TEMP_FILE = "downloaded_file.tmp"

# === Initialize Bot ===
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id

    # --- Step 1: Get file size ---
    async with aiohttp.ClientSession() as session:
        try:
            async with session.head(DOWNLOAD_URL) as resp:
                if resp.status != 200:
                    await event.reply("Cannot reach the file.")
                    return
                total_size = int(resp.headers.get("content-length", 0))
                if total_size == 0:
                    await event.reply("Unknown file size.")
                    return
        except Exception as e:
            await event.reply(f"Head request failed: {e}")
            return

    # --- Step 2: Start message ---
    msg = await event.reply(
        f"Downloading **{format_bytes(total_size)}** file...\n"
        "```[          ] 0.00% | 0 B / 0 B | 0 B/s | ETA: --```",
        buttons=Button.inline("Cancel", b"cancel_download")
    )

    downloaded = 0
    start_time = asyncio.get_event_loop().time()
    cancel_flag = asyncio.Event()

    # --- Cancel handler ---
    @bot.on(events.CallbackQuery(data=b"cancel_download"))
    async def cancel_download(cb):
        if cb.sender_id != user_id:
            return
        cancel_flag.set()
        await cb.answer("Cancelled.")
        await msg.edit("Download **cancelled**.")

    # --- Step 3: Download with progress ---
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DOWNLOAD_URL) as resp:
                if resp.status != 200:
                    await msg.edit("Download failed.")
                    return

                with open(TEMP_FILE, "wb") as f:
                    async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                        if cancel_flag.is_set():
                            return

                        f.write(chunk)
                        downloaded += len(chunk)

                        # Update every ~1 second
                        now = asyncio.get_event_loop().time()
                        if now - start_time >= 1.0 or downloaded == total_size:
                            await update_progress(msg, downloaded, total_size, start_time)
                            start_time = now

        # --- Success: Upload ---
        await msg.edit("Download **complete**! Uploading...")
        await bot.send_file(
            event.chat_id,
            TEMP_FILE,
            caption="Here is your file!",
            reply_to=event.id
        )
        await msg.delete()

    except Exception as e:
        await msg.edit(f"Error: {e}")
    finally:
        if os.path.exists(TEMP_FILE):
            try:
                os.remove(TEMP_FILE)
            except:
                pass


# === Helper: Update progress UI ===
async def update_progress(msg, downloaded: int, total: int, start_time: float):
    percent = downloaded / total
    bar = "█" * int(10 * percent) + "░" * (10 - int(10 * percent))
    elapsed = asyncio.get_event_loop().time() - start_time
    speed = downloaded / elapsed if elapsed > 0 else 0
    eta = (total - downloaded) / speed if speed > 0 else 0
    eta_str = str(timedelta(seconds=int(eta))) if eta > 0 else "--"

    text = (
        f"Downloading **{format_bytes(total)}** file...\n"
        f"```{bar} {percent*100:6.2f}% | "
        f"{format_bytes(downloaded)} / {format_bytes(total)} | "
        f"{format_bytes(speed)}/s | ETA: {eta_str}```"
    )
    try:
        await msg.edit(text, buttons=Button.inline("Cancel", b"cancel_download"))
    except:
        pass  # Ignore flood wait


# === Helper: Format bytes ===
def format_bytes(b):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024:
            return f"{b:.2f} {unit}"
        b /= 1024
    return f"{b:.2f} PB"


# === Run Bot ===
if __name__ == "__main__":
    print("Bot is running... Use /start to download.")
    bot.run_until_disconnected()            # Inside dark region - stays dark
        
