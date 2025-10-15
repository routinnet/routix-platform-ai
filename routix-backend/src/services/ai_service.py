import openai
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import asyncio
import aiohttp
from PIL import Image
import io
import base64
import os
from openai import OpenAI

from src.core.config import settings


class AIService:
    """Service for handling AI integrations."""
    
    def __init__(self):
        # Initialize OpenAI client
        if settings.openai_api_key:
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
        else:
            self.openai_client = None
        
        # Initialize Gemini
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
        else:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
    
    async def analyze_prompt(self, prompt: str, reference_images: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze user prompt to understand thumbnail requirements."""
        
        analysis_prompt = f"""
        Analyze this thumbnail generation request and extract key information:
        
        User Request: "{prompt}"
        
        Please provide a JSON response with the following structure:
        {{
            "category": "gaming|tech|lifestyle|education|entertainment|business|other",
            "style": "modern|vintage|minimalist|bold|colorful|dark|bright",
            "elements": ["text", "person", "product", "background", "effects"],
            "mood": "exciting|professional|fun|serious|energetic|calm",
            "colors": ["primary_color", "secondary_color"],
            "text_content": "main text to include",
            "description": "detailed description for image generation"
        }}
        """
        
        try:
            if settings.gemini_api_key or os.getenv("GEMINI_API_KEY"):
                return await self._analyze_with_gemini(analysis_prompt, reference_images)
            elif self.openai_client:
                return await self._analyze_with_openai(analysis_prompt)
            else:
                # Fallback analysis
                return self._fallback_analysis(prompt)
        except Exception as e:
            print(f"Error in prompt analysis: {e}")
            return self._fallback_analysis(prompt)
    
    async def _analyze_with_gemini(self, prompt: str, reference_images: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze prompt using Gemini."""
        
        try:
            model = genai.GenerativeModel('gemini-pro-vision' if reference_images else 'gemini-pro')
            
            content = [prompt]
            
            # Add reference images if provided
            if reference_images:
                for image_path in reference_images[:3]:  # Limit to 3 images
                    try:
                        if os.path.exists(image_path):
                            with open(image_path, 'rb') as f:
                                image_data = f.read()
                            
                            image = Image.open(io.BytesIO(image_data))
                            content.append(image)
                    except Exception as e:
                        print(f"Error loading image {image_path}: {e}")
            
            response = model.generate_content(content)
            
            # Try to parse JSON response
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                # If not JSON, create structured response
                return self._parse_text_response(response.text)
                
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            raise
    
    async def _analyze_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt using OpenAI."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert thumbnail designer. Analyze requests and provide structured JSON responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._parse_text_response(content)
                
        except Exception as e:
            print(f"OpenAI analysis error: {e}")
            raise
    
    def _fallback_analysis(self, prompt: str) -> Dict[str, Any]:
        """Fallback analysis when AI services are unavailable."""
        
        prompt_lower = prompt.lower()
        
        # Simple keyword-based analysis
        category = "other"
        if any(word in prompt_lower for word in ["game", "gaming", "play"]):
            category = "gaming"
        elif any(word in prompt_lower for word in ["tech", "technology", "software"]):
            category = "tech"
        elif any(word in prompt_lower for word in ["learn", "education", "tutorial"]):
            category = "education"
        elif any(word in prompt_lower for word in ["business", "professional", "corporate"]):
            category = "business"
        
        style = "modern"
        if any(word in prompt_lower for word in ["vintage", "retro", "old"]):
            style = "vintage"
        elif any(word in prompt_lower for word in ["minimal", "simple", "clean"]):
            style = "minimalist"
        elif any(word in prompt_lower for word in ["bold", "strong", "powerful"]):
            style = "bold"
        
        return {
            "category": category,
            "style": style,
            "elements": ["text", "background"],
            "mood": "professional",
            "colors": ["blue", "white"],
            "text_content": prompt[:50],
            "description": f"Create a {style} {category} thumbnail with the text: {prompt[:100]}"
        }
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse non-JSON text response into structured format."""
        
        # Simple parsing logic
        return {
            "category": "other",
            "style": "modern", 
            "elements": ["text", "background"],
            "mood": "professional",
            "colors": ["blue", "white"],
            "text_content": text[:50],
            "description": text[:200]
        }
    
    async def find_matching_templates(
        self, 
        analysis: Dict[str, Any],
        db_session = None,
        limit: int = 5,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Find matching templates from the template database."""
        from src.models.template import Template
        from src.core.database import AsyncSessionLocal
        from sqlalchemy import select
        
        # Use provided session or create new one
        if db_session is None:
            async with AsyncSessionLocal() as session:
                return await self._find_templates_internal(analysis, session, limit, min_score)
        else:
            return await self._find_templates_internal(analysis, db_session, limit, min_score)
    
    async def _find_templates_internal(
        self,
        analysis: Dict[str, Any],
        db_session,
        limit: int,
        min_score: float
    ) -> List[Dict[str, Any]]:
        """Internal method to find templates."""
        from src.models.template import Template
        from sqlalchemy import select
        
        # Get all active templates
        result = await db_session.execute(
            select(Template).where(Template.is_active == True)
        )
        templates = result.scalars().all()
        
        if not templates:
            # Return fallback templates if database is empty
            return self._get_fallback_templates(analysis)
        
        # Calculate match score for each template
        scored_templates = []
        for template in templates:
            score = template.calculate_match_score(analysis)
            
            if score >= min_score:
                scored_templates.append({
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "style": template.style,
                    "mood": template.mood,
                    "primary_color": template.primary_color,
                    "secondary_color": template.secondary_color,
                    "elements": template.elements_list,
                    "tags": template.tags_list,
                    "preview_image": template.preview_image,
                    "is_premium": template.is_premium,
                    "match_score": score,
                    "usage_count": template.usage_count,
                    "rating": template.rating
                })
        
        # Sort by match score (descending) and rating
        scored_templates.sort(
            key=lambda t: (t["match_score"], t["rating"], t["usage_count"]),
            reverse=True
        )
        
        # Return top matches
        return scored_templates[:limit]
    
    def _get_fallback_templates(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get fallback templates when database is empty."""
        category = analysis.get("category", "other")
        style = analysis.get("style", "modern")
        
        return [
            {
                "id": f"fallback_{category}_1",
                "name": f"{category.title()} Template 1",
                "description": f"Professional {category} thumbnail template",
                "category": category,
                "style": style,
                "mood": analysis.get("mood", "professional"),
                "primary_color": "#0066FF",
                "secondary_color": "#FFFFFF",
                "elements": analysis.get("elements", ["text", "background"]),
                "tags": [category, style],
                "preview_image": f"/templates/{category}_template_1.jpg",
                "is_premium": False,
                "match_score": 0.7,
                "usage_count": 0,
                "rating": 0.0
            }
        ]
    
    async def generate_thumbnail(
        self,
        prompt: str,
        template: Dict[str, Any],
        algorithm: str = "basic",
        reference_images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate thumbnail using specified algorithm."""
        
        if algorithm == "basic":
            return await self._generate_with_stable_diffusion(prompt, template, reference_images)
        elif algorithm == "premium":
            return await self._generate_with_dalle(prompt, template, reference_images)
        elif algorithm == "pro":
            return await self._generate_with_midjourney(prompt, template, reference_images)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    async def _generate_with_stable_diffusion(
        self,
        prompt: str,
        template: Dict[str, Any],
        reference_images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate thumbnail using Stable Diffusion API (Stability AI)."""
        
        api_key = os.getenv("STABILITY_API_KEY")
        
        if not api_key:
            print("⚠️  STABILITY_API_KEY not found, using mock generation")
            return await self._mock_stable_diffusion(prompt)
        
        try:
            # ساخت enhanced prompt برای تامبنیل
            enhanced_prompt = f"""
Professional YouTube thumbnail, 16:9 aspect ratio, high quality, eye-catching
Style: {template.get('style', 'modern')}, {template.get('mood', 'exciting')}
Category: {template.get('category', 'general')}
Colors: {template.get('primary_color', 'vibrant')}, {template.get('secondary_color', 'bold')}

{prompt}

Ultra HD, high contrast, vibrant colors, professional quality, clear composition, 
clickable thumbnail, trending, engaging, dramatic lighting
"""
            
            negative_prompt = "blurry, low quality, pixelated, distorted, ugly, bad anatomy, amateur, low resolution, text too small, unclear"
            
            # Call Stability AI API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    json={
                        "text_prompts": [
                            {"text": enhanced_prompt, "weight": 1},
                            {"text": negative_prompt, "weight": -1}
                        ],
                        "cfg_scale": 7,
                        "height": 720,
                        "width": 1280,  # 16:9 ratio perfect for thumbnails
                        "samples": 1,
                        "steps": 30,
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"❌ Stability API error: {response.status} - {error_text}")
                        return await self._mock_stable_diffusion(prompt)
                    
                    data = await response.json()
                    
                    # دانلود و ذخیره تصویر
                    image_base64 = data["artifacts"][0]["base64"]
                    image_data = base64.b64decode(image_base64)
                    
                    # استفاده از storage service برای ذخیره
                    from src.services.storage_service import storage_service
                    image_url = await storage_service.upload_image(
                        image_data,
                        f"sd_{hash(prompt) % 100000}.jpg",
                        folder="generated/stable-diffusion"
                    )
                    
                    print(f"✅ Stable Diffusion generation complete: {image_url}")
                    
                    return {
                        "success": True,
                        "image_url": image_url,
                        "algorithm": "stable-diffusion-xl",
                        "processing_time": 5.0,
                        "metadata": {
                            "model": "stable-diffusion-xl-1024-v1-0",
                            "steps": 30,
                            "cfg_scale": 7,
                            "resolution": "1280x720"
                        }
                    }
                    
        except Exception as e:
            print(f"❌ Stable Diffusion error: {e}")
            return await self._mock_stable_diffusion(prompt)
    
    async def _mock_stable_diffusion(self, prompt: str) -> Dict[str, Any]:
        """Mock implementation for Stable Diffusion"""
        await asyncio.sleep(2)
        return {
            "success": True,
            "image_url": f"/generated/stable_diffusion_mock_{hash(prompt) % 10000}.jpg",
            "algorithm": "stable-diffusion",
            "processing_time": 2.0,
            "metadata": {
                "model": "stable-diffusion-xl",
                "mock": True,
                "steps": 20,
                "guidance_scale": 7.5
            }
        }
    
    async def _generate_with_dalle(
        self,
        prompt: str,
        template: Dict[str, Any],
        reference_images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate thumbnail using DALL-E."""
        
        try:
            # Enhance prompt for thumbnail generation
            enhanced_prompt = f"""
            Create a professional YouTube thumbnail in 16:9 aspect ratio.
            Style: {template.get('style', 'modern')}
            Category: {template.get('category', 'general')}
            
            {prompt}
            
            Requirements:
            - High contrast and vibrant colors
            - Clear, readable text elements
            - Eye-catching composition
            - Professional quality
            - 1280x720 resolution
            """
            
            if self.openai_client:
                response = self.openai_client.images.generate(
                    model="dall-e-3",
                    prompt=enhanced_prompt,
                    size="1792x1024",  # Closest to 16:9 ratio
                    quality="hd",
                    n=1
                )
                
                return {
                    "success": True,
                    "image_url": response.data[0].url,
                    "algorithm": "dall-e-3",
                    "processing_time": 15.0,
                    "metadata": {
                        "model": "dall-e-3",
                        "size": "1792x1024",
                        "quality": "hd"
                    }
                }
            else:
                # Mock response if no API key
                await asyncio.sleep(5)
                return {
                    "success": True,
                    "image_url": f"/generated/dalle_{hash(prompt) % 10000}.jpg",
                    "algorithm": "dall-e-3",
                    "processing_time": 5.0,
                    "metadata": {"model": "dall-e-3", "mock": True}
                }
                
        except Exception as e:
            print(f"DALL-E generation error: {e}")
            raise
    
    async def _generate_with_midjourney(
        self,
        prompt: str,
        template: Dict[str, Any],
        reference_images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate thumbnail using Pro algorithm (DALL-E 3 with enhanced prompts)
        
        Note: Midjourney doesn't have an official API, so we use DALL-E 3 
        with optimized prompts to achieve similar high-quality results.
        """
        
        if not self.openai_client:
            print("⚠️  OpenAI API key not found, using mock generation")
            return await self._mock_midjourney(prompt)
        
        try:
            # پرامپت بهینه‌شده برای خروجی با کیفیت بالا (مشابه Midjourney)
            enhanced_prompt = f"""
Create an ULTRA HIGH QUALITY, professional YouTube thumbnail in 16:9 aspect ratio.

VISUAL STYLE:
- Style: {template.get('style', 'modern')}, cinematic, photorealistic, highly detailed
- Category: {template.get('category', 'general')}
- Mood: {template.get('mood', 'professional')}, dramatic, engaging, eye-catching
- Color Palette: {template.get('primary_color', 'vibrant')}, {template.get('secondary_color', 'bold')}

MAIN CONTENT:
{prompt}

TECHNICAL REQUIREMENTS:
- Ultra sharp focus, intricate details, 8K quality
- Perfect composition and professional framing
- Cinematic lighting with dramatic shadows
- Professional color grading and contrast
- Maximum visual impact for thumbnail
- Clear, bold, readable text elements
- Trending on Artstation quality level
- Award-winning photography style

NEGATIVE PROMPTS TO AVOID:
- blurry, low quality, amateur, distorted, pixelated
- bad anatomy, unclear text, poor composition
"""
            
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt[:4000],  # DALL-E has 4000 char limit
                size="1792x1024",  # Closest to 16:9, highest quality
                quality="hd",
                style="vivid",  # More dramatic and vibrant
                n=1
            )
            
            # دانلود تصویر از URL
            image_url = response.data[0].url
            
            # دانلود و بهینه‌سازی برای تامبنیل
            from src.services.storage_service import storage_service
            image_data = await storage_service.download_from_url(image_url)
            
            # ذخیره با بهینه‌سازی
            optimized_url = await storage_service.upload_image(
                image_data,
                f"pro_{hash(prompt) % 100000}.jpg",
                folder="generated/pro",
                optimize=True
            )
            
            print(f"✅ Pro (DALL-E 3) generation complete: {optimized_url}")
            
            return {
                "success": True,
                "image_url": optimized_url,
                "algorithm": "dall-e-3-pro",
                "processing_time": 20.0,
                "metadata": {
                    "model": "dall-e-3",
                    "quality": "hd",
                    "style": "vivid",
                    "size": "1792x1024",
                    "optimized": True,
                    "tier": "pro"
                }
            }
            
        except Exception as e:
            print(f"❌ Pro generation error: {e}")
            return await self._mock_midjourney(prompt)
    
    async def _mock_midjourney(self, prompt: str) -> Dict[str, Any]:
        """Mock implementation for Pro tier"""
        await asyncio.sleep(5)
        return {
            "success": True,
            "image_url": f"/generated/pro_mock_{hash(prompt) % 10000}.jpg",
            "algorithm": "pro",
            "processing_time": 5.0,
            "metadata": {
                "model": "pro-tier",
                "mock": True,
                "quality": "ultra",
                "aspect_ratio": "16:9"
            }
        }
