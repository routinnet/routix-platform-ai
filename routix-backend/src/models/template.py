from sqlalchemy import Column, String, Text, Boolean, Integer, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json

from src.core.database import Base


class Template(Base):
    """Model for thumbnail templates."""
    __tablename__ = "templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Template categorization
    category = Column(String(50), nullable=False)  # gaming, tech, lifestyle, education, entertainment, business, other
    style = Column(String(50), nullable=False)  # modern, vintage, minimalist, bold, colorful, dark, bright
    mood = Column(String(50), nullable=False)  # exciting, professional, fun, serious, energetic, calm
    
    # Visual properties
    primary_color = Column(String(20), nullable=True)
    secondary_color = Column(String(20), nullable=True)
    color_scheme = Column(Text, nullable=True)  # JSON array of colors
    
    # Template elements and tags
    elements = Column(Text, nullable=True)  # JSON array: ["text", "person", "product", "background", "effects"]
    tags = Column(Text, nullable=True)  # JSON array of searchable tags
    
    # Template content
    preview_image = Column(String(500), nullable=True)  # URL or path to preview image
    template_file = Column(String(500), nullable=True)  # Path to template file (PSD, AI, etc.)
    thumbnail_specs = Column(Text, nullable=True)  # JSON with resolution, format, etc.
    
    # Usage and popularity
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)  # Average rating
    
    # Status
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)  # Premium templates require higher tier
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Template(id={self.id}, name={self.name}, category={self.category})>"

    @property
    def elements_list(self):
        """Get elements as a list."""
        if self.elements:
            try:
                return json.loads(self.elements)
            except json.JSONDecodeError:
                return []
        return []

    @property
    def tags_list(self):
        """Get tags as a list."""
        if self.tags:
            try:
                return json.loads(self.tags)
            except json.JSONDecodeError:
                return []
        return []

    @property
    def colors(self):
        """Get color scheme as a list."""
        if self.color_scheme:
            try:
                return json.loads(self.color_scheme)
            except json.JSONDecodeError:
                return [self.primary_color, self.secondary_color]
        return [self.primary_color, self.secondary_color]

    def calculate_match_score(
        self,
        analysis: dict,
        category_weight: float = 0.4,
        style_weight: float = 0.3,
        mood_weight: float = 0.2,
        element_weight: float = 0.1
    ) -> float:
        """
        Calculate how well this template matches the analysis.
        
        Args:
            analysis: Dictionary with category, style, mood, elements
            category_weight: Weight for category matching (default 0.4)
            style_weight: Weight for style matching (default 0.3)
            mood_weight: Weight for mood matching (default 0.2)
            element_weight: Weight for element matching (default 0.1)
            
        Returns:
            Match score between 0.0 and 1.0
        """
        score = 0.0
        
        # Category match
        if analysis.get('category') == self.category:
            score += category_weight
        
        # Style match
        if analysis.get('style') == self.style:
            score += style_weight
        
        # Mood match
        if analysis.get('mood') == self.mood:
            score += mood_weight
        
        # Element match
        analysis_elements = set(analysis.get('elements', []))
        template_elements = set(self.elements_list)
        if analysis_elements and template_elements:
            element_overlap = len(analysis_elements & template_elements) / len(analysis_elements)
            score += element_weight * element_overlap
        
        return min(score, 1.0)

    def increment_usage(self):
        """Increment usage counter."""
        self.usage_count += 1

    def update_rating(self, new_rating: float, total_ratings: int):
        """Update average rating."""
        if total_ratings > 0:
            self.rating = ((self.rating * (total_ratings - 1)) + new_rating) / total_ratings

    @classmethod
    def get_seed_templates(cls):
        """Get seed templates for initial database population."""
        return [
            # Gaming Templates
            {
                "name": "Epic Gaming Action",
                "description": "High-energy gaming thumbnail with bold colors and dynamic elements",
                "category": "gaming",
                "style": "bold",
                "mood": "exciting",
                "primary_color": "#FF0000",
                "secondary_color": "#000000",
                "color_scheme": '["#FF0000", "#000000", "#FFFF00", "#FFFFFF"]',
                "elements": '["text", "background", "effects"]',
                "tags": '["gaming", "action", "fps", "youtube", "twitch"]',
                "preview_image": "/templates/gaming_epic_action.jpg",
                "is_active": True,
                "is_premium": False
            },
            {
                "name": "Retro Gaming Nostalgia",
                "description": "Vintage-style gaming thumbnail with retro aesthetics",
                "category": "gaming",
                "style": "vintage",
                "mood": "fun",
                "primary_color": "#8B4513",
                "secondary_color": "#FFD700",
                "color_scheme": '["#8B4513", "#FFD700", "#CD853F", "#F4A460"]',
                "elements": '["text", "background", "effects"]',
                "tags": '["gaming", "retro", "vintage", "classic"]',
                "preview_image": "/templates/gaming_retro.jpg",
                "is_active": True,
                "is_premium": False
            },
            
            # Tech Templates
            {
                "name": "Modern Tech Innovation",
                "description": "Sleek and modern tech thumbnail with clean lines",
                "category": "tech",
                "style": "modern",
                "mood": "professional",
                "primary_color": "#0066FF",
                "secondary_color": "#FFFFFF",
                "color_scheme": '["#0066FF", "#FFFFFF", "#00CCFF", "#333333"]',
                "elements": '["text", "background", "product"]',
                "tags": '["tech", "technology", "modern", "innovation", "review"]',
                "preview_image": "/templates/tech_modern.jpg",
                "is_active": True,
                "is_premium": False
            },
            {
                "name": "Minimalist Tech Review",
                "description": "Clean and minimalist tech product showcase",
                "category": "tech",
                "style": "minimalist",
                "mood": "calm",
                "primary_color": "#FFFFFF",
                "secondary_color": "#333333",
                "color_scheme": '["#FFFFFF", "#333333", "#CCCCCC"]',
                "elements": '["text", "background", "product"]',
                "tags": '["tech", "minimal", "clean", "review", "product"]',
                "preview_image": "/templates/tech_minimalist.jpg",
                "is_active": True,
                "is_premium": True
            },
            
            # Education Templates
            {
                "name": "Educational Tutorial",
                "description": "Clear and professional educational content thumbnail",
                "category": "education",
                "style": "modern",
                "mood": "professional",
                "primary_color": "#4CAF50",
                "secondary_color": "#FFFFFF",
                "color_scheme": '["#4CAF50", "#FFFFFF", "#2196F3", "#333333"]',
                "elements": '["text", "background", "person"]',
                "tags": '["education", "tutorial", "learning", "teaching"]',
                "preview_image": "/templates/education_tutorial.jpg",
                "is_active": True,
                "is_premium": False
            },
            {
                "name": "Fun Learning",
                "description": "Engaging and colorful educational thumbnail",
                "category": "education",
                "style": "colorful",
                "mood": "fun",
                "primary_color": "#FF5722",
                "secondary_color": "#FFEB3B",
                "color_scheme": '["#FF5722", "#FFEB3B", "#4CAF50", "#2196F3"]',
                "elements": '["text", "background", "effects"]',
                "tags": '["education", "fun", "kids", "learning"]',
                "preview_image": "/templates/education_fun.jpg",
                "is_active": True,
                "is_premium": False
            },
            
            # Business Templates
            {
                "name": "Corporate Professional",
                "description": "Professional business presentation thumbnail",
                "category": "business",
                "style": "modern",
                "mood": "professional",
                "primary_color": "#1A237E",
                "secondary_color": "#FFFFFF",
                "color_scheme": '["#1A237E", "#FFFFFF", "#3F51B5", "#757575"]',
                "elements": '["text", "background", "person"]',
                "tags": '["business", "corporate", "professional", "presentation"]',
                "preview_image": "/templates/business_corporate.jpg",
                "is_active": True,
                "is_premium": True
            },
            
            # Lifestyle Templates
            {
                "name": "Lifestyle Vlog",
                "description": "Bright and energetic lifestyle vlog thumbnail",
                "category": "lifestyle",
                "style": "bright",
                "mood": "energetic",
                "primary_color": "#FF6F61",
                "secondary_color": "#FFFFFF",
                "color_scheme": '["#FF6F61", "#FFFFFF", "#FFD700", "#87CEEB"]',
                "elements": '["text", "background", "person"]',
                "tags": '["lifestyle", "vlog", "daily", "personal"]',
                "preview_image": "/templates/lifestyle_vlog.jpg",
                "is_active": True,
                "is_premium": False
            },
            
            # Entertainment Templates
            {
                "name": "Entertainment Hype",
                "description": "Eye-catching entertainment content thumbnail",
                "category": "entertainment",
                "style": "bold",
                "mood": "exciting",
                "primary_color": "#FF00FF",
                "secondary_color": "#00FFFF",
                "color_scheme": '["#FF00FF", "#00FFFF", "#FFFF00", "#000000"]',
                "elements": '["text", "background", "effects"]',
                "tags": '["entertainment", "fun", "exciting", "viral"]',
                "preview_image": "/templates/entertainment_hype.jpg",
                "is_active": True,
                "is_premium": False
            },
            {
                "name": "Dark Mode Entertainment",
                "description": "Dramatic dark-themed entertainment thumbnail",
                "category": "entertainment",
                "style": "dark",
                "mood": "serious",
                "primary_color": "#000000",
                "secondary_color": "#FF0000",
                "color_scheme": '["#000000", "#FF0000", "#8B0000", "#FFFFFF"]',
                "elements": '["text", "background", "effects"]',
                "tags": '["entertainment", "dark", "dramatic", "serious"]',
                "preview_image": "/templates/entertainment_dark.jpg",
                "is_active": True,
                "is_premium": True
            }
        ]
