import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin():
    username = 'admin@hiring.com'
    email = 'admin@hiring.com'
    password = 'admin123'

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Admin created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password}")
    else:
        print(f"Admin '{username}' already exists.")

if __name__ == "__main__":
    create_admin()
