import sys
import os
import glob

print("=== PORTABLE LAUNCHER DIAGNOSTICS ===")

# 1. Force add current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
print(f"Added to sys.path: {current_dir}")

# 2. Check site-packages
print("\nChecking installed packages...")
try:
    # Find site-packages in the portable folder
    site_packages = glob.glob(os.path.join(current_dir, "python_portable", "Lib", "site-packages"))
    if not site_packages:
        # Fallback for different layout
        site_packages = glob.glob(os.path.join(current_dir, "python_portable", "*", "site-packages"))
    
    if site_packages:
        print(f"Found site-packages at: {site_packages[0]}")
        pkgs = [os.path.basename(p) for p in glob.glob(os.path.join(site_packages[0], "*"))]
        print(f"Installed packages (top 10): {pkgs[:10]}")
        if "mediapipe" in pkgs or "mediapipe-0.10.9.dist-info" in pkgs:
            print("MediaPipe seems to be installed.")
        else:
            print("WARNING: MediaPipe folder NOT found in site-packages!")
    else:
        print("WARNING: Could not find site-packages folder!")
except Exception as e:
    print(f"Error checking packages: {e}")

# 3. Test Imports Individually
print("\nTesting individual imports...")
try:
    import numpy
    print("SUCCESS: import numpy")
except ImportError as e:
    print(f"FAIL: import numpy -> {e}")

try:
    import cv2
    print("SUCCESS: import cv2")
except ImportError as e:
    print(f"FAIL: import cv2 -> {e}")

try:
    import mediapipe
    print("SUCCESS: import mediapipe")
except ImportError as e:
    print(f"FAIL: import mediapipe -> {e}")

# 4. Import Main
print("\nAttempting to import main...")
try:
    import main
except ImportError as e:
    print(f"\nCRITICAL ERROR: Could not import main.")
    print(f"Error Details: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

# 5. Run
if __name__ == "__main__":
    print("\nStarting GUI mode...")
    sys.argv = [sys.argv[0], '--mode', 'gui']
    main.main()
