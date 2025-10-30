#!/usr/bin/env python3
# pokemon_bot_real_4gb.py - Telethon + REAL 4GB Download from 1Fichier + Progress

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
DOWNLOAD_URL = "https://1fichier.com/?68t5fyri8fwlqkotk4yc?af=5006637"  # Your 4GB file!
CHUNK_SIZE = 1024 * 1024  # 1 MB
TEMP_FILE = "temp_download.tmp"

# === Bot ===
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id

    # --- Get size via HEAD ---
    total_size = None
    async with aiohttp.ClientSession() as session:
        try:
            async with session.head(DOWNLOAD_URL, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    total_size = int(resp.headers.get("content-length", 0))
                elif resp.status >= 400:
                    await event.reply(f"HTTP {resp.status} — check link or try later.")
                    return
        except Exception as e:
            pass  # Proceed without size

    if not total_size:
        await event.reply("Could not detect file size — proceeding anyway.")
        total_size = 4 * 1024**3  # Assume 4 GB

    # --- Start message ---
    msg = await event.reply(
        f"Downloading **{format_bytes(total_size)}** Pokémon Pack...\n"
        "```[          ] 0.00% | 0 B / 4.00 GB | 0 B/s | ETA: --```",
        buttons=Button.inline("Cancel", b"cancel_download")
    )

    downloaded = 0
    start_time = asyncio.get_event_loop().time()
    cancel_flag = asyncio.Event()

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
            async with session.get(DOWNLOAD_URL, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                if resp.status != 200:
                    await msg.edit(f"Download failed (HTTP {resp.status}).")
                    return

                # Detect size if missed
                if "content-length" in resp.headers:
                    total_size = int(resp.headers["content-length"])

                with open(TEMP_FILE, "wb") as f:
                    async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                        if cancel_flag.is_set():
                            return

                        f.write(chunk)
                        downloaded += len(chunk)

                        # Update every 1 sec
                        now = asyncio.get_event_loop().time()
                        if now - start_time >= 1.0 or downloaded >= total_size:
                            await update_progress(msg, downloaded, total_size, start_time)
                            start_time = now

        # --- Upload (if <2GB; else notify) ---
        final_size = os.path.getsize(TEMP_FILE)
        await msg.edit(f"Download **complete** ({format_bytes(final_size)})! Uploading...")
        if final_size > 2 * 1024**3:
            await event.reply("File too big for Telegram (2GB limit). Saved locally!")
        else:
            await bot.send_file(
                event.chat_id,
                TEMP_FILE,
                caption="Your 4 GB Pokémon pack is here! 🌟",
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


# === Update Progress ===
async def update_progress(msg, downloaded: int, total: int, start_time: float):
    percent = (downloaded / total * 100) if total > 0 else 0
    bar = "█" * int(10 * (percent / 100)) + "░" * (10 - int(10 * (percent / 100)))
    elapsed = asyncio.get_event_loop().time() - start_time
    speed = downloaded / elapsed if elapsed > 0 else 0
    eta = (total - downloaded) / speed if speed > 0 and total > downloaded else 0
    eta_str = str(timedelta(seconds=int(eta))) if eta > 0 else "Done!"

    text = (
        f"Downloading **4 GB** Pokémon Pack...\n"
        f"```{bar} {percent:6.2f}% | "
        f"{format_bytes(downloaded)} / {format_bytes(total)} | "
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
    print("Bot running... /start = REAL 4GB download from 1Fichier")
    bot.run_until_disconnected()
