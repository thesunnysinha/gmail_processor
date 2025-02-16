#!/bin/bash

# Check if virtual environment directory exists
if [ ! -d "venv" ]; then
  # Create virtual environment
  python3 -m venv venv

  # Activate virtual environment
  source venv/bin/activate

  # Install requirements
  pip install -r requirements.txt
else
  # Activate virtual environment
  source venv/bin/activate
fi

# Run Django commands
python manage.py migrate
python manage.py fetch
python manage.py apply_rules