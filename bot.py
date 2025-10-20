from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeAnimated
from PIL import Image, ImageSequence
import tempfile
import os
import requests

# Bot credentials
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8474337967:AAH_mbpp4z1nOTDGyoJrM5r0Rii-b_TUcvA"

# Initialize the bot
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle /start command and send modified GIF with black background and resized smaller"""

    gif_url = "https://www.pkparaiso.com/imagenes/espada_escudo/sprites/animados-gigante/swoobat-s.gif"

    try:
        # Download the GIF
        response = requests.get(gif_url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as downloaded_file:
            downloaded_file.write(response.content)
            downloaded_gif_path = downloaded_file.name

        scale_factor = 4  # Resize factor: 4 means 1/4 the original size

        with Image.open(downloaded_gif_path) as im:
            original_width, original_height = im.size

            new_width = original_width // scale_factor
            new_height = original_height // scale_factor

            frames = []
            durations = []

            for frame in ImageSequence.Iterator(im):
                # Create black background with alpha channel
                background = Image.new('RGBA', (new_width, new_height), color=(0, 0, 0, 255))

                # Convert frame to RGBA for transparency support
                frame_rgba = frame.convert('RGBA')

                # Resize the frame to the smaller size
                frame_resized = frame_rgba.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Paste resized frame onto black background with transparency mask
                background.paste(frame_resized, (0, 0), frame_resized)

                # Convert to palette mode for GIF saving
                frames.append(background.convert('P', palette=Image.ADAPTIVE))

                # Save frame duration (default to 100ms)
                durations.append(frame.info.get('duration', 100))

        # Save modified GIF to temp file
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as modified_file:
            modified_gif_path = modified_file.name

        frames[0].save(
            modified_gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            disposal=2  # Proper disposal for transparency
        )

        # Send the resized GIF with black background
        await event.respond(
            file=modified_gif_path,
            attributes=[DocumentAttributeAnimated()]
        )

        # Clean up temp files
        os.remove(downloaded_gif_path)
        os.remove(modified_gif_path)

    except requests.exceptions.RequestException as e:
        await event.respond(f"Failed to download GIF: {str(e)}")
    except Exception as e:
        await event.respond(f"Error processing GIF: {str(e)}")

# Start the bot
print("Bot is running...")
bot.run_until_disconnected()
