from PIL import Image, ImageSequence
import os

# Input GIF path (in your repo folder)
input_path = "giftest.gif"  # adjust if in subfolder
output_path = "giftest_transparent.gif"

# Background color to remove (#0ECD42)
bg_color = (14, 205, 66)

# Open GIF
im = Image.open(input_path)
frames = []

for frame in ImageSequence.Iterator(im):
    frame = frame.convert("RGBA")
    new_data = [
        (0, 0, 0, 0) if pixel[:3] == bg_color else pixel
        for pixel in frame.getdata()
    ]
    frame.putdata(new_data)
    frames.append(frame)

# Save new transparent GIF
frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0, transparency=0, disposal=2)

print(f"✅ Transparent GIF saved at: {os.path.abspath(output_path)}")
