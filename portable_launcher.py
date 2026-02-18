import sys
import os

# 1. Force add the current directory to sys.path
# This ensures that 'gui_app.py', 'core.py', etc. are strictly visible.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"Portable Launcher: Added {current_dir} to sys.path")

# 2. Import main (now it should definitely find modules)
try:
    import main
except ImportError as e:
    print("\nCRITICAL ERROR: Could not import main or its dependencies.")
    print(f"Error Details: {e}")
    print(f"Current sys.path: {sys.path}")
    input("Press Enter to exit...")
    sys.exit(1)

# 3. Run the app
if __name__ == "__main__":
    print("Starting GUI mode...")
    # Inject arguments as if called from command line
    sys.argv = [sys.argv[0], '--mode', 'gui']
    main.main()
