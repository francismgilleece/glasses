#!/usr/bin/env python3
"""
Test script for the time input module.
Demonstrates the basic input module functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from inputs.time_input import create_time_input


async def data_listener(data):
    """Example data listener callback."""
    print(f"📥 New data from {data.source}: {data.data_type}")
    print(f"   Content: {data.content}")
    print(f"   Priority: {data.priority}, Expires: {data.expires_at}")
    print()


async def test_time_input():
    """Test the time input module."""
    print("Testing Time Input Module")
    print("=" * 40)
    
    # Create time input with custom configuration
    config = {
        'update_interval': 5,  # Update every 5 seconds for demo
        'format_12h': True,
        'include_seconds': True,
        'include_date': True
    }
    
    time_input = create_time_input(config)
    
    # Add a data listener to see updates
    time_input.add_data_listener(data_listener)
    
    # Initialize and start the module
    await time_input.initialize()
    await time_input.start()
    
    print("✓ Time input module started")
    print("📡 Listening for time updates (Ctrl+C to stop)...")
    print()
    
    try:
        # Run for a while to see updates
        for i in range(6):  # Run for ~30 seconds
            await asyncio.sleep(5)
            
            # Show current data
            print(f"🕐 Current time: {time_input.get_current_time_string()}")
            print(f"📅 Current date: {time_input.get_current_date_string()}")
            print(f"📱 Display text: {repr(time_input.get_display_text())}")
            
            # Show module status
            status = time_input.get_status()
            print(f"📊 Status: Running={status['running']}, Data count={status['data_count']}")
            print("-" * 40)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    
    # Stop the module
    await time_input.stop()
    print("✓ Time input module stopped")
    print("\n🎉 Time input module test completed!")


if __name__ == "__main__":
    try:
        asyncio.run(test_time_input())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1) 