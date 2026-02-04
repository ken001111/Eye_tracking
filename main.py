"""
Main entry point for the Gaze Tracking System.
Coordinates all components and handles application flow.
"""

import sys
import argparse
from gui_app import main as gui_main

import config

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Gaze Tracking System - Real-time eye tracking with multiple methods"
    )
    parser.add_argument(
        '--mode',
        choices=['gui', 'cli'],
        default='gui',
        help='Application mode: GUI (default) or CLI'
    )
    parser.add_argument(
        '--tracker',
        choices=['mediapipe'],
        default=config.DEFAULT_TRACKER,
        help=f'Tracker method to use (default: {config.DEFAULT_TRACKER})'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'gui':
        # Launch GUI application
        print("Starting Gaze Tracking System (GUI mode)...")
        print(f"Using tracker: {args.tracker}")
        gui_main(tracker_type=args.tracker)
    elif args.mode == 'cli':
        # CLI mode (can be implemented later)
        print("CLI mode not yet implemented. Use --mode gui for GUI application.")
        sys.exit(1)


if __name__ == "__main__":
    main()
