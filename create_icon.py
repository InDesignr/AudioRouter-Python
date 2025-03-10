#!/usr/bin/env python3
"""
Create a simple icon for the Audio Router application
Uses Pillow to create a PNG icon
"""

import os
from PIL import Image, ImageDraw

def create_icon(output_path, size=128):
    """Create a simple audio router icon"""
    # Create a blank image with transparency
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Set colors
    background_color = (52, 152, 219)  # Blue
    foreground_color = (236, 240, 241)  # White/Light gray
    
    # Draw a circle as background
    circle_padding = size // 10
    draw.ellipse(
        [(circle_padding, circle_padding), 
         (size - circle_padding, size - circle_padding)],
        fill=background_color
    )
    
    # Draw audio router symbol (simplified headphones with routing arrow)
    # Headphone arc
    arc_width = size // 12
    arc_padding = size // 3
    draw.arc(
        [(arc_padding, arc_padding), 
         (size - arc_padding, size - arc_padding)],
        start=0, end=180,
        fill=foreground_color, width=arc_width
    )
    
    # Headphone left ear
    left_ear_x = arc_padding
    left_ear_y = size // 2
    ear_size = size // 5
    draw.ellipse(
        [(left_ear_x - ear_size//2, left_ear_y - ear_size//2),
         (left_ear_x + ear_size//2, left_ear_y + ear_size//2)],
        fill=foreground_color
    )
    
    # Headphone right ear
    right_ear_x = size - arc_padding
    right_ear_y = size // 2
    draw.ellipse(
        [(right_ear_x - ear_size//2, right_ear_y - ear_size//2),
         (right_ear_x + ear_size//2, right_ear_y + ear_size//2)],
        fill=foreground_color
    )
    
    # Arrow from bottom to middle (audio routing)
    arrow_width = size // 15
    arrow_head_size = size // 10
    
    # Arrow shaft
    draw.line(
        [(size // 2, size - circle_padding - arrow_width),
         (size // 2, size // 2)],
        fill=foreground_color, width=arrow_width
    )
    
    # Arrow head
    draw.polygon(
        [(size // 2 - arrow_head_size, size // 2 + arrow_head_size),
         (size // 2, size // 2 - arrow_head_size),
         (size // 2 + arrow_head_size, size // 2 + arrow_head_size)],
        fill=foreground_color
    )
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the image
    img.save(output_path)
    print(f"Icon created at: {output_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "audiorouter", "resources", "icon.png")
    create_icon(icon_path)
