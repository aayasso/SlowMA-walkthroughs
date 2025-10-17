"""
EASY ARTWORK TESTER
Just put your artwork images in the project folder and run this script!
"""

from pathlib import Path
from slow_looking import SlowLookingAnalyzer, JourneyLibrary
import json
from PIL import Image, ImageDraw, ImageFont
import os

def test_artwork():
    """
    Simple workflow:
    1. Shows you all available images
    2. You pick one by number
    3. Analyzes it
    4. Shows you readable text
    5. Creates visual with highlighted regions
    6. Opens the visual automatically
    """
    
    # Find all images
    print("\n" + "="*60)
    print("AVAILABLE ARTWORK IMAGES")
    print("="*60)
    
    images = []
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp"]:
        images.extend(Path(".").glob(ext))
    
    if not images:
        print("\n❌ No images found in this folder!")
        print("   Add some .jpg or .png files and try again.\n")
        return
    
    for i, img in enumerate(images, 1):
        print(f"  {i}. {img.name}")
    
    # Get user choice
    print("\n" + "-"*60)
    choice = input("Enter number (or press Enter for #1): ").strip()
    
    if choice == "":
        selected = images[0]
    else:
        try:
            idx = int(choice) - 1
            selected = images[idx]
        except (ValueError, IndexError):
            print("❌ Invalid choice!")
            return
    
    print(f"\n🎨 Testing: {selected.name}")
    print("="*60)
    
    # Initialize
    analyzer = SlowLookingAnalyzer(cache_dir=Path("journeys_cache"))
    library = JourneyLibrary(library_dir=Path("user_library"))
    
    # Create journey
    print("\n⏳ Analyzing artwork (this takes 10-30 seconds)...")
    journey = analyzer.create_journey(selected)
    library.save_journey(journey)
    
    # Print readable version
    print_journey(journey)
    
    # Create visual
    print("\n🖼️  Creating visual with highlighted regions...")
    visual_file = f"{selected.stem}_visual.jpg"
    create_visual(journey, selected, visual_file)
    
    # Save text version
    text_file = f"{selected.stem}_readable.txt"
    save_text(journey, text_file)
    
    print("\n" + "="*60)
    print("✅ COMPLETE!")
    print("="*60)
    print(f"📄 Text version: {text_file}")
    print(f"🖼️  Visual: {visual_file} (should open automatically)")
    print("\nTo test another artwork, just run this script again!\n")


def print_journey(journey):
    """Print journey in readable format"""
    
    print("\n" + "="*70)
    print("JOURNEY PREVIEW")
    print("="*70)
    
    art = journey.artwork
    print(f"\n🎨 {art.title or 'Untitled'}")
    if art.artist:
        print(f"   by {art.artist}")
    
    print(f"\n📍 {journey.total_steps} steps • ~{journey.estimated_duration_minutes} min • {journey.confidence_score:.0%} confidence")
    
    print(f"\n💭 WELCOME")
    print(f"   {journey.welcome_text}")
    
    print("\n" + "-"*70)
    print("JOURNEY STEPS")
    print("-"*70)
    
    for step in journey.steps:
        region = step.region
        print(f"\n📍 STEP {step.step_number}: {region.title}")
        print(f"   ⏱️  Look away: {step.look_away_duration}s")
        print(f"   💭 \"{region.soft_prompt}\"")
        print(f"\n   {region.observation}")
        print(f"\n   💡 Why: {region.why_notable}")
    
    print("\n" + "-"*70)
    print("FINAL SUMMARY")
    print("-"*70)
    
    summary = journey.final_summary
    print(f"\n🎯 {summary.main_takeaway}")
    print(f"\n🔗 {summary.connections}")
    print(f"\n❓ {summary.reflection_question}")


def create_visual(journey, image_path, output_file):
    """Create visual with highlighted regions"""
    
    img = Image.open(image_path)
    width, height = img.size
    visual = img.copy()
    draw = ImageDraw.Draw(visual, 'RGBA')
    
    colors = [
        (255, 50, 50, 80),      # Red
        (50, 255, 50, 80),      # Green
        (50, 50, 255, 80),      # Blue
        (255, 255, 50, 80),     # Yellow
        (255, 50, 255, 80),     # Magenta
        (50, 255, 255, 80),     # Cyan
    ]
    
    for i, step in enumerate(journey.steps):
        region = step.region
        
        # Convert normalized coordinates to pixels
        x = int(region.x * width)
        y = int(region.y * height)
        w = int(region.width * width)
        h = int(region.height * height)
        
        # Draw rectangle
        color = colors[i % len(colors)]
        draw.rectangle([x, y, x + w, y + h], outline=color[:3], width=6, fill=color)
        
        # Draw step number
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
        except:
            font = ImageFont.load_default()
        
        text = str(step.step_number)
        
        # Background for number
        bbox = draw.textbbox((x + 15, y + 15), text, font=font)
        padding = 5
        draw.rectangle(
            [bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding],
            fill=(255, 255, 255, 220)
        )
        
        # Draw number
        draw.text((x + 15, y + 15), text, fill=color[:3], font=font)
    
    visual.save(output_file, quality=95)
    print(f"   ✓ Saved: {output_file}")
    
    # Open automatically
    os.system(f'open "{output_file}"')


def save_text(journey, output_file):
    """Save readable text version"""
    
    lines = []
    lines.append("="*70)
    lines.append("SLOW LOOKING JOURNEY")
    lines.append("="*70)
    lines.append("")
    
    art = journey.artwork
    lines.append(f"🎨 {art.title or 'Untitled'}")
    if art.artist:
        lines.append(f"   by {art.artist}")
    if art.year:
        lines.append(f"   {art.year}")
    lines.append("")
    
    lines.append(f"📍 {journey.total_steps} steps • ~{journey.estimated_duration_minutes} minutes")
    lines.append(f"   Confidence: {journey.confidence_score:.0%}")
    lines.append("")
    
    lines.append("💭 WELCOME")
    lines.append(f"   {journey.welcome_text}")
    lines.append("")
    lines.append("-"*70)
    
    for step in journey.steps:
        region = step.region
        lines.append("")
        lines.append(f"STEP {step.step_number}: {region.title.upper()}")
        lines.append("="*70)
        lines.append("")
        lines.append(f"⏱️  LOOK AWAY: {step.look_away_duration} seconds")
        lines.append(f"   While looking at the artwork:")
        lines.append(f"   \"{region.soft_prompt}\"")
        lines.append("")
        lines.append(f"👁️  OBSERVATION")
        lines.append(f"   {region.observation}")
        lines.append("")
        lines.append(f"💡 WHY THIS MATTERS")
        lines.append(f"   {region.why_notable}")
        lines.append("")
        if step.builds_on:
            lines.append(f"🔗 BUILDS ON")
            lines.append(f"   {step.builds_on}")
            lines.append("")
        lines.append(f"📊 Concept: {region.concept_tag} • Importance: {region.importance}/10")
        lines.append("")
        lines.append("-"*70)
    
    summary = journey.final_summary
    lines.append("")
    lines.append("FINAL SUMMARY")
    lines.append("="*70)
    lines.append("")
    lines.append("🎯 MAIN TAKEAWAY")
    lines.append(f"   {summary.main_takeaway}")
    lines.append("")
    lines.append("🔗 CONNECTIONS")
    lines.append(f"   {summary.connections}")
    lines.append("")
    lines.append("↩️  INVITATION")
    lines.append(f"   {summary.invitation_to_return}")
    lines.append("")
    lines.append("❓ REFLECTION")
    lines.append(f"   {summary.reflection_question}")
    lines.append("")
    lines.append("="*70)
    
    Path(output_file).write_text("\n".join(lines))
    print(f"   ✓ Saved: {text_file}")


if __name__ == "__main__":
    test_artwork()