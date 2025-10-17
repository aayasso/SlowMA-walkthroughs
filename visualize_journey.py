from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
import os

def visualize_journey(journey_file, image_file, output_file="journey_visual.jpg"):
    """Create a visual showing all the highlighted regions"""
    
    # Load journey data
    journey_data = json.loads(Path(journey_file).read_text())
    
    # Load image
    img = Image.open(image_file)
    width, height = img.size
    
    # Create a copy to draw on
    visual = img.copy()
    draw = ImageDraw.Draw(visual, 'RGBA')
    
    # Colors for each step
    colors = [
        (255, 0, 0, 100),      # Red
        (0, 255, 0, 100),      # Green
        (0, 0, 255, 100),      # Blue
        (255, 255, 0, 100),    # Yellow
        (255, 0, 255, 100),    # Magenta
        (0, 255, 255, 100),    # Cyan
    ]
    
    print(f"\n🎨 {journey_data['artwork']['title']}")
    print(f"   by {journey_data['artwork']['artist']}")
    print("\n📍 Visualizing {0} regions:\n".format(len(journey_data['steps'])))
    
    # Draw each region
    for i, step in enumerate(journey_data['steps']):
        region = step['region']
        
        # Convert normalized coordinates to pixel coordinates
        x = int(region['x'] * width)
        y = int(region['y'] * height)
        w = int(region['width'] * width)
        h = int(region['height'] * height)
        
        # Draw semi-transparent rectangle
        color = colors[i % len(colors)]
        draw.rectangle([x, y, x + w, y + h], outline=color[:3], width=5, fill=color)
        
        # Draw step number
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        except:
            font = ImageFont.load_default()
        
        # Draw number with background
        text = str(step['step_number'])
        bbox = draw.textbbox((x + 10, y + 10), text, font=font)
        draw.rectangle(bbox, fill=(255, 255, 255, 200))
        draw.text((x + 10, y + 10), text, fill=color[:3], font=font)
        
        print(f"  Step {step['step_number']}: {region['title']}")
        print(f"    Position: ({region['x']:.2f}, {region['y']:.2f})")
        print(f"    Size: {region['width']:.2f} × {region['height']:.2f}")
        print()
    
    # Save the visualization
    visual.save(output_file, quality=95)
    print(f"✓ Visual saved to: {output_file}")
    print(f"  Open it to see all highlighted regions!\n")
    
    # Open the file automatically
    os.system(f'open "{output_file}"')

if __name__ == "__main__":
    # Use your actual files
    visualize_journey(
        "user_library/skull-cigarette-vanitas-001.json",
        "2B--glory%20days.jpg",
        "journey_visual.jpg"
    )