import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List

from database import db, create_document, get_documents

app = FastAPI(title="The Time-Traveler Codex API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Time-Traveler Codex Backend Running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the Codex API!"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# ----------------------------
# Content API
# Collections used:
#   era, project, skill, achievement, profile
# ----------------------------

class AnyPayload(BaseModel):
    data: Dict[str, Any]

@app.get("/api/content")
def get_all_content():
    content = {
        "eras": [],
        "projects": [],
        "skills": [],
        "achievements": [],
        "profile": None,
        "styles": {}
    }
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    content["eras"] = get_documents("era")
    content["projects"] = get_documents("project")
    content["skills"] = get_documents("skill")
    content["achievements"] = get_documents("achievement")
    profiles = get_documents("profile")
    content["profile"] = profiles[0] if profiles else None

    # Global styles stored in a single doc in collection 'styles' with key 'global'
    try:
        styles = list(db["styles"].find({"key": "global"}).limit(1))
        content["styles"] = styles[0] if styles else {"key": "global", "theme": "cyber", "glow": 0.6}
    except Exception:
        content["styles"] = {"key": "global", "theme": "cyber", "glow": 0.6}

    return content

@app.post("/api/eras")
def create_era(payload: AnyPayload):
    era_id = create_document("era", payload.data)
    return {"inserted_id": era_id}

@app.post("/api/projects")
def create_project_api(payload: AnyPayload):
    proj_id = create_document("project", payload.data)
    return {"inserted_id": proj_id}

@app.post("/api/skills")
def create_skill_api(payload: AnyPayload):
    skill_id = create_document("skill", payload.data)
    return {"inserted_id": skill_id}

@app.post("/api/achievements")
def create_achievement_api(payload: AnyPayload):
    ach_id = create_document("achievement", payload.data)
    return {"inserted_id": ach_id}

@app.post("/api/profile")
def set_profile_api(payload: AnyPayload):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    # upsert single profile
    db["profile"].delete_many({})
    prof_id = create_document("profile", payload.data)
    return {"inserted_id": prof_id}

@app.post("/api/styles")
def set_styles_api(payload: AnyPayload):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    db["styles"].delete_many({"key": "global"})
    payload.data["key"] = "global"
    sid = create_document("styles", payload.data)
    return {"inserted_id": sid}

# ----------------------------
# Seed endpoint to bootstrap demo content
# ----------------------------
@app.post("/api/seed")
def seed_demo():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    # only seed if empty
    if db["era"].count_documents({}) > 0:
        return {"status": "already-seeded"}

    eras = [
        {"key": "ancient", "name": "Ancient Civilization Era", "theme": "ancient", "description": "Desert ruins under golden sunlight."},
        {"key": "medieval", "name": "Medieval Arcane Era", "theme": "medieval", "description": "Arcane library of glowing runes."},
        {"key": "industrial", "name": "Industrial Revolution", "theme": "industrial", "description": "Steam, gears and copper pipes."},
        {"key": "cyber", "name": "Cyber Age (2080)", "theme": "cyber", "description": "Neon holographic interfaces."},
        {"key": "cosmic", "name": "Cosmic Future", "theme": "cosmic", "description": "Deep space and energy spheres."},
    ]
    for e in eras:
        create_document("era", e)

    demo_projects = [
        {
            "title": "Solar Cartographer",
            "era_key": "ancient",
            "subtitle": "Mapping constellations in desert skies",
            "description": "A data-vis project styled as floating artifacts.",
            "problem": "Scattered star data.",
            "solution": "Unified visual cartography.",
            "result": "Faster insights.",
            "tech_stack": ["D3.js", "Python"],
            "media": {"image": "", "video": "", "model": ""}
        },
        {
            "title": "Grimoire Engine",
            "era_key": "medieval",
            "subtitle": "Generative spellbook UI",
            "description": "Floating spellbooks reveal interactive pages.",
            "tech_stack": ["React", "Framer Motion"]
        },
        {
            "title": "CopperWorks",
            "era_key": "industrial",
            "subtitle": "Blueprint renderer",
            "description": "Mechanical blueprints unfold with details.",
            "tech_stack": ["Three.js", "Node"]
        },
        {
            "title": "Neon Nexus",
            "era_key": "cyber",
            "subtitle": "Holographic dashboard",
            "description": "Glowing tiles materialize project windows.",
            "tech_stack": ["React", "WebGL"]
        },
        {
            "title": "Cosmic Lattice",
            "era_key": "cosmic",
            "subtitle": "Orbital knowledge base",
            "description": "Energy spheres open cosmic info panels.",
            "tech_stack": ["Three.js", "GSAP"]
        },
    ]
    for p in demo_projects:
        create_document("project", p)

    skills = [
        {"name": "React", "level": 90, "category": "Frontend", "icon": "Atom"},
        {"name": "Three.js", "level": 80, "category": "3D", "icon": "Cube"},
        {"name": "FastAPI", "level": 85, "category": "Backend", "icon": "Server"},
    ]
    for s in skills:
        create_document("skill", s)

    achievements = [
        {"title": "Hackathon Winner", "description": "Built an AR prototype in 24h", "year": 2023, "capsule": "orbit"}
    ]
    for a in achievements:
        create_document("achievement", a)

    profile = {
        "name": "The Time Traveler",
        "role": "Creative Technologist",
        "photo_url": "",
        "bio": "Jumping across eras to craft immersive experiences.",
        "timeline": [
            {"year": 2018, "title": "First Expedition", "text": "Discovered the Ancient Codex"},
            {"year": 2022, "title": "Cyber Age", "text": "Built neon universes"}
        ],
        "links": [
            {"label": "GitHub", "url": "https://github.com/"},
            {"label": "LinkedIn", "url": "https://linkedin.com/"}
        ]
    }
    create_document("profile", profile)

    db["styles"].delete_many({"key": "global"})
    create_document("styles", {"key": "global", "theme": "cyber", "glow": 0.7})

    return {"status": "seeded"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
