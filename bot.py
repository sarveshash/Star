#!/usr/bin/env python3
# pokemon_bot.py - Telethon + 10GB Download + REAL Progress (No HTTP Errors)

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
DOWNLOAD_URL = "http://ipv4.download.thinkbroadband.com/10GB.zip"  # ← NEW 10GB FILE! (Reliable)
CHUNK_SIZE = 1024 * 1024  # 1 MB
TEMP_FILE = "downloaded_file.tmp"

# === Bot ===
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id

    # --- Try to get size via HEAD (optional, with longer timeout) ---
    total_size = None
    async with aiohttp.ClientSession() as session:
        try:
            async with session.head(DOWNLOAD_URL, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                print(f"HEAD Status: {resp.status}")  # Debug log
                if resp.status == 200:
                    total_size = int(resp.headers.get("content-length", 0))
                    print(f"Detected size: {total_size} bytes")  # Debug
                elif resp.status == 403:
                    await event.reply("Server blocked access (403). Try later.")
                    return
                elif resp.status >= 400:
                    await event.reply(f"HTTP Error {resp.status} from server.")
                    return
        except asyncio.TimeoutError:
            print("HEAD timed out — proceeding without size.")
        except Exception as e:
            print(f"HEAD failed: {e}")  # Debug
            pass  # Ignore — stream download anyway

    # --- Start message ---
    size_str = format_bytes(total_size) if total_size else "Large file"
    msg = await event.reply(
        f"Downloading **{size_str}** (Pokémon Data Pack)...\n"
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
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=None, sock_read=300)  # No total timeout, 5min read
        ) as session:
            async with session.get(DOWNLOAD_URL, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                print(f"GET Status: {resp.status}")  # Debug
                if resp.status != 200:
                    await msg.edit(f"Download failed (HTTP {resp.status}). Server issue.")
                    return

                # Detect size during GET if missed in HEAD
                if not detected_size and "content-length" in resp.headers:
                    detected_size = int(resp.headers["content-length"])
                    print(f"Detected size during GET: {detected_size}")

                with open(TEMP_FILE, "wb") as f:
                    async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                        if cancel_flag.is_set():
                            return

                        f.write(chunk)
                        downloaded += len(chunk)

                        # Update every 1 sec
                        now = asyncio.get_event_loop().time()
                        if now - start_time >= 1.0:
                            # Use downloaded as "total" if unknown (indefinite progress)
                            display_total = detected_size or downloaded
                            await update_progress(msg, downloaded, display_total, start_time)
                            start_time = now

        # --- Success: Upload ---
        final_size = os.path.getsize(TEMP_FILE)
        await msg.edit(f"Download **complete** ({format_bytes(final_size)})! Uploading...")
        await bot.send_file(
            event.chat_id,
            TEMP_FILE,
            caption="Your massive Pokémon data pack is here! 🌟",
            reply_to=event.id
        )
        await msg.delete()

    except asyncio.TimeoutError:
        await msg.edit("Download timed out. Server too slow?")
    except Exception as e:
        print(f"Download error: {e}")  # Debug
        await msg.edit(f"Error: {e}")
    finally:
        if os.path.exists(TEMP_FILE):
            try:
                os.remove(TEMP_FILE)
            except:
                pass


# === Update Progress UI ===
async def update_progress(msg, downloaded: int, total: int, start_time: float):
    percent = (downloaded / total * 100) if total > downloaded else 100
    bar = "█" * int(10 * (percent / 100)) + "░" * (10 - int(10 * (percent / 100)))
    elapsed = asyncio.get_event_loop().time() - start_time
    speed = downloaded / elapsed if elapsed > 0 else 0
    eta = (total - downloaded) / speed if speed > 0 and total > downloaded else 0
    eta_str = str(timedelta(seconds=int(eta))) if eta > 0 else "Done!"

    total_str = format_bytes(total) if total > 0 else format_bytes(downloaded)

    text = (
        f"Downloading **Large file** (Pokémon Pack)...\n"
        f"```{bar} {percent:6.2f}% | "
        f"{format_bytes(downloaded)} / {total_str} | "
        f"{format_bytes(speed)}/s | ETA: {eta_str}```"
    )
    try:
        await msg.edit(text, buttons=Button.inline("Cancel", b"cancel_download"))
    except:
        pass  # Ignore flood


# === Format Bytes ===
def format_bytes(b):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024:
            return f"{b:.2f} {unit}"
        b /= 1024
    return f"{b:.2f} PB"


# === Run ===
if __name__ == "__main__":
    print("Bot running... /start = 10GB download with REAL progress (check console for debug)")
    bot.run_until_disconnected()
