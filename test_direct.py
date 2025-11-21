#!/usr/bin/env python
"""
Direct test without importing the cached settings
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

# Force reload .env
load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")

print("=" * 60)
print("🔍 Direct OpenAI Test (bypassing cached settings)")
print("=" * 60)
print(f"\n✅ API Key loaded: {api_key[:30]}...{api_key[-10:]}")
print(f"📏 Key length: {len(api_key)}")

client = OpenAI(api_key=api_key)

try:
    print("\n🤖 Testing with model: gpt-4o-mini")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a 2-sentence email subject line about chemical products."}
        ],
        max_tokens=50
    )
    
    print("✅ SUCCESS!")
    print(f"📧 Response: {response.choices[0].message.content}")
    print("\n" + "=" * 60)
    print("✅ OpenAI is working! The issue was cached settings.")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    
    # Try alternative model
    try:
        print("\n🔄 Trying gpt-3.5-turbo instead...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'test successful' in 2 words"}
            ],
            max_tokens=10
        )
        print(f"✅ SUCCESS with gpt-3.5-turbo!")
        print(f"📧 Response: {response.choices[0].message.content}")
        print("\n💡 Solution: Use gpt-3.5-turbo instead of gpt-4o-mini")
    except Exception as e2:
        print(f"❌ Also failed: {e2}")
