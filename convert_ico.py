from PIL import Image
import sys
import os

ico_path = r"c:\Pharma_logiciels_version_01\frontend1\windows\runner\resources\app_icon.ico"
png_path = r"c:\Pharma_logiciels_version_01\frontend1\assets\logo.png"

try:
    img = Image.open(ico_path)
    # ICOs can contain multiple sizes. We want the largest.
    # verify if it has sizes
    if hasattr(img, 'ico'):
        # This might not be standard PIL.
        # Standard PIL chooses the largest by default or we iterate.
        pass
    
    # Save as PNG
    img.save(png_path, format='PNG')
    print(f"Successfully converted {ico_path} to {png_path}")
except ImportError:
    print("Pillow not installed")
except Exception as e:
    print(f"Error: {e}")
