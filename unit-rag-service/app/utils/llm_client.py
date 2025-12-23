from openai import OpenAI
from typing import List, Optional
import time
from app.config import settings

# Initialize OpenAI client with longer default timeout
openai_client = OpenAI(
    api_key=settings.openai_api_key,
    timeout=120.0  # 2 minutes default timeout
)


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
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate completion with retry logic and extended timeout
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
                    timeout=120.0,  # 2 minutes timeout for complex question generation
                )
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


# Singleton instance
llm_client = LLMClient()

llm_client = LLMClient()
