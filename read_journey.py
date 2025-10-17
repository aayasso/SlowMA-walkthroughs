from pathlib import Path
import json

def format_journey_readable(journey_file, output_file="journey_readable.txt"):
    """Convert journey JSON to beautiful readable text"""
    
    journey = json.loads(Path(journey_file).read_text())
    
    output = []
    output.append("=" * 70)
    output.append("SLOW LOOKING JOURNEY")
    output.append("=" * 70)
    output.append("")
    
    # Artwork info
    art = journey['artwork']
    output.append(f"🎨 ARTWORK")
    output.append(f"   Title: {art['title'] or 'Unknown'}")
    output.append(f"   Artist: {art['artist'] or 'Unknown'}")
    if art['year']:
        output.append(f"   Year: {art['year']}")
    if art['style']:
        output.append(f"   Style: {art['style']}")
    output.append("")
    
    # Journey overview
    output.append(f"📍 JOURNEY OVERVIEW")
    output.append(f"   Duration: ~{journey['estimated_duration_minutes']} minutes")
    output.append(f"   Steps: {journey['total_steps']} observations")
    output.append(f"   Confidence: {journey['confidence_score']:.0%}")
    output.append("")
    
    # Welcome
    output.append(f"💭 WELCOME")
    output.append(f"   {journey['welcome_text']}")
    output.append("")
    output.append("-" * 70)
    
    # Each step
    for step in journey['steps']:
        region = step['region']
        
        output.append("")
        output.append(f"STEP {step['step_number']}: {region['title'].upper()}")
        output.append("=" * 70)
        output.append("")
        
        output.append(f"⏱️  LOOK AWAY: {step['look_away_duration']} seconds")
        output.append("")
        output.append(f"   While looking at the artwork, consider:")
        output.append(f"   \"{region['soft_prompt']}\"")
        output.append("")
        
        output.append(f"👁️  OBSERVATION")
        output.append(f"   {region['observation']}")
        output.append("")
        
        output.append(f"💡 WHY THIS MATTERS")
        output.append(f"   {region['why_notable']}")
        output.append("")
        
        if step['builds_on']:
            output.append(f"🔗 CONNECTION")
            output.append(f"   {step['builds_on']}")
            output.append("")
        
        output.append(f"📊 CONCEPT: {region['concept_tag']}")
        output.append(f"   Importance: {region['importance']}/10")
        output.append("")
        output.append("-" * 70)
    
    # Final summary
    output.append("")
    output.append("FINAL SUMMARY")
    output.append("=" * 70)
    output.append("")
    
    summary = journey['final_summary']
    
    output.append("🎯 MAIN TAKEAWAY")
    output.append(f"   {summary['main_takeaway']}")
    output.append("")
    
    output.append("🔗 HOW IT ALL CONNECTS")
    output.append(f"   {summary['connections']}")
    output.append("")
    
    output.append("↩️  INVITATION TO RETURN")
    output.append(f"   {summary['invitation_to_return']}")
    output.append("")
    
    output.append("❓ REFLECTION QUESTION")
    output.append(f"   {summary['reflection_question']}")
    output.append("")
    
    output.append("=" * 70)
    
    # Write to file
    text = "\n".join(output)
    Path(output_file).write_text(text)
    
    # Also print to terminal
    print(text)
    
    print(f"\n✓ Readable version saved to: {output_file}")
    print(f"  You can open this in any text editor!\n")

if __name__ == "__main__":
    format_journey_readable(
        "user_library/2B--glory%20days.jpg.json",
        "journey_readable.txt"
    )