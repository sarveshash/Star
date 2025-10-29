from PIL import Image,ImageDraw
import numpy as np

def create_pokemon_gradient_background(width=640, height=360, dark_position=0.5, dark_intensity=1.0):
    """
    Create smooth gradient background with adjustable center darkness.
    
    Args:
        width: Image width
        height: Image height
        dark_position: Where the darkest point is (0.0=top, 1.0=bottom, 0.5=center)
                      Lower = darker area moves up, Higher = darker area moves down
        dark_intensity: How dark the center is (0.5=lighter, 1.0=normal, 1.5=darker)
    """
    # Create new RGB image
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    # COLOR CODES
    top_color = np.array([9, 48, 87], dtype=float)      # RGB(9, 48, 87) - Medium blue
    mid_color = np.array([1, 3, 28], dtype=float)       # RGB(1, 3, 28) - Dark navy
    bottom_color = np.array([28, 66, 104], dtype=float) # RGB(28, 66, 104) - Lighter blue
    
    # Apply dark intensity adjustment to middle color
    mid_color_adjusted = mid_color * dark_intensity
    mid_color_adjusted = np.clip(mid_color_adjusted, 0, 255)  # Keep within valid range
    
    # Calculate dark point position
    mid_point = height * dark_position
    
    # Create smooth vertical gradient
    for y in range(height):
        if y < mid_point:
            # Top to middle transition
            t = y / mid_point if mid_point > 0 else 0
            color = top_color * (1 - t) + mid_color_adjusted * t
        else:
            # Middle to bottom transition
            remaining = height - mid_point
            t = (y - mid_point) / remaining if remaining > 0 else 0
            color = mid_color_adjusted * (1 - t) + bottom_color * t
        
        r, g, b = int(round(color[0])), int(round(color[1])), int(round(color[2]))
        
        # Fill entire row with calculated color
        for x in range(width):
            pixels[x, y] = (r, g, b)
    
    return img


# MAIN EXECUTION - Easy adjustments here!
if __name__ == "__main__":
    # ADJUST THESE VALUES:
    # dark_position: 0.4 = darker area higher, 0.5 = center (default), 0.6 = darker area lower
    # dark_intensity: 0.7 = lighter center, 1.0 = normal (default), 1.3 = darker center
    
    background = create_pokemon_gradient_background(
        width=640, 
        height=360,
        dark_position=0.5,    # Try 0.4 to move dark up, 0.6 to move dark down
        dark_intensity=1.0    # Try 0.8 for lighter, 1.2 for darker
    )
    
    # Save file
    background.save('pokemon_background_clean.png')
    
    print("✓ Adjustable Pokemon background created!")
    print("✓ Saved as: pokemon_background_clean.png")
    print(f"  Size: {background.size}")
    print("
  To adjust:")
    print("  - dark_position: 0.4 (higher) | 0.5 (center) | 0.6 (lower)")
    print("  - dark_intensity: 0.8 (lighter) | 1.0 (normal) | 1.2 (darker)")
