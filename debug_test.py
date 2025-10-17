from pathlib import Path
import os

print("Current directory:", os.getcwd())
print("\nChecking folders:")

folders = ["journeys_cache", "user_library", "cache", "gallery_journeys"]

for folder in folders:
    folder_path = Path(folder)
    exists = folder_path.exists()
    is_dir = folder_path.is_dir() if exists else False
    
    print(f"\n{folder}:")
    print(f"  Exists: {exists}")
    print(f"  Is directory: {is_dir}")
    
    if exists and is_dir:
        files = list(folder_path.glob("*"))
        print(f"  Files inside: {len(files)}")
        for f in files:
            print(f"    - {f.name}")

print("\n" + "="*50)
print("Looking for all .json files:")
for json_file in Path(".").rglob("*.json"):
    print(f"  {json_file}")