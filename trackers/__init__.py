"""
Tracker factory and exports for modular eye tracking backends.
"""

from trackers.base_tracker import BaseTracker
from trackers.mediapipe_tracker import MediaPipeTracker

# Tracker registry
TRACKER_REGISTRY = {
    'mediapipe': MediaPipeTracker,
}


def create_tracker(tracker_type: str = 'dnn', **kwargs) -> BaseTracker:
    """
    Factory function to create a tracker instance.
    
    Args:
        tracker_type: Type of tracker ('dnn', 'haar', 'hybrid')
        **kwargs: Additional arguments to pass to tracker constructor
        
    Returns:
        Tracker instance
        
    Raises:
        ValueError: If tracker_type is not recognized
    """
    tracker_type = tracker_type.lower()
    
    if tracker_type not in TRACKER_REGISTRY:
        available = ', '.join(TRACKER_REGISTRY.keys())
        raise ValueError(
            f"Unknown tracker type: '{tracker_type}'. "
            f"Available types: {available}"
        )
    
    tracker_class = TRACKER_REGISTRY[tracker_type]
    return tracker_class(**kwargs)


def get_available_trackers():
    """
    Get list of available tracker types.
    
    Returns:
        List of tracker type names
    """
    return list(TRACKER_REGISTRY.keys())


__all__ = [
    'BaseTracker',
    'OpenCVDNNTracker',
    'OpenCVHaarTracker',
    'HybridTracker',
    'create_tracker',
    'get_available_trackers',
    'TRACKER_REGISTRY',
]
