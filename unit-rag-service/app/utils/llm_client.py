from openai import OpenAI
from typing import List, Optional
import time
import os
import uuid
import httpx
from app.config import settings

# Initialize OpenAI client with longer default timeout
openai_client = OpenAI(
    api_key=settings.openai_api_key,
    timeout=120.0  # 2 minutes default timeout
)

# Base URL for serving static images (will be set based on request)
STATIC_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "images")


class LLMClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self):
        self.openai_client = openai_client
        self.openai_model = settings.openai_model
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    async def generate_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_streaming: bool = False,
    ) -> str:
        """
        Generate completion with retry logic, optimized timeout, and optional streaming
        """
        
        # Try OpenAI with retries
        for attempt in range(self.max_retries):
            try:
                print(f"🔄 Attempt {attempt + 1}/{self.max_retries} - Calling OpenAI API...")
                
                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=60.0,  # Reduced to 60s for faster failure detection
                    stream=use_streaming,
                )
                
                if use_streaming:
                    # Collect streaming chunks
                    content = ""
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            content += chunk.choices[0].delta.content
                    print(f"✅ Generated with OpenAI ({self.openai_model}) - Streaming")
                    return content
                else:
                    print(f"✅ Generated with OpenAI ({self.openai_model})")
                    return response.choices[0].message.content
                
            except Exception as openai_error:
                error_msg = str(openai_error)
                
                # Check for quota/credit issues (no retry)
                if "insufficient_quota" in error_msg or "429" in error_msg:
                    print("\n" + "="*70)
                    print("🚨 OPENAI QUOTA EXCEEDED 🚨")
                    print("="*70)
                    print("❌ Your OpenAI API has no credits available")
                    print("💡 To fix this:")
                    print("   1. Go to: https://platform.openai.com/settings/organization/billing")
                    print("   2. Add at least $5 credit to your account")
                    print("="*70 + "\n")
                    raise Exception(f"OpenAI API error: {error_msg}")
                
                # Retry on timeout or connection errors
                elif "timeout" in error_msg.lower() or "Connection error" in error_msg or "APIConnectionError" in error_msg:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (attempt + 1)
                        print(f"⚠️  Timeout/Connection error (attempt {attempt + 1}/{self.max_retries})")
                        print(f"⏳ Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue  # Retry
                    else:
                        print("\n" + "="*70)
                        print("🌐 OPENAI CONNECTION ERROR - Max retries reached")
                        print("="*70)
                        print("❌ Cannot connect to OpenAI API after 3 attempts")
                        print("💡 Possible issues:")
                        print("   1. Check your internet connection")
                        print("   2. OpenAI API might be experiencing issues")
                        print("   3. Your firewall might be blocking the connection")
                        print("="*70 + "\n")
                        raise Exception(f"OpenAI API error: {error_msg}")
                else:
                    print(f"❌ OpenAI API error: {error_msg}")
                    raise Exception(f"OpenAI API error: {error_msg}")
        
        raise Exception("Max retries exceeded")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts (OpenAI only for now)"""
        try:
            response = self.openai_client.embeddings.create(
                model=settings.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise Exception(f"Embedding generation error: {str(e)}")
    
    async def generate_with_vision(
        self,
        system_prompt: str,
        user_prompt: str,
        image_base64: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate completion using GPT-4 Vision with image input
        
        Args:
            system_prompt: System message for context
            user_prompt: User's text prompt
            image_base64: Base64-encoded image
            model: Model to use (gpt-4o, gpt-4-turbo, etc.)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            print(f"👁️ Calling GPT-4 Vision API...")
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}",
                                    "detail": "high"  # Use "high" for detailed image analysis
                                }
                            }
                        ]
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=90.0  # Vision API might take longer
            )
            
            content = response.choices[0].message.content
            print(f"✅ Vision response generated ({model})")
            return content
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Vision API error: {error_msg}")
            
            if "insufficient_quota" in error_msg or "429" in error_msg:
                print("\n" + "="*70)
                print("🚨 OPENAI QUOTA EXCEEDED 🚨")
                print("="*70)
                print("❌ Your OpenAI API has no credits available")
                print("💡 GPT-4 Vision requires credits. Add at least $10 to your account.")
                print("="*70 + "\n")
            
            raise Exception(f"Vision API error: {error_msg}")


# Singleton instance
llm_client = LLMClient()
