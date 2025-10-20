from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeAnimated
from PIL import Image, ImageSequence
import tempfile
import os

# Bot credentials
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8474337967:AAH_mbpp4z1nOTDGyoJrM5r0Rii-b_TUcvA"

# Initialize the bot
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle /start command and send modified GIF with black background"""

    gif_path = "swoobat-s.gif"

    try:
        with Image.open(gif_path) as im:
            original_width, original_height = im.size

            # Add padding (e.g., 100 pixels total - 50 on each side)
            padding = 50
            bg_width = original_width #+ (2 * padding)
            bg_height = original_height #+ (2 * padding)

            frames = []
            durations = []

            for frame in ImageSequence.Iterator(im):
                # Create black background
                background = Image.new('RGB', (bg_width, bg_height), color='black')

                # Convert frame to RGBA to handle transparency
                frame_rgba = frame.convert('RGBA')

                # Center the original frame
                x = (bg_width - original_width) // 2
                y = (bg_height - original_height) // 2

                # Paste the frame with transparency onto the black background
                background.paste(frame_rgba, (x, y), frame_rgba)

                # Convert to palette mode for GIF saving
                frames.append(background.convert('P', palette=Image.ADAPTIVE))
                durations.append(frame.info.get('duration', 100))  # Default 100ms

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as temp_file:
                temp_filename = temp_file.name
                frames[0].save(
                    temp_filename,
                    format='GIF',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=0
                )

            # Send the GIF
            await event.respond(
                file=temp_filename,
                attributes=[DocumentAttributeAnimated()]
            )

            os.remove(temp_filename)

    except FileNotFoundError:
        await event.respond("GIF file not found. Please check the file path.")
    except Exception as e:
        await event.respond(f"Error processing GIF: {str(e)}")

# Start the bot
print("Bot is running...")
bot.run_until_disconnected()
                
