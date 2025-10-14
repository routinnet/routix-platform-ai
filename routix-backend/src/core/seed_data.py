from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.algorithm import Algorithm
from src.models.user import User
from src.models.template import Template
from src.core.security import get_password_hash


import json

async def seed_algorithms(db: AsyncSession):
    """Seed the database with default algorithms."""
    
    algorithms_data = [
        {
            "id": "basic",
            "name": "basic",
            "display_name": "Basic Generation",
            "description": "Fast and efficient thumbnail generation using Stable Diffusion. Perfect for quick results.",
            "cost_credits": 1,
            "is_active": True,
            "parameters": json.dumps({
                "model": "stable-diffusion-xl",
                "steps": 20,
                "guidance_scale": 7.5,
                "resolution": "1280x720"
            })
        },
        {
            "id": "premium",
            "name": "premium", 
            "display_name": "Premium Generation",
            "description": "High-quality thumbnail generation using DALL-E 3. Superior quality and detail.",
            "cost_credits": 3,
            "is_active": True,
            "parameters": json.dumps({
                "model": "dall-e-3",
                "quality": "hd",
                "resolution": "1792x1024"
            })
        },
        {
            "id": "pro",
            "name": "pro",
            "display_name": "Pro Generation", 
            "description": "Professional-grade thumbnail generation using Midjourney. Ultra-high quality results.",
            "cost_credits": 5,
            "is_active": True,
            "parameters": json.dumps({
                "model": "midjourney-v6",
                "quality": "ultra",
                "aspect_ratio": "16:9"
            })
        }
    ]
    
    for algo_data in algorithms_data:
        # Check if algorithm already exists
        result = await db.execute(select(Algorithm).where(Algorithm.id == algo_data["id"]))
        existing = result.scalar_one_or_none()
        
        if not existing:
            algorithm = Algorithm(**algo_data)
            db.add(algorithm)
    
    await db.commit()
    print("Algorithms seeded successfully")


async def seed_test_user(db: AsyncSession):
    """Create a test user for development."""
    
    test_email = "test@routix.com"
    
    # Check if test user already exists
    result = await db.execute(select(User).where(User.email == test_email))
    existing = result.scalar_one_or_none()
    
    if not existing:
        test_user = User(
            email=test_email,
            username="testuser",
            password_hash=get_password_hash("pass123"),
            credits=100,  # Give test user some credits
            is_verified=True
        )
        
        db.add(test_user)
        await db.commit()
        print("Test user created successfully")
    else:
        print("Test user already exists")


async def seed_templates(db: AsyncSession):
    """Seed the database with template data."""
    
    templates_data = Template.get_seed_templates()
    
    for template_data in templates_data:
        # Check if template already exists by name
        result = await db.execute(
            select(Template).where(Template.name == template_data["name"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            template = Template(**template_data)
            db.add(template)
    
    await db.commit()
    print("Templates seeded successfully")


async def seed_database(db: AsyncSession):
    """Seed the database with initial data."""
    
    print("Seeding database...")
    
    await seed_algorithms(db)
    await seed_test_user(db)
    await seed_templates(db)
    
    print("Database seeding completed")
