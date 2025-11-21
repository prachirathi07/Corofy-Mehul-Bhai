import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

env_key = os.getenv("OPENAI_API_KEY")
# test_key removed - use environment variable instead
test_key = os.getenv("OPENAI_API_KEY")  # Use .env file instead of hardcoding

print("🔍 Checking API Keys...")
print(f"\n.env key (first 20): {env_key[:20] if env_key else 'NOT FOUND'}")
print(f"test.py key (first 20): {test_key[:20]}")
print(f"\n.env key (last 10): {env_key[-10:] if env_key else 'NOT FOUND'}")
print(f"test.py key (last 10): {test_key[-10:]}")
print(f"\nKeys match: {env_key == test_key if env_key else False}")
print(f"\n.env key length: {len(env_key) if env_key else 0}")
print(f"test.py key length: {len(test_key)}")
