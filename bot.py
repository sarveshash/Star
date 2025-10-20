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
    """Handle /start command and send modified GIF with black background"""

    gif_url = "https://www.pkparaiso.com/imagenes/espada_escudo/sprites/animados-gigante/swoobat-s.gif"

    try:
        # Download the GIF
        response = requests.get(gif_url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as downloaded_file:
            downloaded_file.write(response.content)
            downloaded_gif_path = downloaded_file.name

        # Open and process the GIF
        with Image.open(downloaded_gif_path) as im:
            original_width, original_height = im.size

            frames = []
            durations = []

            for frame in ImageSequence.Iterator(im):
                # Create black background with integer size
                bg_width, bg_height = original_width // 2, original_height // 2
                background = Image.new('RGB', (bg_width, bg_height), color='black')

                # Convert frame to RGBA to handle transparency
                frame_rgba = frame.convert('RGBA')

                # Resize the frame to fit the new background size
                # Use Resampling.LANCZOS for high quality (replace old ANTIALIAS)
                frame_resized = frame_rgba.resize((bg_width, bg_height), Image.Resampling.LANCZOS)

                # Paste the resized frame with transparency onto the black background
                background.paste(frame_resized, (0, 0), frame_resized)

                # Convert to palette mode for GIF saving
                frames.append(background.convert('P', palette=Image.ADAPTIVE))
                durations.append(frame.info.get('duration', 100))  # Default 100ms

            # Save modified GIF to temp file
            with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as modified_file:
                modified_gif_path = modified_file.name
                frames[0].save(
                    modified_gif_path,
                    format='GIF',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=0
                )

            # Send the GIF
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
