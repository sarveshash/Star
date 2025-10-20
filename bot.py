from telethon import TelegramClient, events
from PIL import Image, ImageSequence
import io

# Bot credentials
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8474337967:AAH_mbpp4z1nOTDGyoJrM5r0Rii-b_TUcvA"

# Initialize the bot
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle /start command with GIF processing"""
    
    # Path to your original GIF file
    original_gif_path = "your_gif_file.gif"  # Replace with your GIF file path
    
    try:
        # Open the original GIF
        with Image.open(original_gif_path) as im:
            # Get original dimensions
            original_width, original_height = im.size
            
            # Calculate new dimensions (50% smaller)
            new_width = original_width // 2
            new_height = original_height // 2
            
            # Create blue background with new dimensions
            bg_width = new_width + 100  # Add padding
            bg_height = new_height + 100  # Add padding
            
            # Process all frames
            frames = []
            durations = []
            
            for frame in ImageSequence.Iterator(im):
                # Create blue background
                background = Image.new('RGB', (bg_width, bg_height), color='blue')
                
                # Resize the frame
                resized_frame = frame.convert('RGBA').resize(
                    (new_width, new_height), 
                    Image.Resampling.LANCZOS
                )
                
                # Calculate position to center the GIF on blue background
                x = (bg_width - new_width) // 2
                y = (bg_height - new_height) // 2
                
                # Paste resized frame onto blue background
                background.paste(resized_frame, (x, y), resized_frame)
                
                frames.append(background.convert('P', palette=Image.ADAPTIVE))
                
                # Get frame duration (default to 100ms if not specified)
                durations.append(frame.info.get('duration', 100))
            
            # Save processed GIF to bytes buffer
            output_buffer = io.BytesIO()
            frames[0].save(
                output_buffer,
                format='GIF',
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                optimize=False
            )
            output_buffer.seek(0)
            
            # Send the processed GIF
            await event.respond(
                file=output_buffer,
                caption="Welcome! 🎮"
            )
            
    except FileNotFoundError:
        await event.respond("GIF file not found. Please check the file path.")
    except Exception as e:
        await event.respond(f"Error processing GIF: {str(e)}")

# Start the bot
print("Bot is running...")
bot.run_until_disconnected()
