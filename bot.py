from PIL import Image
import os

# Folder containing your PNG sequence
input_folder = "/root/Star"  # change to your folder
output_gif = "/root/Star/final.gif"

# Background color to remove (#0ECD42)
bg_color = (14, 205, 66)

# Get list of PNG files sorted
png_files = sorted([f for f in os.listdir(input_folder) if f.endswith(".png")])

frames = []

for file in png_files:
    path = os.path.join(input_folder, file)
    img = Image.open(path).convert("RGBA")
    
    # Remove background
    data = [
        (0, 0, 0, 0) if pixel[:3] == bg_color else pixel
        for pixel in img.getdata()
    ]
    img.putdata(data)
    
    frames.append(img)

# Save as animated GIF
frames[0].save(
    output_gif,
    save_all=True,
    append_images=frames[1:],
    loop=0,
    duration=100,  # change duration per frame if needed (ms)
    transparency=0,
    disposal=2
)

print(f"✅ GIF created at: {output_gif}")
