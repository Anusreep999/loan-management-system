#!/user/bin/env bash

set -e  # Exit on error

#modify this line as needed for your package manager
pip install -r requirements.txt

# Apply any database migrations
python manage.py migrate


