import os
import zipfile
from collections import defaultdict
from PIL import Image
import io
import re
import time

# Configuration
MODS_DIR = "E:/Modrinth/profiles/Profile Name/mods"  # Mods folder
TARGET_COLORS = {(198, 198, 198), (85, 85, 85)}  # Target gray colors    

def rotate_logs(base_name, max_backups=5):
    """Rotates log files similar to Minecraft's latest.log system."""
    # First, rename existing backup logs
    for i in range(max_backups - 1, 0, -1):
        old_name = f"{base_name[:-4]}-{i}.txt"
        new_name = f"{base_name[:-4]}-{i+1}.txt"
        if os.path.exists(old_name):
            try:
                os.rename(old_name, new_name)
            except Exception as e:
                print(f"  ⚠️ Error rotating {old_name}: {str(e)}")
    
    # Rename current log if it exists
    if os.path.exists(base_name):
        try:
            os.rename(base_name, f"{base_name[:-4]}-1.txt")
        except Exception as e:
            print(f"  ⚠️ Error rotating {base_name}: {str(e)}")

def extract_profile_name(mods_dir):
    """Extracts profile name from mods directory path."""
    # Try to extract profile name from path like "E:/Modrinth/profiles/Profile Name/mods"
    pattern = r'[/\\]profiles[/\\]([^/\\]+)[/\\]mods$'
    match = re.search(pattern, mods_dir)
    if match:
        return match.group(1)
    return "Unknown Profile"

def main():
    # Extract profile name for log filename
    profile_name = extract_profile_name(MODS_DIR)
    base_log_name = f"GUI Finder Log - {profile_name}.txt"
    
    print("\n" + "="*60)
    print("GUI TEXTURE FINDER")
    print("="*60)
    print(f"Profile: {profile_name}")
    print(f"Scanning for textures with colors: {[(r, g, b) for r, g, b in TARGET_COLORS]}")
    print(f"Target directory: {MODS_DIR}")
    
    # Rotate logs before starting
    rotate_logs(base_log_name)
    
    results = defaultdict(lambda: defaultdict(list))
    total_textures = 0
    processed_mods = 0
    skipped_mods = 0
    start_time = time.time()
    
    # Process each JAR file in mods folder
    for filename in os.listdir(MODS_DIR):
        if not filename.lower().endswith('.jar'):
            continue
            
        jar_path = os.path.join(MODS_DIR, filename)
        processed_mods += 1
        mod_textures = 0
        
        try:
            with zipfile.ZipFile(jar_path, 'r') as zip_ref:
                print(f"\n🔍 Processing mod: {filename}")
                
                for file_info in zip_ref.infolist():
                    file_path = file_info.filename
                    
                    # Check path structure
                    parts = file_path.split('/')
                    if len(parts) < 5:
                        continue
                        
                    # Verify path pattern assets/*/textures/(gui|screens)/*.png
                    if (parts[0] != 'assets' or 
                        parts[2] != 'textures' or 
                        parts[3].lower() not in ['gui', 'screens'] or
                        not file_path.lower().endswith('.png')):
                        continue
                    
                    modid = parts[1]
                    relative_path = '/'.join(parts[3:])
                    
                    # Check PNG content
                    try:
                        with zip_ref.open(file_path) as img_file:
                            img_data = io.BytesIO(img_file.read())
                            img = Image.open(img_data)
                            
                            # Convert to RGB for proper color checking
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            
                            # Check for target colors
                            color_found = False
                            for pixel in img.getdata():
                                if pixel in TARGET_COLORS:
                                    color_found = True
                                    break
                            
                            if color_found:
                                results[filename][modid].append(relative_path)
                                mod_textures += 1
                                print(f"  ✅ Found: {modid}/{relative_path}")
                    
                    except Exception as e:
                        print(f"  ⚠️ Error processing {file_path}: {str(e)}")
        
        except zipfile.BadZipFile:
            skipped_mods += 1
            print(f"  ⚠️ Skipping (not a valid JAR): {filename}")
    
    total_textures = sum(len(textures) for mods in results.values() for textures in mods.values())
    elapsed_time = time.time() - start_time
    
    # Output results to file
    with open(base_log_name, 'w') as out:
        out.write(f"GUI TEXTURE FINDER LOG\n")
        out.write(f"Profile: {profile_name}\n")
        out.write(f"Scan time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
        out.write(f"Elapsed time: {elapsed_time:.2f} seconds\n")
        out.write(f"Total mods processed: {processed_mods}\n")
        out.write(f"Mods skipped: {skipped_mods}\n")
        out.write(f"Total GUI textures found: {total_textures}\n")
        out.write("="*60 + "\n\n")
        
        for mod, modids in results.items():
            out.write(f"Mod: {mod}\n")
            
            for modid, textures in modids.items():
                out.write(f"  ModID: {modid}\n")
                
                for tex in sorted(textures):
                    out.write(f"    - {tex}\n")
    
    # Output results to console
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    print(f"Profile: {profile_name}")
    print(f"Total mods processed: {processed_mods}")
    print(f"Mods skipped: {skipped_mods}")
    print(f"Total GUI textures found: {total_textures}")
    print(f"Processing time: {elapsed_time:.2f} seconds")
    print(f"Report saved to: {os.path.abspath(base_log_name)}")
    print("="*60)
    
    # Display summary in console
    for mod, modids in results.items():
        print(f"\n📦 Mod: {mod}")
        
        for modid, textures in modids.items():
            print(f"  🧩 ModID: {modid}")
            
            for tex in sorted(textures)[:3]:  # Show first 3 textures
                print(f"    • {tex}")
            
            if len(textures) > 3:
                print(f"    • ... and {len(textures) - 3} more")
    
    if total_textures == 0:
        print("\n💡 Recommendations:")
        print("1. Verify the mods directory path is correct")
        print("2. Check if mods actually contain GUI textures")
        print("3. Consider adjusting target color values if needed")

if __name__ == "__main__":
    main()