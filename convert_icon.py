from PIL import Image
import os

# Paths
source_png = r"C:\Users\ARNAUD\.gemini\antigravity\brain\3ec9556b-8dc1-488f-a7ea-a890faf36302\modern_pharma_logo_1767775693658.png"
dest_ico = r"c:\Pharma_logiciels_version_01\frontend1\windows\runner\resources\app_icon.ico"

try:
    print(f"Opening {source_png}...")
    img = Image.open(source_png)
    
    print("Converting to ICO...")
    # ICO files can contain multiple sizes
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(dest_ico, format='ICO', sizes=icon_sizes)
    
    print(f"Success! Saved to {dest_ico}")
except Exception as e:
    print(f"Error: {e}")
