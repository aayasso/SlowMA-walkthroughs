# ============================================================================
# SLOW LOOKING - ART EDUCATION TOOL
# Guided walkthrough architecture for mindful art appreciation
# ============================================================================

"""
Installation requirements:
pip install anthropic pydantic python-dotenv pillow

Create a .env file with:
ANTHROPIC_API_KEY=your_key_here
"""

import os
import json
import hashlib
import time
import base64
from pathlib import Path
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum
import uuid

from anthropic import Anthropic
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# DATA MODELS - SLOW LOOKING JOURNEY
# ============================================================================

class AnnotatedRegion(BaseModel):
    """A notable area in the artwork"""
    
    # Visual location (normalized 0-1 coordinates)
    x: float = Field(ge=0, le=1, description="Top-left x")
    y: float = Field(ge=0, le=1, description="Top-left y")
    width: float = Field(ge=0, le=1, description="Width")
    height: float = Field(ge=0, le=1, description="Height")
    
    # Educational content
    importance: float = Field(ge=1, le=10, description="Importance 1-10")
    title: str = Field(max_length=40, description="Brief title")
    
    # Rich description for this region
    observation: str = Field(
        min_length=80, 
        max_length=250,
        description="What to notice - encouraging and accessible"
    )
    
    why_notable: str = Field(
        min_length=50,
        max_length=200,
        description="Why this matters - informed but conversational"
    )
    
    soft_prompt: str = Field(
        max_length=100,
        description="Gentle guiding question or prompt during look-away time"
    )
    
    concept_tag: Literal["composition", "technique", "symbolism", "color", 
                         "light", "subject", "emotion", "context", "style"]


class WalkthroughStep(BaseModel):
    """A single moment in the slow looking journey"""
    
    step_number: int = Field(ge=1, description="Position in sequence")
    region: AnnotatedRegion
    
    # Pacing
    look_away_duration: int = Field(
        ge=30, 
        le=60,
        description="Seconds to look at artwork before reveal"
    )
    
    # Pedagogical reasoning
    why_this_sequence: str = Field(
        max_length=150,
        description="Why this observation comes at this point in the journey"
    )
    
    # Connection to previous steps
    builds_on: Optional[str] = Field(
        None,
        max_length=200,
        description="How this connects to what came before"
    )


class ArtworkMetadata(BaseModel):
    """Basic artwork information"""
    title: Optional[str] = None
    artist: Optional[str] = None
    year: Optional[str] = None
    period: Optional[str] = None
    style: Optional[str] = None
    medium: Optional[str] = None


class FinalSummary(BaseModel):
    """Closing synthesis of the journey"""
    
    main_takeaway: str = Field(
        min_length=100,
        max_length=300,
        description="The key insight from this slow looking experience"
    )
    
    connections: str = Field(
        min_length=150,
        max_length=400,
        description="How the observations connect and build on each other"
    )
    
    invitation_to_return: str = Field(
        max_length=150,
        description="Encouraging prompt to look again or explore further"
    )
    
    reflection_question: str = Field(
        max_length=100,
        description="Open-ended question for continued contemplation"
    )


class SlowLookingJourney(BaseModel):
    """Complete guided walkthrough experience"""
    
    # Unique identifier for saving/loading
    journey_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Artwork info
    artwork: ArtworkMetadata
    image_filename: str
    
    # Journey structure
    total_steps: int = Field(ge=3, le=6)
    estimated_duration_minutes: int = Field(ge=3, le=8)
    
    # The sequential experience
    steps: List[WalkthroughStep] = Field(
        min_length=3,
        max_length=6,
        description="Ordered sequence of observations"
    )
    
    # Opening
    welcome_text: str = Field(
        max_length=200,
        description="Warm, inviting introduction to the experience"
    )
    
    # Closing
    final_summary: FinalSummary
    
    # Metadata
    created_at: str
    confidence_score: float = Field(ge=0, le=1)
    
    # Journey narrative
    pedagogical_approach: str = Field(
        max_length=200,
        description="The teaching strategy used for this artwork"
    )


# ============================================================================
# PROMPTS - SLOW LOOKING FOCUSED
# ============================================================================

SLOW_LOOKING_PROMPT = """You are an art educator designing a "slow looking" experience - a guided, mindful journey through an artwork that helps someone truly SEE and appreciate it deeply.

CONTEXT: This is a mobile app for museum visitors standing in front of artworks. Most people spend only 8 seconds looking at art. Your job is to create a 3-5 minute contemplative experience that transforms how they see.

TONE: Blend of Duolingo's encouraging style + mindful meditation + accessible art education
- Warm and inviting, never intimidating
- Curious and wondering, not lecturing
- Conversational but informed
- Encouraging small discoveries

YOUR TASK: Design a sequential journey of 3-6 observation "stops"

REQUIREMENTS:

1. DYNAMIC NUMBER OF STOPS (3-6)
   - Simple compositions: 3-4 stops
   - Rich, complex works: 5-6 stops
   - Quality over quantity - each stop must genuinely teach something

2. PEDAGOGICAL SEQUENCING
   - Order matters! Start with accessible observations, build to deeper insights
   - Each stop should naturally lead to the next
   - Create a narrative arc through the artwork
   - Consider: immediate → compositional → technical → symbolic → contextual

3. LOOK-AWAY TIMING (30-60 seconds per stop)
   - Longer for complex observations requiring careful looking
   - Shorter for immediate, visible elements
   - First stop often longer (60s) to settle into the experience

4. SOFT PROMPTS for look-away moments
   - Gentle, specific guidance: "Notice how the light touches different surfaces..."
   - NOT directive: "Look at the top left corner"
   - Contemplative, open: "What draws your eye first?"
   - Help them see without telling them what to see

5. REGION SELECTION
   - Focus on genuinely interesting details
   - Mix scales: overall composition + intimate details
   - Avoid trivial observations
   - Each region should create an "aha!" moment

6. WRITING STYLE for observations
   - Start with "Notice..." or "See how..." not "This is..."
   - Use vivid, sensory language
   - Ask gentle questions
   - Connect to universal human experience
   - Be specific about what to look for
   - Explain WHY it matters, not just WHAT it is

7. FINAL SUMMARY
   - Tie all observations together
   - Show how they built on each other
   - Leave them with a lasting insight
   - Invite them to return and look again

RESPONSE FORMAT: Valid JSON matching SlowLookingJourney schema

{
    "journey_id": "auto-generated",
    "artwork": {
        "title": "title or null",
        "artist": "artist or null", 
        "year": "year or null",
        "period": "period or null",
        "style": "style or null",
        "medium": "medium or null"
    },
    "image_filename": "provided by system",
    "total_steps": 3-6,
    "estimated_duration_minutes": 3-8,
    "steps": [
        {
            "step_number": 1,
            "region": {
                "x": 0.0-1.0,
                "y": 0.0-1.0,
                "width": 0.0-1.0,
                "height": 0.0-1.0,
                "importance": 1-10,
                "title": "brief title",
                "observation": "What to notice - 80-250 chars, encouraging and accessible",
                "why_notable": "Why this matters - 50-200 chars, informed but conversational",
                "soft_prompt": "Gentle question or prompt - max 100 chars",
                "concept_tag": "composition|technique|symbolism|color|light|subject|emotion|context|style"
            },
            "look_away_duration": 30-60,
            "why_this_sequence": "Why this observation comes now - max 150 chars",
            "builds_on": "Connection to previous steps or null"
        }
    ],
    "welcome_text": "Warm invitation to the experience - max 200 chars",
    "final_summary": {
        "main_takeaway": "Key insight from journey - 100-300 chars",
        "connections": "How observations connect - 150-400 chars",
        "invitation_to_return": "Encouraging prompt - max 150 chars",
        "reflection_question": "Open question for contemplation - max 100 chars"
    },
    "created_at": "ISO timestamp",
    "confidence_score": 0.0-1.0,
    "pedagogical_approach": "Teaching strategy used - max 200 chars"
}

EXAMPLES OF GOOD STOPS:

❌ BAD: "This is a portrait of a woman."
✅ GOOD: "Notice how her gaze doesn't quite meet ours - she's looking just past us, creating a sense of mystery and distance. This tiny detail transforms her from subject to enigma."

❌ BAD: "The artist used complementary colors."
✅ GOOD: "See the vibrant orange against that deep blue? These colors intensify each other, making both feel more alive. Your eye naturally bounces between them, creating visual energy."

❌ BAD: "There is interesting brushwork here."
✅ GOOD: "Look closely at these thick, visible brushstrokes - you can almost feel the artist's hand moving. Instead of hiding the paint, they're celebrating it, inviting you to see both the image AND the act of painting."

Remember: You're teaching someone to LOOK, not just telling them facts. Create moments of genuine discovery."""


# ============================================================================
# JOURNEY ANALYZER
# ============================================================================

class SlowLookingAnalyzer:
    """Creates guided slow looking journeys through artworks"""
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[Path] = None):
        """
        Initialize the analyzer
        
        Args:
            api_key: Anthropic API key
            cache_dir: Directory for caching journeys
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY required")
        
        self.client = Anthropic(api_key=self.api_key)
        self.cache_dir = cache_dir or Path("journeys_cache")
        self.cache_dir.mkdir(exist_ok=True)
    
    def _encode_image(self, image_path: Path) -> tuple[str, str]:
        """Encode image to base64"""
        suffix = image_path.suffix.lower()
        media_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        media_type = media_type_map.get(suffix, "image/jpeg")
        image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")
        return media_type, image_data
    
    def _get_cache_key(self, image_path: Path) -> str:
        """Generate cache key from image content"""
        return hashlib.md5(image_path.read_bytes()).hexdigest()
    
    def create_journey(
        self, 
        image_path: Path,
        use_cache: bool = True
    ) -> SlowLookingJourney:
        """
        Create a slow looking journey for an artwork
        
        Args:
            image_path: Path to artwork image
            use_cache: Whether to use cached journey
            
        Returns:
            SlowLookingJourney with complete guided experience
        """
        
        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(image_path)
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                print(f"✓ Using cached journey for {image_path.name}")
                data = json.loads(cache_file.read_text())
                return SlowLookingJourney(**data)
        
        print(f"🎨 Creating slow looking journey for {image_path.name}...")
        
        # Encode image
        media_type, image_data = self._encode_image(image_path)
        
        # Call Claude API
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8192,
                temperature=0.7,  # Slightly creative for engaging writing
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": SLOW_LOOKING_PROMPT
                            }
                        ],
                    }
                ],
            )
            
            # Extract response
            response_text = response.content[0].text
            
            # Parse JSON (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            journey_data = json.loads(response_text.strip())
            
            # Add system fields
            journey_data["image_filename"] = image_path.name
            journey_data["created_at"] = datetime.now().isoformat()
            
            # Create Pydantic model
            journey = SlowLookingJourney(**journey_data)
            
            # Cache the result
            cache_key = self._get_cache_key(image_path)
            cache_file = self.cache_dir / f"{cache_key}.json"
            cache_file.write_text(journey.model_dump_json(indent=2))
            
            print(f"✓ Journey created: {journey.total_steps} steps, "
                  f"~{journey.estimated_duration_minutes} min "
                  f"(confidence: {journey.confidence_score:.0%})")
            
            return journey
            
        except Exception as e:
            print(f"✗ Error creating journey: {e}")
            raise


# ============================================================================
# JOURNEY LIBRARY - Save & Retrieve Completed Walkthroughs
# ============================================================================

class JourneyLibrary:
    """Manage saved slow looking journeys"""
    
    def __init__(self, library_dir: Path = Path("user_library")):
        self.library_dir = library_dir
        self.library_dir.mkdir(exist_ok=True)
        self.index_file = library_dir / "_index.json"
        self._load_index()
    
    def _load_index(self):
        """Load library index"""
        if self.index_file.exists():
            self.index = json.loads(self.index_file.read_text())
        else:
            self.index = {"journeys": []}
    
    def _save_index(self):
        """Save library index"""
        self.index_file.write_text(json.dumps(self.index, indent=2))
    
    def save_journey(self, journey: SlowLookingJourney, completed_at: Optional[str] = None):
        """
        Save a completed journey to user's library
        
        Args:
            journey: The completed journey
            completed_at: Timestamp of completion (defaults to now)
        """
        completed_at = completed_at or datetime.now().isoformat()
        
        # Save full journey data
        journey_file = self.library_dir / f"{journey.journey_id}.json"
        journey_file.write_text(journey.model_dump_json(indent=2))
        
        # Update index
        index_entry = {
            "journey_id": journey.journey_id,
            "image_filename": journey.image_filename,
            "title": journey.artwork.title or "Untitled",
            "artist": journey.artwork.artist or "Unknown Artist",
            "completed_at": completed_at,
            "steps_count": journey.total_steps,
            "duration_minutes": journey.estimated_duration_minutes
        }
        
        # Check if already in index
        existing = [j for j in self.index["journeys"] if j["journey_id"] == journey.journey_id]
        if existing:
            # Update existing entry
            for j in self.index["journeys"]:
                if j["journey_id"] == journey.journey_id:
                    j.update(index_entry)
        else:
            # Add new entry
            self.index["journeys"].append(index_entry)
        
        self._save_index()
        print(f"✓ Journey saved to library: {journey.artwork.title or 'Untitled'}")
    
    def get_journey(self, journey_id: str) -> Optional[SlowLookingJourney]:
        """Retrieve a saved journey by ID"""
        journey_file = self.library_dir / f"{journey_id}.json"
        if not journey_file.exists():
            return None
        
        data = json.loads(journey_file.read_text())
        return SlowLookingJourney(**data)
    
    def list_journeys(self) -> List[dict]:
        """Get list of all saved journeys"""
        return sorted(
            self.index["journeys"], 
            key=lambda x: x["completed_at"], 
            reverse=True
        )
    
    def get_stats(self) -> dict:
        """Get library statistics"""
        return {
            "total_journeys": len(self.index["journeys"]),
            "total_steps": sum(j["steps_count"] for j in self.index["journeys"]),
            "total_minutes": sum(j["duration_minutes"] for j in self.index["journeys"]),
        }


# ============================================================================
# BATCH PROCESSOR FOR GALLERY
# ============================================================================

class GalleryPreprocessor:
    """Pre-process artworks for curated gallery"""
    
    def __init__(
        self, 
        analyzer: SlowLookingAnalyzer, 
        output_dir: Path = Path("gallery_journeys")
    ):
        self.analyzer = analyzer
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
    
    def process_gallery(self, artwork_dir: Path, delay_seconds: float = 2.0):
        """
        Process all artworks in directory
        
        Args:
            artwork_dir: Directory with artwork images
            delay_seconds: Delay between API calls
        """
        
        # Find images
        images = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp"]:
            images.extend(artwork_dir.glob(ext))
        
        if not images:
            print(f"No images found in {artwork_dir}")
            return
        
        print(f"\n{'='*60}")
        print(f"Creating {len(images)} slow looking journeys")
        print(f"{'='*60}\n")
        
        results = []
        
        for i, image_path in enumerate(images, 1):
            print(f"\n[{i}/{len(images)}] {image_path.name}")
            print("-" * 40)
            
            try:
                # Create journey
                journey = self.analyzer.create_journey(
                    image_path,
                    use_cache=True
                )
                
                # Save to gallery
                output_file = self.output_dir / f"{image_path.stem}.json"
                output_file.write_text(journey.model_dump_json(indent=2))
                
                results.append({
                    "filename": image_path.name,
                    "status": "success",
                    "steps": journey.total_steps,
                    "duration": journey.estimated_duration_minutes,
                    "confidence": journey.confidence_score
                })
                
                # Rate limit
                if i < len(images):
                    time.sleep(delay_seconds)
                
            except Exception as e:
                print(f"✗ Error: {e}")
                results.append({
                    "filename": image_path.name,
                    "status": "error",
                    "error": str(e)
                })
        
        self._print_report(results)
        
        # Save report
        report_file = self.output_dir / "_gallery_report.json"
        report_file.write_text(json.dumps(results, indent=2))
    
    def _print_report(self, results):
        """Print processing summary"""
        successes = [r for r in results if r["status"] == "success"]
        failures = [r for r in results if r["status"] == "error"]
        
        print(f"\n{'='*60}")
        print("GALLERY PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total: {len(results)}")
        print(f"✓ Success: {len(successes)}")
        print(f"✗ Failed: {len(failures)}")
        
        if successes:
            avg_steps = sum(r["steps"] for r in successes) / len(successes)
            avg_duration = sum(r["duration"] for r in successes) / len(successes)
            avg_confidence = sum(r["confidence"] for r in successes) / len(successes)
            
            print(f"\nAverage steps: {avg_steps:.1f}")
            print(f"Average duration: {avg_duration:.1f} minutes")
            print(f"Average confidence: {avg_confidence:.0%}")
        
        print(f"{'='*60}\n")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    print("="*60)
    print("SLOW LOOKING - Art Education Tool")
    print("="*60)
    
    # Initialize
    analyzer = SlowLookingAnalyzer(cache_dir=Path("journeys_cache"))
    library = JourneyLibrary(library_dir=Path("user_library"))
    
    # Example 1: Create a journey for a single artwork
    print("\n📱 EXAMPLE 1: Create a Slow Looking Journey")
    print("-" * 60)
    
    test_image = Path("/Users/alievanayasso//Documents/SlowMA/2B--glory%20days.jpg")
    
    if test_image.exists():
        # Create the journey
        journey = analyzer.create_journey(test_image)
        
        # Display journey info
        print(f"\n🎨 {journey.artwork.title or 'Untitled'}")
        if journey.artwork.artist:
            print(f"   by {journey.artwork.artist}")
        
        print(f"\n📍 Journey Overview:")
        print(f"   Steps: {journey.total_steps}")
        print(f"   Duration: ~{journey.estimated_duration_minutes} minutes")
        print(f"   Confidence: {journey.confidence_score:.0%}")
        
        print(f"\n💭 Welcome: {journey.welcome_text}")
        
        print(f"\n🚶 Journey Steps:")
        for step in journey.steps:
            print(f"\n   Step {step.step_number}: {step.region.title}")
            print(f"   └─ Look away for {step.look_away_duration}s")
            print(f"   └─ Soft prompt: \"{step.region.soft_prompt}\"")
            print(f"   └─ Observation: {step.region.observation[:80]}...")
        
        print(f"\n🎯 Main Takeaway:")
        print(f"   {journey.final_summary.main_takeaway}")
        
        print(f"\n❓ Reflection Question:")
        print(f"   {journey.final_summary.reflection_question}")
        
        # Save to library
        library.save_journey(journey)
        
        # Show library stats
        stats = library.get_stats()
        print(f"\n📚 Library: {stats['total_journeys']} journeys saved")
        
    else:
        print(f"Test image not found: {test_image}")
        print("Add a 'test_artwork.jpg' to test")
    
    print("\n" + "="*60)
    print("\n📦 EXAMPLE 2: Batch Process Gallery")
    print("-" * 60)
    print("""
To pre-process a curated gallery:

    preprocessor = GalleryPreprocessor(
        analyzer, 
        output_dir=Path("gallery_journeys")
    )
    preprocessor.process_gallery(
        Path("my_artworks"),
        delay_seconds=2.0
    )
    """)
    
    print("\n" + "="*60)
    print("🎯 NEXT STEPS:")
    print("="*60)
    print("""
    1. Set up .env with ANTHROPIC_API_KEY
    2. Test with a few artworks to evaluate journey quality
    3. Refine the prompt if needed for tone/style
    4. Build the mobile UI for the walkthrough experience
    """)