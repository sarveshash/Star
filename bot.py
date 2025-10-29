from PIL import Image,ImageDraw
import numpy as np

def create_pokemon_gradient_background(width=640, height=360):
    """
    Create smooth gradient background matching Pokemon character selection screen.
    No dots - just clean gradient.
    """
    # Create new RGB image
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    # COLOR CODES
    top_color = np.array([9, 48, 87], dtype=float)      # RGB(9, 48, 87) - Medium blue
    mid_color = np.array([1, 3, 28], dtype=float)       # RGB(1, 3, 28) - Dark navy
    bottom_color = np.array([28, 66, 104], dtype=float) # RGB(28, 66, 104) - Lighter blue
    
    mid_point = height * 0.5  # Gradient middle at 50% height
    
    # Create smooth vertical gradient
    for y in range(height):
        if y < mid_point:
            # Top to middle transition
            t = y / mid_point
            color = top_color * (1 - t) + mid_color * t
        else:
            # Middle to bottom transition
            t = (y - mid_point) / (height - mid_point)
            color = mid_color * (1 - t) + bottom_color * t
        
        r, g, b = int(round(color[0])), int(round(color[1])), int(round(color[2]))
        
        # Fill entire row with calculated color
        for x in range(width):
            pixels[x, y] = (r, g, b)
    
    return img


# MAIN EXECUTION
if __name__ == "__main__":
    # Create clean gradient background (no dots)
    background = create_pokemon_gradient_background(640, 360)
    
    # Save file
    background.save('pokemon_background_clean.png')
    
    print("✓ Clean Pokemon background created!")
    print("✓ Saved as: pokemon_background_clean.png")
    print(f"  Size: {background.size}")
    print("  No dots - just smooth gradient")

def add_star_dots(img, density=0.004, seed=42):
    """
    Add star dot pattern overlay to background.
    """
    width, height = img.size
    draw = ImageDraw.Draw(img)
    
    np.random.seed(seed)
    num_dots = int(width * height * density)
    
    for _ in range(num_dots):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        
        # Dot size (mostly 1px, some 2px)
        size = np.random.choice([1, 2], p=[0.75, 0.25])
        
        # Dot brightness (gray/white)
        brightness = np.random.randint(90, 140)
        color = (brightness, brightness, brightness)
        
        if size == 1:
            draw.point((x, y), fill=color)
        else:
            draw.ellipse([x-1, y-1, x+1, y+1], fill=color)
    
    return img


# MAIN EXECUTION
if __name__ == "__main__":
    # Create 640x360 background with gradient
    background = create_pokemon_gradient_background(640, 360)
    
    # Add star pattern
    background = add_star_dots(background, density=0.004)
    
    # Save in current directory on VPS
    background.save('pokemon_background.png')
    
    print("✓ Pokemon background created successfully!")
    print("✓ Saved as: pokemon_background.png")
    print(f"  Size: {background.size}")
    print(f"  Colors: Top RGB(9,48,87) → Mid RGB(1,3,28) → Bottom RGB(28,66,104)")
