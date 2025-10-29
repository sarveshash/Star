from PIL import Image
import numpy as np

def create_pokemon_gradient_background(width=640, height=360, dark_spread=0.5):
    """
    Create smooth gradient background with adjustable dark area spread.
    
    Args:
        width: Image width
        height: Image height
        dark_spread: How much area stays dark (0.3=narrow, 0.5=normal, 0.7=wide)
                    Higher value = larger dark area in center
    """
    # Create new RGB image
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    # COLOR CODES
    top_color = np.array([9, 48, 87], dtype=float)      # RGB(9, 48, 87) - Medium blue
    mid_color = np.array([1, 3, 28], dtype=float)       # RGB(1, 3, 28) - Dark navy
    bottom_color = np.array([28, 66, 104], dtype=float) # RGB(28, 66, 104) - Lighter blue
    
    # Calculate dark region boundaries
    center = height * 0.5
    dark_height = height * dark_spread
    
    dark_start = center - (dark_height / 2)
    dark_end = center + (dark_height / 2)
    
    # Create smooth vertical gradient
    for y in range(height):
        if y < dark_start:
            # Top to dark start
            t = y / dark_start if dark_start > 0 else 0
            color = top_color * (1 - t) + mid_color * t
        elif y <= dark_end:
            # Inside dark region - stays dark
            color = mid_color
        else:
            # Dark end to bottom
            remaining = height - dark_end
            t = (y - dark_end) / remaining if remaining > 0 else 0
            color = mid_color * (1 - t) + bottom_color * t
        
        r, g, b = int(round(color[0])), int(round(color[1])), int(round(color[2]))
        
        # Fill entire row with calculated color
        for x in range(width):
            pixels[x, y] = (r, g, b)
    
    return img


# MAIN EXECUTION - Adjust dark area spread here!
if __name__ == "__main__":
    # ADJUST THIS VALUE:
    # dark_spread: 0.3 = narrow dark area, 0.5 = normal, 0.6 = wider, 0.7 = very wide
    
    background = create_pokemon_gradient_background(
        width=640, 
        height=360,
        dark_spread=0.4  # Try 0.6, 0.65, or 0.7 for wider dark area
    )
    
    # Save file
    background.save('pokemon_background_clean.png')
    
    print("✓ Pokemon background with adjustable dark spread created!")
    print("✓ Saved as: pokemon_background_clean.png")
    print(f"  Size: {background.size}")
    print("To adjust dark area size:")
    print("  - dark_spread=0.4 (smaller dark area)")
    print("  - dark_spread=0.5 (normal)")
    print("  - dark_spread=0.6 (wider dark area)")
    print("  - dark_spread=0.7 (very wide dark area)")
