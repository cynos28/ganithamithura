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
    
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "natural",
        base_url: str = "http://localhost:8000"
    ) -> Optional[str]:
        """
        Generate an image using DALL-E 3 and save it locally.
        
        Args:
            prompt: Description of the image to generate
            size: Image size - "1024x1024", "1024x1792", or "1792x1024"
            quality: "standard" ($0.04) or "hd" ($0.08)
            style: "natural" or "vivid"
            base_url: Base URL for serving the saved image
        
        Returns:
            Local URL of the saved image, or None if generation fails
        """
        try:
            print(f"🎨 Generating image with DALL-E 3...")
            
            # Ensure images directory exists
            os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)
            
            # Enhance prompt for child-friendly educational images
            enhanced_prompt = f"""Create a simple, colorful, child-friendly educational illustration for kindergarten students (ages 6-10). 
            
The image should be:
- Bright and cheerful with a clean white or light background
- Clear and easy to understand for young children
- Safe and appropriate for educational use
- Cartoon-style or flat illustration style
- Without any text or numbers in the image

Subject: {prompt}"""
            
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size=size,
                quality=quality,
                style=style,
                n=1
            )
            
            dalle_url = response.data[0].url
            print(f"✅ DALL-E image generated, downloading...")
            
            # Download the image
            async with httpx.AsyncClient() as client:
                img_response = await client.get(dalle_url, timeout=60.0)
                if img_response.status_code == 200:
                    # Generate unique filename
                    filename = f"{uuid.uuid4().hex}.png"
                    filepath = os.path.join(STATIC_IMAGES_DIR, filename)
                    
                    # Save image locally
                    with open(filepath, "wb") as f:
                        f.write(img_response.content)
                    
                    # Return local URL
                    local_url = f"{base_url}/static/images/{filename}"
                    print(f"✅ Image saved locally: {filename}")
                    return local_url
                else:
                    print(f"⚠️ Failed to download image: {img_response.status_code}")
                    return None
            
        except Exception as e:
            error_msg = str(e)
            if "content_policy_violation" in error_msg.lower():
                print(f"⚠️ Content policy violation - skipping image generation")
            elif "insufficient_quota" in error_msg or "429" in error_msg:
                print(f"⚠️ DALL-E quota exceeded - skipping image generation")
            else:
                print(f"⚠️ Image generation failed: {error_msg}")
            return None
    
    async def generate_image_prompt_from_question(
        self,
        question_text: str,
        topic: str,
        objects: List[str],
        correct_answer: str = ""
    ) -> str:
        """
        Generate an appropriate image description for a question.
        Uses GPT to extract visual elements from the question.
        The correct answer is used to ensure accurate proportions/comparisons.
        """
        try:
            prompt = f"""Extract the main visual elements from this math question to create an educational illustration.

Question: {question_text}
Topic: {topic}
Related objects: {', '.join(objects)}
Correct Answer: {correct_answer}

CRITICAL REQUIREMENTS:
1. The image MUST accurately reflect the CORRECT ANSWER
2. If comparing sizes/lengths/weights, show the objects with ACCURATE proportions based on the correct answer
3. Example: If asking "which is longer, pen or book?" and the answer is "book", the book MUST be clearly BIGGER/LONGER than the pen
4. Example: If asking "which is heavier, apple or watermelon?" and the answer is "watermelon", the watermelon MUST appear LARGER/HEAVIER
5. Make objects clearly distinguishable with obvious size/measurement differences

Create a brief image description (2-3 sentences) that:
1. Shows the objects with CORRECT relative sizes/proportions based on the answer
2. Makes the measurement comparison visually obvious to children
3. Is suitable for a colorful children's illustration with clear, exaggerated differences

Return ONLY the image description, nothing else.
Example: "A large blue book (about 30cm) placed next to a small yellow pencil (about 15cm), clearly showing the book is much longer."
"""
            
            response = await self.generate_completion(
                prompt=prompt,
                system_message="You are an expert at creating accurate educational illustrations. You ALWAYS show correct proportions based on the answer.",
                temperature=0.5,  # Lower temperature for more accurate proportions
                max_tokens=150
            )
            
            return response.strip()
            
        except Exception as e:
            # Fallback to a simple description using the topic and objects
            print(f"⚠️ Could not generate image prompt: {str(e)}")
            return f"Educational illustration showing {topic} measurement with {objects[0] if objects else 'common objects'}"


# Singleton instance
llm_client = LLMClient()
