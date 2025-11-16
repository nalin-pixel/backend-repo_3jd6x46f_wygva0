"""
Database Schemas for The Time-Traveler Codex

Each Pydantic model maps to a MongoDB collection (lowercased class name).
These schemas are used for validation and by the Flames database viewer.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal

class Era(BaseModel):
    key: str = Field(..., description="Unique slug-like identifier, e.g., 'ancient'")
    name: str = Field(..., description="Display name of the era")
    theme: Literal["ancient","medieval","industrial","cyber","cosmic","custom"] = Field("custom")
    description: Optional[str] = Field(None, description="Short description for the era")
    colors: Optional[dict] = Field(default=None, description="Optional color tokens for UI theming")
    background_media: Optional[str] = Field(default=None, description="Image/Video URL for background")

class ProjectMedia(BaseModel):
    image: Optional[str] = None
    video: Optional[str] = None
    model: Optional[str] = None

class Project(BaseModel):
    title: str
    era_key: str = Field(..., description="Which era this project belongs to (matches Era.key)")
    subtitle: Optional[str] = None
    description: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    result: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)
    github: Optional[HttpUrl] = None
    live_url: Optional[HttpUrl] = None
    media: Optional[ProjectMedia] = None
    showcase_data: Optional[dict] = None

class Skill(BaseModel):
    name: str
    level: int = Field(75, ge=0, le=100)
    category: str = Field("General")
    icon: Optional[str] = Field(None, description="Lucide icon name or URL")

class Achievement(BaseModel):
    title: str
    description: Optional[str] = None
    year: Optional[int] = None
    certificate_url: Optional[HttpUrl] = None
    capsule: Literal["pulse","orbit","glow","spark"] = Field("glow")

class Profile(BaseModel):
    name: str
    role: str
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    timeline: List[dict] = Field(default_factory=list, description="List of {year, title, text}")
    links: List[dict] = Field(default_factory=list, description="List of {label, url}")

# Example schemas kept for reference (not used by Codex)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
