
import os
import sys
import django
from django.utils import translation

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def verify_language(lang_code, text, expected_trans):
    translation.activate(lang_code)
    current = translation.gettext(text)
    if expected_trans in current:
        print(f"[PASS] {lang_code}: '{text}' -> '{current}'")
    else:
        print(f"[FAIL] {lang_code}: '{text}' expected '{expected_trans}', got '{current}'")

def main():
    print("Verifying Translations...")
    
    # Check Hindi
    verify_language('hi', 'Maid Hiring System', 'मेड हायरिंग सिस्टम')
    verify_language('hi', 'Find Your Perfect Help', 'अपनी सही मदद खोजें')
    
    # Check Marathi
    verify_language('mr', 'Maid Hiring System', 'मोलकरीण हायरिंग सिस्टम')
    verify_language('mr', 'Find Your Perfect Help', 'आपली योग्य मदत शोधा')
    
    print("Verification Complete.")

if __name__ == "__main__":
    main()
