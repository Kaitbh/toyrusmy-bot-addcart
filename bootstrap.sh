#!/bin/bash

# Optional: create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python3 -m playwright install

echo "✅ Setup complete. You can now run the monitor script with:"
echo "   source venv/bin/activate && python monitor.py"