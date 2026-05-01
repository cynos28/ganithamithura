#!/usr/bin/env python3
"""
Script to check if OpenAI API key has credits
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY', '')

if not api_key:
    print('❌ No OPENAI_API_KEY found in .env file')
    exit(1)

print(f'✅ API Key found: {api_key[:10]}...{api_key[-4:]}')
print(f'   Length: {len(api_key)} characters')
print('\n🔍 Testing OpenAI API...\n')

try:
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Make a minimal test call (very cheap - ~$0.00001)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Say 'OK'"}
        ],
        max_tokens=5
    )
    
    print('✅ SUCCESS! Your OpenAI API key is working!')
    print(f'   Response: {response.choices[0].message.content}')
    print(f'   Model: {response.model}')
    print(f'\n💰 Your API key HAS CREDITS and is ready to use!')
    
except Exception as e:
    error_message = str(e)
    print(f'❌ API call failed: {error_message}\n')
    
    if 'insufficient_quota' in error_message.lower() or 'quota' in error_message.lower():
        print('💔 Your API key has NO CREDITS (quota exceeded)')
        print('   → You need to add credits at: https://platform.openai.com/account/billing')
    elif 'invalid' in error_message.lower():
        print('🔑 Your API key is INVALID')
        print('   → Check your key at: https://platform.openai.com/api-keys')
    elif 'rate_limit' in error_message.lower():
        print('⏱️  Rate limit reached (but key is valid)')
        print('   → Wait a moment and try again')
    else:
        print('⚠️  Unknown error - check your internet connection or OpenAI status')
