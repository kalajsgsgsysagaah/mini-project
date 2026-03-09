import sys
import os

# Add parent directory to path so we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.app import app_vercel as app
