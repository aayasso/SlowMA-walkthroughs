import sys
print(f"Python version: {sys.version}")

try:
    import anthropic
    print("✓ anthropic installed")
except ImportError:
    print("✗ anthropic NOT installed - run: pip install anthropic")

try:
    import pydantic
    print("✓ pydantic installed")
except ImportError:
    print("✗ pydantic NOT installed - run: pip install pydantic")

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv installed")
except ImportError:
    print("✗ python-dotenv NOT installed - run: pip install python-dotenv")

try:
    from PIL import Image
    print("✓ pillow installed")
except ImportError:
    print("✗ pillow NOT installed - run: pip install pillow")

import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    print(f"✓ API key found (starts with: {api_key[:10]}...)")
else:
    print("✗ API key NOT found - check your .env file")

from pathlib import Path
test_image = Path("test_artwork.jpg")
if test_image.exists():
    print(f"✓ Test image found: {test_image}")
else:
    print("✗ Test image not found - add a test_artwork.jpg file")

print("\n" + "="*50)
print("Setup status: Check for any ✗ marks above")
print("="*50)