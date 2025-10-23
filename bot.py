from PIL import Image
import os

# Folder containing your PNG sequence (directly in /root/Star/)
input_folder = "/root/Star"

# Background color to remove (#0ECD42)
bg_color = (14, 205, 66)

# Get list of PNG files
png_files = sorted([f for f in os.listdir(input_folder) if f.endswith(".png")])

for file in png_files:
    path = os.path.join(input_folder, file)
    img = Image.open(path).convert("RGBA")
    
    # Remove background
    new_data = [
        (0, 0, 0, 0) if pixel[:3] == bg_color else pixel
        for pixel in img.getdata()
    ]
    img.putdata(new_data)
    
    # Save with same name, overwrite original
    img.save(path)

print("✅ Background removed from all images in", input_folder)
