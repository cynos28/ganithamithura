from openai import OpenAI
from typing import List, Optional
from app.config import settings

# Initialize OpenAI client
openai_client = OpenAI(api_key=settings.openai_api_key)


class LLMClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self):
        self.openai_client = openai_client
        self.openai_model = settings.openai_model
    
    async def generate_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate completion with automatic fallback:
        1. Try OpenAI first
        2. If fails (no credits), try Gemini
        3. If both fail, raise exception
        """
        
        # Try OpenAI first (with timeout)
        try:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=5.0,  # 5 second timeout
            )
            print(f"✅ Generated with OpenAI ({self.openai_model})")
            return response.choices[0].message.content
            
        except Exception as openai_error:
            error_msg = str(openai_error)
            
            # Check for quota/credit issues and display clear message
            if "insufficient_quota" in error_msg or "429" in error_msg:
                print("\n" + "="*70)
                print("🚨 OPENAI QUOTA EXCEEDED 🚨")
                print("="*70)
                print("❌ Your OpenAI API has no credits available")
                print("💡 To fix this:")
                print("   1. Go to: https://platform.openai.com/settings/organization/billing")
                print("   2. Add at least $5 credit to your account")
                print("   3. Questions will use fallback templates until fixed")
                print("="*70 + "\n")
            elif "Connection error" in error_msg or "timeout" in error_msg.lower():
                print("\n" + "="*70)
                print("🌐 OPENAI CONNECTION ERROR")
                print("="*70)
                print("❌ Cannot connect to OpenAI API")
                print("💡 Check your internet connection")
                print("="*70 + "\n")
            else:
                print(f"❌ OpenAI API error: {error_msg}")
            
            raise Exception(f"OpenAI API error: {error_msg}")
    
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
