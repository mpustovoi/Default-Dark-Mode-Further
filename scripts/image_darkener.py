import os
from PIL import Image
import time

def main():
    """
    Darkens all PNG images in the current directory by applying a darkening factor.
    """
    DARKEN_FACTOR = 0.399
    EXTENSIONS = {'.png'}
    
    print("\n" + "="*60)
    print("IMAGE DARKENER")
    print("="*60)
    print(f"Darkening factor: {DARKEN_FACTOR}")
    print(f"Target directory: {os.path.abspath('.')}")
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    start_time = time.time()
    
    for root, _, files in os.walk('.'):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in EXTENSIONS:
                img_path = os.path.join(root, file)
                
                try:
                    with Image.open(img_path) as img:
                        width, height = img.size
                        
                        # Skip if already processed (assuming processed images would be darker)
                        # This is a simple check - could be improved with more sophisticated logic
                        if width == 160 and height == 160 and img.mode == 'RGBA':
                            should_process = False
                            for x in range(0, width, 10):
                                for y in range(0, height, 10):
                                    r, g, b, *a = img.getpixel((x, y))
                                    if r > 100 or g > 100 or b > 100:  # If any bright pixels found
                                        should_process = True
                                        break
                                if should_process:
                                    break
                            if not should_process:
                                skipped_count += 1
                                continue
                        
                        # Process the image
                        if img.mode not in ['RGBA', 'RGB']:
                            img = img.convert('RGBA')
                        
                        pixels = img.load()
                        width, height = img.size
                        
                        for x in range(width):
                            for y in range(height):
                                rgba = pixels[x, y]
                                r, g, b = rgba[0], rgba[1], rgba[2]
                                a = rgba[3] if len(rgba) > 3 else 255
                                
                                if a == 0:
                                    continue
                                
                                r = int(r * DARKEN_FACTOR)
                                g = int(g * DARKEN_FACTOR)
                                b = int(b * DARKEN_FACTOR)
                                
                                pixels[x, y] = (r, g, b, a)
                        
                        img.save(img_path)
                        processed_count += 1
                        print(f"  ✅ Darkened: {file} ({width}×{height})")
                
                except Exception as e:
                    error_count += 1
                    print(f"  ❌ Error processing {file}: {str(e)}")
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)
    print(f"Total images processed: {processed_count}")
    print(f"Images skipped: {skipped_count}")
    print(f"Errors encountered: {error_count}")
    print(f"Processing time: {elapsed_time:.2f} seconds")
    print(f"Target directory: {os.path.abspath('.')}")
    print("="*60)
    
    if error_count > 0:
        print("\n💡 Recommendations:")
        print("1. Check file permissions for problematic images")
        print("2. Verify that all PNG files are not corrupted")
        print("3. Ensure PIL/Pillow library is properly installed")

if __name__ == "__main__":
    main()