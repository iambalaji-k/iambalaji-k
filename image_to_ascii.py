import sys
import os
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw

def image_to_ascii(image_path, output_path, target_width=52, aspect_ratio_factor=0.55):
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return False
    
    try:
        # Load RGB image
        img_rgb = Image.open(image_path).convert('RGB')
        width, height = img_rgb.size
        
        # 1. Create a binary mask of the foreground using floodfill from corners
        img_copy = img_rgb.copy()
        fill_color = (255, 0, 255)  # Magenta sentinel
        
        # Floodfill from the corners and outer boundaries
        ImageDraw.floodfill(img_copy, (0, 0), fill_color, thresh=30)
        ImageDraw.floodfill(img_copy, (width-1, 0), fill_color, thresh=30)
        ImageDraw.floodfill(img_copy, (0, height-1), fill_color, thresh=30)
        ImageDraw.floodfill(img_copy, (width-1, height-1), fill_color, thresh=30)
        
        # Floodfill along edges to catch borders
        for x in range(0, width, 100):
            ImageDraw.floodfill(img_copy, (x, 0), fill_color, thresh=30)
            ImageDraw.floodfill(img_copy, (x, height-1), fill_color, thresh=30)
        for y in range(0, height, 100):
            ImageDraw.floodfill(img_copy, (0, y), fill_color, thresh=30)
            ImageDraw.floodfill(img_copy, (width-1, y), fill_color, thresh=30)
            
        # Extract background pixels (those filled with magenta) using numpy
        arr = np.array(img_copy)
        is_bg = (arr[:, :, 0] == 255) & (arr[:, :, 1] == 0) & (arr[:, :, 2] == 255)
        
        mask_arr = np.ones((height, width), dtype=np.uint8) * 255
        mask_arr[is_bg] = 0
        mask = Image.fromarray(mask_arr)
        
        # Convert original image to grayscale for shading
        img_gray = img_rgb.convert('L')
        
        # Boost contrast to make features more defined
        contrast = ImageEnhance.Contrast(img_gray)
        img_gray = contrast.enhance(1.6)
        
        # Boost sharpness to enhance edges
        sharpness = ImageEnhance.Sharpness(img_gray)
        img_gray = sharpness.enhance(1.8)
        
    except Exception as e:
        print(f"Error loading/enhancing image: {e}")
        return False
    
    # Calculate target height based on aspect ratio factor of monospace characters
    orig_w, orig_h = img_rgb.size
    aspect_ratio = orig_h / orig_w
    target_height = int(target_width * aspect_ratio * aspect_ratio_factor)
    
    # Let's cap target height at 28 lines to fit our slightly larger SVG layout
    if target_height > 28:
        target_height = 28
        
    # Resize both image and mask
    img_gray = img_gray.resize((target_width, target_height), Image.Resampling.LANCZOS)
    mask = mask.resize((target_width, target_height), Image.Resampling.NEAREST)
    
    # An expanded 29-character gradient ranging from dark to light (high density to low density)
    chars = ["@", "#", "8", "&", "G", "p", "b", "d", "k", "w", "o", "a", "h", "*", "j", "z", "u", "i", "c", "t", "!", "+", "=", "-", ";", ":", ",", ".", " "]
    num_chars = len(chars)
    
    ascii_lines = []
    for y in range(target_height):
        line = ""
        for x in range(target_width):
            mask_val = mask.getpixel((x, y))
            if mask_val == 0:
                line += " "  # Map background directly to a space
            else:
                pixel_val = img_gray.getpixel((x, y))
                # Map pixel value (0 to 255) to character index (0 to num_chars - 1)
                char_idx = int((pixel_val / 255.0) * (num_chars - 1))
                line += chars[char_idx]
        # Pad the line to target_width with spaces to prevent rendering shifts
        line = line.ljust(target_width)
        ascii_lines.append(line)
        
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for line in ascii_lines:
                f.write(line + "\n")
        print(f"Successfully generated ASCII art at {output_path} ({target_width}x{target_height})")
        return True
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False

if __name__ == '__main__':
    img_path = "D:/Vibe Coding/githubhome/balaji.png"
    out_path = "D:/Vibe Coding/githubhome/my_face_ascii.txt"
    image_to_ascii(img_path, out_path)
