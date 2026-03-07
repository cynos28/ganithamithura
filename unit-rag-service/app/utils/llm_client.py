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
                    
                    # Return relative URL (frontend will prepend the correct base URL)
                    local_url = f"/static/images/{filename}"
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
        Generate a child-friendly, measurement-focused image description
        that makes the correct answer visually obvious.
        """
        try:
            # Build a stricter, layout-focused prompt so images clearly match the question
            prompt = f"""
You are designing ONE clear educational picture for young children (ages 6–10)
to go with a math measurement question.

QUESTION (for context only, do NOT write the question text in the image):
{question_text}

TOPIC: {topic}
TYPICAL OBJECTS IN THIS TOPIC: {', '.join(objects)}
CORRECT ANSWER (object or choice that must visually "win"): {correct_answer}

GLOBAL RULES FOR THE PICTURE:
- Show ONLY the few objects needed to answer the question (usually 2–3 items).
- Use a simple, bright, kid‑friendly cartoon style on a plain light background.
- Do NOT include any text, numbers, labels or arrows in the image.
- Avoid complex scenes or extra decorations that might distract from the comparison.
- Make the measurement idea so clear that a 6‑year‑old can answer just by looking.

IF IT IS A LENGTH / HEIGHT QUESTION:
- Place the objects side by side on the SAME straight baseline.
- The correct object MUST be clearly longer/taller than the other(s).
- Exaggerate the length difference so it is obvious at first glance.

IF IT IS A WEIGHT / MASS QUESTION:
- Show a very simple balance scale OR just the objects side by side.
- The heavier correct object should look noticeably larger/denser or tip the scale down.

IF IT IS AN AREA QUESTION:
- Show flat shapes or surfaces filled with solid color or tiles.
- The correct answer must clearly cover MORE surface area than the others.

IF IT IS A VOLUME / CAPACITY QUESTION:
- Show containers with visible liquid or blocks inside.
- The correct container must clearly hold MORE or LESS, with very different fill levels.

WHAT YOU MUST RETURN:
- Write 1–2 sentences describing exactly what should be drawn, including:
  - Which objects appear (with simple colors).
  - How they are arranged (left/right, on a table, on a scale, etc.).
  - How the correct answer is made visually obvious (bigger/longer/heavier/higher level).
- Do NOT mention the question text or any answer letters like A/B/C/D.

Example description:
"A bright blue storybook lying flat on a table, much longer than a short yellow pencil beside it, both aligned on the same straight line so it is clear the book is longer."
""".strip()

            response = await self.generate_completion(
                prompt=prompt,
                system_message=(
                    "You are an expert at creating accurate, child‑friendly educational illustrations. "
                    "You ALWAYS show correct visual proportions so the right answer is obvious to young students."
                ),
                temperature=0.5,  # Lower temperature for more consistent, precise layouts
                max_tokens=180,
            )

            return response.strip()

        except Exception as e:
            # Fallback to a simple description using the topic and objects
            print(f"⚠️ Could not generate image prompt: {str(e)}")
            return (
                f"Simple, colorful illustration showing {topic.lower()} measurement with "
                f"{objects[0] if objects else 'two everyday objects'} where the correct one is clearly larger for kids."
            )


# Singleton instance
llm_client = LLMClient()
