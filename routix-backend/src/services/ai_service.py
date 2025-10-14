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
        """Generate thumbnail using Stable Diffusion (mock implementation)."""
        
        # Mock generation - in real implementation, this would call Stable Diffusion API
        await asyncio.sleep(2)  # Simulate processing time
        
        return {
            "success": True,
            "image_url": f"/generated/stable_diffusion_{hash(prompt) % 10000}.jpg",
            "algorithm": "stable-diffusion",
            "processing_time": 2.0,
            "metadata": {
                "model": "stable-diffusion-xl",
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
        """Generate thumbnail using Midjourney (mock implementation)."""
        
        # Mock generation - in real implementation, this would call Midjourney API
        await asyncio.sleep(10)  # Simulate longer processing time
        
        return {
            "success": True,
            "image_url": f"/generated/midjourney_{hash(prompt) % 10000}.jpg",
            "algorithm": "midjourney",
            "processing_time": 10.0,
            "metadata": {
                "model": "midjourney-v6",
                "quality": "ultra",
                "aspect_ratio": "16:9"
            }
        }
