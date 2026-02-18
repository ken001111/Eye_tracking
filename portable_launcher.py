import sys
import os
import glob

print("=== PORTABLE LAUNCHER DIAGNOSTICS (v2) ===")

# 1. Force add current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. Check Libraries
print("\nChecking critical libraries...")
missing = []

try:
    import numpy
    print("[OK] numpy")
except ImportError:
    print("[FAIL] numpy")
    missing.append("numpy")

try:
    import cv2
    print("[OK] cv2")
except ImportError:
    print("[FAIL] cv2")
    missing.append("cv2")

try:
    import mediapipe
    print("[OK] mediapipe")
except ImportError:
    print("[FAIL] mediapipe")
    missing.append("mediapipe")

try:
    import PIL
    print("[OK] Pillow (PIL)")
except ImportError:
    print("[FAIL] Pillow")
    missing.append("Pillow")

try:
    import pygame
    print("[OK] pygame")
except ImportError:
    print("[FAIL] pygame")
    missing.append("pygame")

try:
    import tkinter
    print("[OK] tkinter")
except ImportError:
    print("[FAIL] tkinter (Required for GUI)")
    missing.append("tkinter")

if missing:
    print(f"\nCRITICAL: The following libraries are missing: {missing}")
    if "tkinter" in missing:
        print("\nISSUE DETECTED: The 'Portable' Python version is missing the GUI (tkinter) library.")
        print("SOLUTION: Unfortunately, you cannot use this Portable mode for the GUI.")
        print("You MUST install Python 3.11 manually from python.org.")
    input("\nPress Enter to exit...")
    sys.exit(1)

# 3. Import Main
print("\nLibraries OK. Importing main...")
try:
    import main
except ImportError as e:
    print(f"\nCRITICAL ERROR: Could not import main.")
    print(f"Error Details: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

# 4. Run
if __name__ == "__main__":
    print("\nStarting GUI mode...")
    sys.argv = [sys.argv[0], '--mode', 'gui']
    main.main()
