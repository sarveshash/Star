#!/usr/bin/env python3
# pokemon_bot_fake_8gb.py - FAKE 8GB Download with REAL-LOOKING Progress

import asyncio
import os
from datetime import timedelta
from telethon import TelegramClient, events, Button

# === CREDENTIALS ===
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8474337967:AAH_mbpp4z1nOTDGyoJrM5r0Rii-b_TUcvA"

# === FAKE DOWNLOAD CONFIG ===
FAKE_SIZE_GB = 8
CHUNK_SIZE = 1024 * 1024 * 10  # 10 MB per "chunk" (fake)
DELAY_PER_CHUNK = 0.8  # seconds per 10 MB → ~100 Mbps fake speed

# === Bot ===
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id
    total_bytes = FAKE_SIZE_GB * 1024**3  # 8 GB in bytes
    downloaded = 0
    start_time = asyncio.get_event_loop().time()
    cancel_flag = asyncio.Event()

    # --- Start message ---
    msg = await event.reply(
        f"Downloading **{FAKE_SIZE_GB:.2f} GB** Pokémon Data Pack...\n"
        "```[          ] 0.00% | 0 B / 8.00 GB | 0 B/s | ETA: --```",
        buttons=Button.inline("Cancel", b"cancel_fake")
    )

    # --- Cancel handler ---
    @bot.on(events.CallbackQuery(data=b"cancel_fake"))
    async def cancel_cb(cb):
        if cb.sender_id != user_id:
            return
        cancel_flag.set()
        await cb.answer("Cancelled!")
        await msg.edit("Download **cancelled**.")

    # --- Fake download loop ---
    try:
        while downloaded < total_bytes and not cancel_flag.is_set():
            # Simulate downloading a chunk
            chunk = min(CHUNK_SIZE, total_bytes - downloaded)
            downloaded += chunk
            await asyncio.sleep(DELAY_PER_CHUNK)  # Simulate network delay

            # Update progress
            await update_progress(msg, downloaded, total_bytes, start_time)

        if cancel_flag.is_set():
            return

        # --- Success: Send fake file ---
        await msg.edit("Download **complete**! Sending file...")
        
        # Create tiny fake file
        fake_file = "fake_8gb_pack.png"
        with open(fake_file, "wb") as f:
            f.write(b"PKMN")  # 4 bytes

        await bot.send_file(
            event.chat_id,
            fake_file,
            caption="Pokémon 8 GB Data Pack (compressed!) Ready!",
            reply_to=event.id
        )
        await msg.delete()

    except Exception as e:
        await msg.edit(f"Error: {e}")
    finally:
        if os.path.exists("fake_8gb_pack.png"):
            try:
                os.remove("fake_8gb_pack.png")
            except:
                pass


# === Update Progress (REAL MATH) ===
async def update_progress(msg, downloaded: int, total: int, start_time: float):
    percent = downloaded / total
    bar = "█" * int(10 * percent) + "░" * (10 - int(10 * percent))
    elapsed = asyncio.get_event_loop().time() - start_time
    speed = downloaded / elapsed if elapsed > 0 else 0
    eta = (total - downloaded) / speed if speed > 0 else 0
    eta_str = str(timedelta(seconds=int(eta))) if eta > 0 else "--"

    text = (
        f"Downloading **8.00 GB** Pokémon Data Pack...\n"
        f"```{bar} {percent*100:6.2f}% | "
        f"{format_bytes(downloaded)} / 8.00 GB | "
        f"{format_bytes(speed)}/s | ETA: {eta_str}```"
    )
    try:
        await msg.edit(text, buttons=Button.inline("Cancel", b"cancel_fake"))
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
    print("Bot running... /start = FAKE 8GB download with REAL progress")
    bot.run_until_disconnected()
