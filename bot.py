#!/usr/bin/env python3
# pokemon_bot.py - Telethon + 8GB Download + REAL Progress (No HEAD fail)

import asyncio
import aiohttp
import os
from datetime import timedelta
from telethon import TelegramClient, events, Button

# === CREDENTIALS ===
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8474337967:AAH_mbpp4z1nOTDGyoJrM5r0Rii-b_TUcvA"

# === CONFIG ===
DOWNLOAD_URL = "https://ash-speed.hetzner.com/8GB.bin"  # 8 GB TEST FILE
CHUNK_SIZE = 1024 * 1024  # 1 MB
TEMP_FILE = "downloaded_file.tmp"

# === Bot ===
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id

    # --- Try to get size via HEAD (optional) ---
    total_size = None
    async with aiohttp.ClientSession() as session:
        try:
            async with session.head(DOWNLOAD_URL, timeout=10) as resp:
                if resp.status == 200:
                    total_size = int(resp.headers.get("content-length", 0))
        except:
            pass  # Ignore — we'll detect size during download

    # --- Start message ---
    size_str = format_bytes(total_size) if total_size else "?? GB"
    msg = await event.reply(
        f"Downloading **8 GB File**...\n"
        f"```[          ] 0.00% | 0 B / {size_str} | 0 B/s | ETA: --```",
        buttons=Button.inline("Cancel", b"cancel_download")
    )

    downloaded = 0
    start_time = asyncio.get_event_loop().time()
    cancel_flag = asyncio.Event()
    detected_size = total_size

    # --- Cancel ---
    @bot.on(events.CallbackQuery(data=b"cancel_download"))
    async def cancel_download(cb):
        if cb.sender_id != user_id:
            return
        cancel_flag.set()
        await cb.answer("Cancelled.")
        await msg.edit("Download **cancelled**.")

    # --- Download ---
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None)) as session:
            async with session.get(DOWNLOAD_URL) as resp:
                if resp.status != 200:
                    await msg.edit("Download failed (HTTP error).")
                    return

                # Detect size from Content-Length if not known
                if not detected_size and "content-length" in resp.headers:
                    detected_size = int(resp.headers["content-length"])

                with open(TEMP_FILE, "wb") as f:
                    async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                        if cancel_flag.is_set():
                            return

                        f.write(chunk)
                        downloaded += len(chunk)

                        # Update every 1 sec
                        now = asyncio.get_event_loop().time()
                        if now - start_time >= 1.0:
                            await update_progress(
                                msg, downloaded, detected_size or downloaded, start_time
                            )
                            start_time = now

        # --- Upload ---
        await msg.edit("Download **complete**! Uploading...")
        await bot.send_file(
            event.chat_id,
            TEMP_FILE,
            caption="Your 8 GB file is ready!",
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


# === Update Progress UI ===
async def update_progress(msg, downloaded: int, total: int, start_time: float):
    percent = downloaded / total if total > 0 else 0
    bar = "█" * int(10 * percent) + "░" * (10 - int(10 * percent))
    elapsed = asyncio.get_event_loop().time() - start_time
    speed = downloaded / elapsed if elapsed > 0 else 0
    eta = (total - downloaded) / speed if speed > 0 and total > downloaded else 0
    eta_str = str(timedelta(seconds=int(eta))) if eta > 0 else "--"

    total_str = format_bytes(total) if total > 0 else "?? GB"

    text = (
        f"Downloading **8 GB File**...\n"
        f"```{bar} {percent*100:6.2f}% | "
        f"{format_bytes(downloaded)} / {total_str} | "
        f"{format_bytes(speed)}/s | ETA: {eta_str}```"
    )
    try:
        await msg.edit(text, buttons=Button.inline("Cancel", b"cancel_download"))
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
    print("Bot running... /start = 8GB download with REAL progress")
    bot.run_until_disconnected()
