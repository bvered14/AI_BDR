#!/usr/bin/env python3
"""
Cache Manager for Apollo API
============================

Simple script to manage the Apollo API cache for development and testing.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from bdr_ai.apollo_api import ApolloAPI
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python utils/cache_manager.py [status|clear|info]")
        print("\nCommands:")
        print("  status    - Show cache status")
        print("  clear     - Clear the cache")
        print("  info      - Show detailed cache information")
        return

    command = sys.argv[1].lower()
    apollo = ApolloAPI()

    if command == "status":
        apollo.print_cache_status()

    elif command == "clear":
        print("🗑️ Clearing Apollo API cache...")
        apollo.clear_cache()
        print("✅ Cache cleared successfully")

    elif command == "info":
        cache_info = apollo.get_cache_info()
        print("\n📊 Detailed Cache Information:")
        print("=" * 50)
        for key, value in cache_info.items():
            print(f"  {key}: {value}")

    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: status, clear, info")


if __name__ == "__main__":
    main()
