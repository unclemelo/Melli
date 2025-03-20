#!/bin/bash

# Define the path to your virtual environment
VENV_PATH="melli"

# Check if the virtual environment exists
if [ -d "$VENV_PATH" ]; then
    echo "Activating virtual environment..."
    # Activate virtual environment (Linux/macOS)
    source "$VENV_PATH/bin/activate"
else
    echo "Virtual environment not found. Please create one first."
fi
