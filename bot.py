from PIL import Image
import os

# Folder containing your PNG sequence
input_folder = "/root/Star"
output_folder = os.path.join(input_folder, "processed")

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

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
    
    # Save to output folder with same name
    img.save(os.path.join(output_folder, file))

print(f"✅ Background removed. Processed images saved in: {output_folder}")
