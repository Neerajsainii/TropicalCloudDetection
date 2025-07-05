#!/usr/bin/env python
"""
Generate a new Django secret key for production use.
Run this script and copy the generated key to your environment variables.
"""

from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    secret_key = get_random_secret_key()
    print("Generated Django Secret Key:")
    print(secret_key)
    print("\nCopy this key to your Render environment variables as SECRET_KEY") 