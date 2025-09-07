#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create migrations
echo "Creating migrations..."
python manage.py makemigrations

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
from transport.models import Profile
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    Profile.objects.create(user=user, role='naručilac', phone_number='', address='', company_name='Admin')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Build process completed successfully!"
