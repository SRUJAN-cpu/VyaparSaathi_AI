"""
Demo mode management for VyaparSaathi.

Handles switching between demo (synthetic) and real data modes,
with clear indicators for demo mode usage.
"""

from typing import Dict, Any, Optional, Literal


DataSource = Literal["demo", "real"]


class DemoModeManager:
    """
    Manages demo mode state and data source routing.
    """
    
    def __init__(self):
        """Initialize demo mode manager."""
        self._user_modes: Dict[str, DataSource] = {}
    
    def set_mode(self, user_id: str, mode: DataSource) -> None:
        """
        Set data mode for a user.
        
        Args:
            user_id: User identifier
            mode: Data source mode ("demo" or "real")
        """
        if mode not in ["demo", "real"]:
            raise ValueError(f"Invalid mode: {mode}. Must be 'demo' or 'real'")
        
        self._user_modes[user_id] = mode
    
    def get_mode(self, user_id: str) -> DataSource:
        """
        Get current data mode for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Current data source mode (defaults to "real")
        """
        return self._user_modes.get(user_id, "real")
    
    def is_demo_mode(self, user_id: str) -> bool:
        """
        Check if user is in demo mode.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if user is in demo mode
        """
        return self.get_mode(user_id) == "demo"
    
    def clear_mode(self, user_id: str) -> None:
        """
        Clear mode setting for a user (resets to default "real").
        
        Args:
            user_id: User identifier
        """
        if user_id in self._user_modes:
            del self._user_modes[user_id]


# Global demo mode manager instance
_demo_manager = DemoModeManager()


def set_demo_mode(user_id: str, enabled: bool = True) -> None:
    """
    Enable or disable demo mode for a user.
    
    Args:
        user_id: User identifier
        enabled: True to enable demo mode, False for real data mode
    """
    mode: DataSource = "demo" if enabled else "real"
    _demo_manager.set_mode(user_id, mode)


def is_demo_mode(user_id: str) -> bool:
    """
    Check if user is in demo mode.
    
    Args:
        user_id: User identifier
        
    Returns:
        True if user is in demo mode
    """
    return _demo_manager.is_demo_mode(user_id)


def get_data_source(user_id: str) -> DataSource:
    """
    Get the current data source for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Data source mode ("demo" or "real")
    """
    return _demo_manager.get_mode(user_id)


def add_demo_indicator(
    response: Dict[str, Any],
    user_id: str,
) -> Dict[str, Any]:
    """
    Add demo mode indicator to a response.
    
    Args:
        response: Response dictionary to modify
        user_id: User identifier
        
    Returns:
        Modified response with demo indicator
    """
    if is_demo_mode(user_id):
        response["_demo_mode"] = True
        response["_demo_notice"] = (
            "⚠️ DEMO MODE: This data is synthetic and for demonstration purposes only. "
            "Switch to real data mode to use your actual business data."
        )
    else:
        response["_demo_mode"] = False
    
    return response


def get_demo_indicator_text(user_id: str) -> Optional[str]:
    """
    Get demo mode indicator text for display.
    
    Args:
        user_id: User identifier
        
    Returns:
        Demo indicator text if in demo mode, None otherwise
    """
    if is_demo_mode(user_id):
        return (
            "⚠️ DEMO MODE: You are viewing synthetic demonstration data. "
            "This is not your real business data."
        )
    return None


def validate_mode_switch(
    user_id: str,
    target_mode: DataSource,
    has_real_data: bool = False,
) -> tuple[bool, Optional[str]]:
    """
    Validate if mode switch is allowed.
    
    Args:
        user_id: User identifier
        target_mode: Target mode to switch to
        has_real_data: Whether user has uploaded real data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if target_mode == "real" and not has_real_data:
        return (
            False,
            "Cannot switch to real data mode: No real data available. "
            "Please upload your sales data first."
        )
    
    return (True, None)


def switch_mode(
    user_id: str,
    target_mode: DataSource,
    has_real_data: bool = False,
) -> Dict[str, Any]:
    """
    Switch user's data mode with validation.
    
    Args:
        user_id: User identifier
        target_mode: Target mode to switch to ("demo" or "real")
        has_real_data: Whether user has uploaded real data
        
    Returns:
        Result dictionary with success status and message
    """
    # Validate switch
    is_valid, error_msg = validate_mode_switch(user_id, target_mode, has_real_data)
    
    if not is_valid:
        return {
            "success": False,
            "error": error_msg,
            "current_mode": get_data_source(user_id),
        }
    
    # Perform switch
    _demo_manager.set_mode(user_id, target_mode)
    
    return {
        "success": True,
        "message": f"Successfully switched to {target_mode} data mode",
        "current_mode": target_mode,
        "demo_indicator": get_demo_indicator_text(user_id),
    }
