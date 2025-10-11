import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.generation import Generation, GenerationStatus
from src.models.algorithm import Algorithm
from src.services.ai_service import AIService
from src.core.database import AsyncSessionLocal
from src.core.config import settings


class GenerationService:
    """Service for managing thumbnail generation process."""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def process_generation(self, generation_id: UUID, db: Optional[AsyncSession] = None):
        """Process a thumbnail generation request."""
        
        # Use provided session or create new one
        if db is None:
            async with AsyncSessionLocal() as session:
                await self._process_generation_internal(generation_id, session)
        else:
            await self._process_generation_internal(generation_id, db)
    
    async def _process_generation_internal(self, generation_id: UUID, db: AsyncSession):
        """Internal method to process generation."""
        
        try:
            # Get generation record
            result = await db.execute(select(Generation).where(Generation.id == generation_id))
            generation = result.scalar_one_or_none()
            
            if not generation:
                print(f"Generation {generation_id} not found")
                return
            
            # Get algorithm details
            result = await db.execute(select(Algorithm).where(Algorithm.id == generation.algorithm_id))
            algorithm = result.scalar_one_or_none()
            
            if not algorithm:
                await self._mark_generation_failed(generation, "Algorithm not found", db)
                return
            
            # Mark as started
            generation.mark_as_started()
            await db.commit()
            
            # Step 1: Analyze prompt (10% progress)
            await self._update_progress(generation, 10, "Analyzing prompt...", db)
            
            reference_images = None
            if generation.reference_images:
                try:
                    reference_images = json.loads(generation.reference_images)
                except json.JSONDecodeError:
                    pass
            
            analysis = await self.ai_service.analyze_prompt(
                generation.prompt,
                reference_images
            )
            
            # Step 2: Find matching templates (30% progress)
            await self._update_progress(generation, 30, "Finding matching templates...", db)
            
            templates = await self.ai_service.find_matching_templates(analysis)
            
            if not templates:
                await self._mark_generation_failed(generation, "No matching templates found", db)
                return
            
            # Select best template
            best_template = templates[0]  # Highest match score
            
            # Step 3: Generate thumbnail (60% progress)
            await self._update_progress(generation, 60, "Generating thumbnail...", db)
            
            generation_result = await self.ai_service.generate_thumbnail(
                prompt=generation.prompt,
                template=best_template,
                algorithm=generation.algorithm_id,
                reference_images=reference_images
            )
            
            if not generation_result.get("success"):
                await self._mark_generation_failed(
                    generation,
                    "Thumbnail generation failed",
                    db
                )
                return
            
            # Step 4: Save and optimize result (90% progress)
            await self._update_progress(generation, 90, "Saving result...", db)
            
            # Save the generated image (mock implementation)
            result_url = await self._save_generated_image(
                generation_result.get("image_url"),
                generation.user_id,
                generation.id
            )
            
            # Step 5: Complete generation (100% progress)
            metadata = {
                "analysis": analysis,
                "template": best_template,
                "generation_details": generation_result.get("metadata", {}),
                "processing_time": generation_result.get("processing_time", 0)
            }
            
            generation.mark_as_completed(
                result_url=result_url,
                metadata=json.dumps(metadata)
            )
            
            await db.commit()
            
            print(f"Generation {generation_id} completed successfully")
            
        except Exception as e:
            print(f"Error processing generation {generation_id}: {e}")
            
            # Get generation again in case of error
            result = await db.execute(select(Generation).where(Generation.id == generation_id))
            generation = result.scalar_one_or_none()
            
            if generation:
                await self._mark_generation_failed(generation, str(e), db)
    
    async def _update_progress(
        self,
        generation: Generation,
        progress: int,
        message: str,
        db: AsyncSession
    ):
        """Update generation progress."""
        
        generation.update_progress(progress)
        await db.commit()
        
        print(f"Generation {generation.id}: {progress}% - {message}")
        
        # Small delay to simulate processing
        await asyncio.sleep(0.5)
    
    async def _mark_generation_failed(
        self,
        generation: Generation,
        error_message: str,
        db: AsyncSession
    ):
        """Mark generation as failed."""
        
        generation.mark_as_failed(error_message)
        await db.commit()
        
        print(f"Generation {generation.id} failed: {error_message}")
    
    async def _save_generated_image(
        self,
        image_url: str,
        user_id: UUID,
        generation_id: UUID
    ) -> str:
        """Save generated image to local storage."""
        
        # Create directory for generated images
        generated_dir = os.path.join(settings.upload_dir, "generated", str(user_id))
        os.makedirs(generated_dir, exist_ok=True)
        
        # Generate filename
        filename = f"{generation_id}.jpg"
        file_path = os.path.join(generated_dir, filename)
        
        # In a real implementation, you would download the image from image_url
        # For now, we'll create a placeholder file
        try:
            # Create a placeholder image file
            with open(file_path, 'w') as f:
                f.write(f"Generated thumbnail for {generation_id}")
            
            # Return the URL path
            return f"/uploads/generated/{user_id}/{filename}"
            
        except Exception as e:
            print(f"Error saving generated image: {e}")
            # Return the original URL as fallback
            return image_url
    
    async def get_generation_progress(self, generation_id: UUID) -> Optional[Dict[str, Any]]:
        """Get current progress of a generation."""
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Generation).where(Generation.id == generation_id))
            generation = result.scalar_one_or_none()
            
            if not generation:
                return None
            
            return {
                "generation_id": generation.id,
                "status": generation.status,
                "progress": generation.progress,
                "error_message": generation.error_message,
                "created_at": generation.created_at,
                "started_at": generation.started_at,
                "completed_at": generation.completed_at
            }
    
    async def cancel_generation(self, generation_id: UUID) -> bool:
        """Cancel a generation if it's still in progress."""
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Generation).where(Generation.id == generation_id))
            generation = result.scalar_one_or_none()
            
            if not generation:
                return False
            
            if generation.status in [GenerationStatus.QUEUED, GenerationStatus.PROCESSING]:
                generation.status = GenerationStatus.CANCELLED
                await db.commit()
                return True
            
            return False
