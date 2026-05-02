from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import os
import json
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types
from typing import List, Optional
import httpx
import base64

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import bcrypt
from jose import JWTError, jwt

# Initialize environment & LLM Client
load_dotenv()
try:
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except Exception:
    gemini_client = None
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

# ---------------------------------------------------------
# Pinecone Cloud Vector DB Setup
# ---------------------------------------------------------
try:
    from pinecone import Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    # The host URL comes straight from the .env to bypass index lookups
    pinecone_index = pc.Index(host=os.getenv("PINECONE_HOST"))
    print("🧠 Pinecone Cloud DB Initialized & Ready")
except Exception as e:
    print(f"⚠️ Warning: Pinecone initialization failed: {e}")
    pinecone_index = None

def index_in_pinecone(document_id: str, title: str, text: str):
    """Synchronous background task to hit Gemini Embedding API and store directly into Pinecone."""
    if pinecone_index is None or gemini_client is None: return
    try:
        response = gemini_client.models.embed_content(
            model='gemini-embedding-2',
            contents=text,
        )
        vector = response.embeddings[0].values
        
        pinecone_index.upsert(
            vectors=[(document_id, vector, {"title": title, "content": text})],
            namespace="synapseip_notes"
        )
        print(f"✅ Pinecone Indexed: [{document_id}]")
    except Exception as e:
        print(f"❌ Pinecone Indexing Error: {e}")

def generate_short_memory(source_id: str):
    """Synchronous background task to compress raw source text into short-term memory."""
    db = SessionLocal()
    try:
        source = db.query(GeminiSource).filter(GeminiSource.id == int(source_id)).first()
        if not source or not source.content:
            return
            
        prompt = f"""Analyze the following brainstorm note and output a JSON object with two fields:
1. "title": A clean, 3-5 word title summarizing the core topic.
2. "summary": An extremely concise 2-3 sentence executive summary capturing the core intent/mechanic.

Return ONLY valid JSON.

Note:
{source.content}"""
        
        from google.genai import types
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        import json
        try:
            data = json.loads(response.text.strip())
            if "title" in data:
                source.title = data["title"]
            if "summary" in data:
                source.short_memory = data["summary"]
        except Exception as json_e:
            print(f"JSON Parsing Error: {json_e}. Raw text: {response.text}")
            source.short_memory = response.text.strip()
            
        source.processed = True
        db.commit()
        print(f"✅ Generated Short-Term Memory for: [{source_id}]")
    except Exception as e:
        print(f"❌ Short-Term Memory Error: {e}")
    finally:
        db.close()


# ---------------------------------------------------------
# Security Setup
# ---------------------------------------------------------
SECRET_KEY = "synapse_super_secret_matrix"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ---------------------------------------------------------
# Database Setup Setup
# ---------------------------------------------------------
import shutil

DATA_DIR = os.environ.get("DATA_DIR", ".")
target_db_path = os.path.join(DATA_DIR, 'gemini_sources.db')
seed_db_path = "seed_db.sqlite3"

if os.path.exists(seed_db_path):
    should_copy = False
    if not os.path.exists(target_db_path):
        should_copy = True
    elif os.path.getsize(target_db_path) < 100000:  # <100KB usually means it's an empty schema
        should_copy = True
        
    if should_copy:
        print(f"📦 Seeding persistent disk database from {seed_db_path}...")
        try:
            shutil.copy2(seed_db_path, target_db_path)
            print("✅ Database successfully seeded!")
        except Exception as e:
            print("❌ Failed to seed database:", e)

# Allow deployment to Render (Postgres) via DATABASE_URL, fallback to SQLite locally
if os.getenv("DATABASE_URL"):
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://")
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
else:
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{target_db_path}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    suggested_themes = Column(Text, nullable=True)
    notes_since_last_check = Column(Integer, default=0)
    current_vibe_step = Column(Integer, default=0)
    is_consistent = Column(Boolean, default=False)
    onboarding_config = Column(Text, nullable=True)
    followup_history = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class GeminiSource(Base):
    __tablename__ = "gemini_sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    title = Column(String, index=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_url = Column(String, index=True)
    processed = Column(Boolean, default=False)
    short_memory = Column(Text, nullable=True)

class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    report_data = Column(Text) # Stored serialized JSON
    timestamp = Column(DateTime, default=datetime.utcnow)

class ArchitectBlueprint(Base):
    __tablename__ = "architect_blueprints"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    blueprint_data = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ArchitectDraftState(Base):
    __tablename__ = "architect_draft_states"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True)
    current_loop = Column(Integer, default=0)
    loop0_draft = Column(Text, nullable=True)
    loop1_draft = Column(Text, nullable=True)
    loop2_draft = Column(Text, nullable=True)
    loop3_outline = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProjectTheme(Base):
    __tablename__ = "project_themes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    theme_name = Column(String, index=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ProjectThemeFragment(Base):
    __tablename__ = "project_theme_fragments"

    id = Column(Integer, primary_key=True, index=True)
    theme_id = Column(Integer, ForeignKey("project_themes.id"))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SystemConfig(Base):
    __tablename__ = "system_configs"
    key = Column(String, primary_key=True, index=True)
    value = Column(String)

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    phase = Column(String) # 'onboarding' or 'followup'
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class TokenLog(Base):
    __tablename__ = "token_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    action = Column(String, index=True)
    model_name = Column(String)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

class FrameworkTemplate(Base):
    __tablename__ = "framework_templates"
    id = Column(Integer, primary_key=True, index=True)
    normalized_name = Column(String, unique=True, index=True)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# ---------------------------------------------------------
# Pydantic Models for Validation
# ---------------------------------------------------------
class SourceCreate(BaseModel):
    title: str
    content: str
    source_url: str
    project_id: Optional[int] = None

class VisionSourceCreate(BaseModel):
    project_id: int
    source_url: str
    image_base64: str

class ProjectCreate(BaseModel):
    name: str

class ProjectUpdate(BaseModel):
    name: str

class VibeStepUpdate(BaseModel):
    step: int

class ProjectResponse(BaseModel):
    id: int
    name: str
    timestamp: datetime
    
    class Config:
        from_attributes = True



class AnalysisSchema(BaseModel):
    summary: str = Field(description="Brief product overview.")
    swot: str = Field(description="Strengths, Weaknesses, Opportunities, Threats.")
    market_analysis: str = Field(description="Top competitors, service differences, and Blue Ocean viability.")
    cost_benefit: str = Field(description="Financial and operational tradeoff of building it.")
    blindspots: str = Field(description="Other areas the user should consider brainstorming about to make the product better or more complete.")
    viability_score: int = Field(description="Integer from 0-100 indicating sure-fire success vs flop.")
    the_harsh_truth: str = Field(description="The single biggest 'Flop Risk' for this idea.")
    the_pivot_path: str = Field(description="One structural change to the idea that would increase its health score by at least 20 points.")
    verdict: str = Field(description="Either 'Green Light (Build)', 'Yellow Light (Refine)', or 'Red Light (Pivot/Abandon)'.")

class AnalyzeRequest(BaseModel):
    target_platform: str = "Antigravity"
    designer_name: str = ""
    app_name: str = ""
    app_purpose: str = ""
    target_audience: str = ""
    app_type: str = "Commercial"
    budget_constraints: str = "Free Tier Only"
    ai_integration: str = "None"
    security_auth: str = ""
    build_environment: str = "Greenfield (New)"
    standout_features: list[str] = []
    project_id: int

class MockupPromptRequest(BaseModel):
    project_id: int

class BulkDeleteRequest(BaseModel):
    source_ids: list[int]

class OutlineSchema(BaseModel):
    chapters: list[str]

class ArchitectLoopRequest(BaseModel):
    project_id: int
    target_platform: str
    designer_name: str
    app_name: str
    app_purpose: str
    budget_constraints: str
    ai_integration: str
    security_auth: str
    build_environment: str
    standout_features: list[str]
    feedback: Optional[str] = None

class BlueprintEditRequest(BaseModel):
    project_id: int
    highlighted_text: str
    instructions: Optional[str] = None
    container_preference: str = "auto"

class ArchitectStateResponse(BaseModel):
    current_loop: int
    loop0_draft: Optional[str] = None
    loop1_draft: Optional[str] = None
    loop2_draft: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class OnboardingRequest(BaseModel):
    project_id: int
    history: list[ChatMessage]

class FollowupRequest(BaseModel):
    project_id: int
    history: list[ChatMessage]

class OnboardingResponseSchema(BaseModel):
    message: str = Field(description="Your conversational reply or evaluation.")
    is_complete: bool = Field(description="True if Designer Name, App Name, Core Purpose, Target Audience, App Type, Budget/Hosting Constraints, Security Strategy, AI Integration, Build Environment, and Standout Features are confidently identified. False otherwise.")
    designer_name: Optional[str] = Field(description="Extracted designer name.", default=None)
    app_name: Optional[str] = Field(description="Extracted app name.", default=None)
    core_purpose: Optional[str] = Field(description="Extracted core purpose.", default=None)
    target_audience: Optional[str] = Field(description="Extracted target audience and target region/location.", default=None)
    app_type: Optional[str] = Field(description="Must be exactly either 'Personal' or 'Commercial'.", default=None)
    budget_constraints: Optional[str] = Field(description="Extracted budget and hosting constraints (e.g. 'Free Tier Only', 'Paid Enterprise', 'Undecided').", default=None)
    ai_integration: Optional[str] = Field(description="Extracted AI integration role, functionality, and thinking processes (or 'None' if standard deterministic app).", default=None)
    security_auth: Optional[str] = Field(description="Extracted Security and Authentication strategy (e.g. 'Clerk OAuth', 'JWT Custom', 'None required').", default=None)
    build_environment: Optional[str] = Field(description="Must be exactly either 'Greenfield (New)' or 'Brownfield (Existing)'.", default=None)
    standout_features: list[str] = Field(description="List of specific features that make this app stand out.", default_factory=list)

class PasswordChangeRequest(BaseModel):
    new_password: str

class SourceResponse(BaseModel):
    id: int
    title: str
    content: str
    timestamp: datetime
    source_url: str
    total_count: int = 0
    processed: bool = False

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ReportChangeRequest(BaseModel):
    hostname: str
    html_payload: str

class ThemeUpdateRequest(BaseModel):
    content: str

# ---------------------------------------------------------
# Security Helpers
# ---------------------------------------------------------
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ---------------------------------------------------------
from collections import defaultdict
import traceback

project_locks = defaultdict(asyncio.Lock)

async def call_with_retry(func, *args, retries=3, base_delay=10, **kwargs):
    import asyncio
    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "503" in err_str or "ResourceExhausted" in err_str:
                if attempt < retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    print(f"Rate limited. Retrying in {wait_time}s... (Attempt {attempt+1}/{retries})")
                    await asyncio.sleep(wait_time)
                else:
                    raise e
            else:
                raise e

async def process_single_card(unprocessed_dict):
    import json
    target_id = unprocessed_dict['id']
    raw_title = unprocessed_dict['title']
    raw_content = unprocessed_dict['content']
    target_project_id = unprocessed_dict['project_id']
    
    smart_title = raw_title
    try:
        db_cb = SessionLocal()
        try:
            proj = db_cb.query(Project).filter(Project.id == target_project_id).first()
            if proj:
                await check_circuit_breaker(proj.user_id, db_cb)
        finally:
            db_cb.close()
            
        await manager.broadcast(json.dumps({"type": "source_progress", "source_id": target_id, "message": "Initializing AI synthesis...", "progress": 10}))
        
        if gemini_client:
            # 1. Fetch existing themes
            db_themes = SessionLocal()
            try:
                existing_themes = db_themes.query(ProjectTheme).filter(ProjectTheme.project_id == target_project_id).all()
                theme_names = [t.theme_name for t in existing_themes]
            finally:
                db_themes.close()
            
            # 2. Extract Multiple Topics & Generate Title (Chunked to prevent 128k penalty)
            content_chunks = [raw_content[i:i+300000] for i in range(0, len(raw_content), 300000)]
            all_topics = []
            
            title_prompt = f"You are a neat summarization bot. Create a professional, catchy, 3 to 6 word title summarizing this interaction. Do not use quotes, labels, or generic prefixes. Only return the title itself.\n\nText: {raw_content[:1500]}"
            title_res = await call_with_retry(gemini_client.aio.models.generate_content, model='gemini-2.5-flash', contents=title_prompt)
            
            await manager.broadcast(json.dumps({"type": "source_progress", "source_id": target_id, "message": f"Extracting architectural themes (0/{len(content_chunks)} chunks)...", "progress": 30}))
            
            failed_chunks = []
            
            for chunk_idx, chunk in enumerate(content_chunks):
                extract_prompt = f"""
                Analyze the following brainstorm note and output a JSON object with two fields:
                1. "summary": A brief 1-sentence summary of what this note is about.
                2. "topics": An array of specific architectural components, UI features, or concepts discussed in the text.
                
                CRITICAL RULES:
                - You MUST extract a maximum of 5 topics. Only pick the top 3 to 5 most important core concepts.
                - If a topic strongly matches an existing theme from this project, use that EXACT existing theme name.
                - Current existing themes for this project: {theme_names if theme_names else 'None'}
                
                JSON FORMAT:
                {{
                    "summary": "...",
                    "topics": [
                        {{"topic": "Theme Name", "content": "The actual detailed insight from the text"}}
                    ]
                }}
                
                Raw Note (Part {chunk_idx+1}/{len(content_chunks)}): {chunk}
                """
                
                extract_res = await call_with_retry(
                    gemini_client.aio.models.generate_content,
                    model='gemini-2.5-flash',
                    contents=extract_prompt,
                    config={'response_mime_type': 'application/json'}
                )
                
                temp_db = SessionLocal()
                try:
                    await log_token_usage(temp_db, f"Note Categorization (Chunk {chunk_idx+1})", "gemini-2.5-flash", extract_res, project_id=target_project_id)
                finally:
                    temp_db.close()
                    
                try:
                    parsed = json.loads(extract_res.text.replace('```json', '').replace('```', '').strip())
                    chunk_topics = parsed.get("topics", []) if isinstance(parsed, dict) else parsed
                    if isinstance(chunk_topics, list):
                        all_topics.extend(chunk_topics)
                except Exception as parse_e:
                    failed_chunks.append(f"Chunk {chunk_idx+1}/{len(content_chunks)}: JSON Parsing Failed ({str(parse_e)[:50]})")
                
                await manager.broadcast(json.dumps({"type": "source_progress", "source_id": target_id, "message": f"Extracting architectural themes ({chunk_idx+1}/{len(content_chunks)} chunks)...", "progress": 30 + int(20 * (chunk_idx+1)/len(content_chunks))}))
                await asyncio.sleep(1) # Prevent rate limits
                
            temp_db = SessionLocal()
            try:
                await log_token_usage(temp_db, "Note Titling", "gemini-2.5-flash", title_res, project_id=target_project_id)
            finally:
                temp_db.close()
                
            smart_title = title_res.text.strip().strip('"').strip("'")
            if len(smart_title) > 100:
                smart_title = smart_title[:100]
                
            topics = all_topics if all_topics else [{"topic": "General Notes", "content": raw_content[:1500]}]
                
            # 3. Continuous Agentic Memory Merge (WITH PROJECT LOCK)
            await manager.broadcast(json.dumps({"type": "source_progress", "source_id": target_id, "message": "Waiting for Agentic Memory Lock...", "progress": 50}))
            
            async with project_locks[target_project_id]:
                await manager.broadcast(json.dumps({"type": "source_progress", "source_id": target_id, "message": "Weaving into Agentic Memory...", "progress": 60}))
                
                for item in topics[:5]: # Hard cap at 5 to absolutely guarantee no rate limit bursts
                    topic_name = item.get("topic")
                    topic_content = item.get("content")
                    if not topic_name or not topic_content: continue
                    
                    # Prevent Gemini 15 RPM rate limit backoff hanging
                    await asyncio.sleep(2)
                    
                    db_merge = SessionLocal()
                    try:
                        vector = None
                        if pinecone_index is not None:
                            try:
                                embed_res = await call_with_retry(
                                    gemini_client.aio.models.embed_content,
                                    model='gemini-embedding-2',
                                    contents=f"Topic: {topic_name}\n\n{topic_content}"
                                )
                                vector = embed_res.embeddings[0].values
                            except Exception as e:
                                print("Embedding failed:", e)
                                failed_chunks.append(f"Topic Embedding Failed: {topic_name} ({str(e)[:50]})")
                                
                        theme_record = None
                        if vector and pinecone_index is not None:
                            try:
                                pinecone_query = await asyncio.to_thread(pinecone_index.query, vector=vector, top_k=20, namespace="synapseip_themes")
                                if pinecone_query.get('matches') and pinecone_query['matches'][0]['score'] > 0.80:
                                    match_id = pinecone_query['matches'][0]['id']
                                    if match_id.startswith("theme_"):
                                        db_theme_id = int(match_id.split("_")[1])
                                        theme_record = db_merge.query(ProjectTheme).filter(ProjectTheme.id == db_theme_id, ProjectTheme.project_id == target_project_id).first()
                            except Exception as e:
                                print("Pinecone theme query failed:", e)
                                
                        if not theme_record:
                            theme_record = ProjectTheme(
                                project_id=target_project_id,
                                theme_name=topic_name,
                                content=""
                            )
                            db_merge.add(theme_record)
                            db_merge.commit()
                            db_merge.refresh(theme_record)
                            
                        # INSTANT INGESTION: Save fragment directly to the bucket. No LLM merging.
                        fragment = ProjectThemeFragment(
                            theme_id=theme_record.id,
                            content=topic_content
                        )
                        db_merge.add(fragment)
                        db_merge.commit()
                        
                        # We intentionally do NOT upsert to Pinecone here because the fragments are raw.
                        # Pinecone upsert will happen during the high-fidelity consolidation step.
                                
                    finally:
                        db_merge.close()
                
                # Generate Suggested Themes (Still inside lock to ensure atomic updates)
                await manager.broadcast(json.dumps({"type": "source_progress", "source_id": target_id, "message": "Suggesting Next Themes...", "progress": 85}))
                
                db_sugg = SessionLocal()
                try:
                    current_themes = db_sugg.query(ProjectTheme).filter(ProjectTheme.project_id == target_project_id).all()
                    current_theme_names = [t.theme_name for t in current_themes]
                    
                    sugg_prompt = f"""
                    You are an expert app architect.
                    Currently captured themes for this app project: {current_theme_names}
                    
                    What are 3-4 critical architectural themes that are MISSING and still need to be brainstormed?
                    Examples could include: "Authentication & Security", "Monetization", "Database Schema", "UI/UX System", "Third-party APIs".
                    Output ONLY a raw JSON array of strings representing the missing theme names. No markdown blocks, no explanation.
                    """
                    
                    sugg_res = await call_with_retry(
                        gemini_client.aio.models.generate_content,
                        model='gemini-2.5-flash',
                        contents=sugg_prompt
                    )
                    await log_token_usage(db_sugg, "Theme Suggestion", "gemini-2.5-flash", sugg_res, project_id=target_project_id)
                    
                    clean_sugg = sugg_res.text.strip()
                    if clean_sugg.startswith("```json"):
                        clean_sugg = clean_sugg[7:-3].strip()
                    elif clean_sugg.startswith("```"):
                        clean_sugg = clean_sugg[3:-3].strip()
                        
                    project = db_sugg.query(Project).filter(Project.id == target_project_id).first()
                    if project:
                        project.suggested_themes = clean_sugg
                        db_sugg.commit()
                finally:
                    db_sugg.close()
                
                await manager.broadcast("themes_updated")
                
        # Reopen connection for swift instantaneous commit
        db2 = SessionLocal()
        try:
            finished_item = db2.query(GeminiSource).filter(GeminiSource.id == target_id).first()
            if finished_item:
                finished_item.title = smart_title
                finished_item.processed = True
                
                if failed_chunks:
                    finished_item.content += "\n\n--- ⚠️ PARTIAL PROCESSING WARNINGS ---\n" + "\n".join(failed_chunks)
                
                finished_item.processed = True
                
                p = db2.query(Project).filter(Project.id == target_project_id).first()
                if p:
                    p.notes_since_last_check += 1
                    
                db2.commit()
        finally:
            db2.close()

        # Notify UI to update instantly
        await manager.broadcast("new_source")
        await manager.broadcast(json.dumps({"type": "source_progress_complete", "source_id": target_id}))

    except Exception as e:
        print(f"Error in processing card {target_id}:", e)
        db_err = SessionLocal()
        try:
            err_item = db_err.query(GeminiSource).filter(GeminiSource.id == target_id).first()
            if err_item:
                tb = traceback.format_exc()
                err_item.title = f"⚠️ Processing Failed: {str(e)[:50]}"
                err_item.content = err_item.content + f"\n\n--- DIAGNOSTICS ---\n{tb}"
                err_item.processed = True
                db_err.commit()
                await manager.broadcast("new_source")
                await manager.broadcast(json.dumps({"type": "source_progress_complete", "source_id": target_id}))
        finally:
            db_err.close()

async def background_processor():
    while True:
        try:
            db = SessionLocal()
            cards_to_process = []
            project_id_to_check = None
            try:
                # Fetch a batch of up to 5 unprocessed cards that aren't already locked
                unprocessed_cards = db.query(GeminiSource).filter(
                    GeminiSource.processed == False,
                    ~GeminiSource.title.startswith("Processing 🔄")
                ).order_by(GeminiSource.timestamp.asc()).limit(5).all()
                
                if not unprocessed_cards:
                    # Check for consistency check
                    project_to_check = db.query(Project).filter(Project.notes_since_last_check >= 5).first()
                    if project_to_check:
                        project_id_to_check = project_to_check.id
                else:
                    # Detach payloads and mark as temporarily processing to lock them from other theoretical loops
                    for card in unprocessed_cards:
                        cards_to_process.append({
                            'id': card.id,
                            'title': card.title,
                            'content': card.content,
                            'project_id': card.project_id
                        })
                        # Mark title to lock it, but leave processed=False so UI knows it's pending
                        card.title = "Processing 🔄 " + card.title
                    db.commit()
            finally:
                db.close()

            if not cards_to_process:
                if project_id_to_check:
                    try:
                        await perform_consistency_check(project_id_to_check)
                    except Exception as e:
                        print("Automated Consistency Check failed:", e)
                    
                    # Reset counter
                    db_reset = SessionLocal()
                    try:
                        p = db_reset.query(Project).filter(Project.id == project_id_to_check).first()
                        if p:
                            p.notes_since_last_check = 0
                            db_reset.commit()
                    finally:
                        db_reset.close()
                await asyncio.sleep(2)
                continue

            # Process the batch sequentially to avoid lock contention timeouts
            for c in cards_to_process:
                try:
                    # Add a 600 second strict timeout per card to prevent permanent hanging
                    await asyncio.wait_for(process_single_card(c), timeout=600.0)
                except BaseException as res:
                    c_id = c['id']
                    print(f"CRITICAL: Card {c_id} failed violently in background worker: {res}")
                    db_fail = SessionLocal()
                    try:
                        c_item = db_fail.query(GeminiSource).filter(GeminiSource.id == c_id).first()
                        if c_item and c_item.title.startswith("Processing 🔄"):
                            c_item.title = f"⚠️ Processing Failed: Timeout/Crash"
                            c_item.processed = True
                            db_fail.commit()
                            await manager.broadcast("new_source")
                            await manager.broadcast(json.dumps({"type": "source_progress_complete", "source_id": c_id}))
                    except Exception as e_inner:
                        print("Failed to unlock crashed card:", e_inner)
                    finally:
                        db_fail.close()

        except Exception as e:
            print("Outer error in background processor loop:", e)
            
        await asyncio.sleep(2)

def _run_one_time_migration():
    """If MIGRATION_SOURCE_URL is set and the local DB is empty, migrate data from the source (Neon) into the local SQLite."""
    migration_url = os.environ.get("MIGRATION_SOURCE_URL")
    if not migration_url:
        return
    
    # Only migrate if local DB is empty (no users exist yet)
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count > 0:
            print("⏭️  Migration skipped: local database already has data.")
            return
    finally:
        db.close()
    
    print("🚀 One-time migration from MIGRATION_SOURCE_URL detected...")
    try:
        from sqlalchemy import text as sa_text
        pg_engine = create_engine(migration_url, pool_pre_ping=True)
        pg_session = sessionmaker(bind=pg_engine)()
        
        tables = ["users", "projects", "gemini_sources", "generated_reports", 
                   "architect_blueprints", "project_themes", "system_configs", 
                   "chat_history", "token_logs"]
        
        local_session = SessionLocal()
        total = 0
        for table_name in tables:
            try:
                rows = pg_session.execute(sa_text(f"SELECT * FROM {table_name}")).fetchall()
                if not rows:
                    continue
                columns = list(pg_session.execute(sa_text(f"SELECT * FROM {table_name} LIMIT 0")).keys())
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    local_session.execute(
                        sa_text(f"INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join([':' + c for c in columns])})"),
                        row_dict
                    )
                local_session.commit()
                total += len(rows)
                print(f"   ✅ {table_name}: {len(rows)} rows migrated")
            except Exception as e:
                print(f"   ❌ {table_name}: {e}")
                local_session.rollback()
        
        local_session.close()
        pg_session.close()
        print(f"🎉 Migration complete! {total} total rows migrated.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

async def daily_vector_pruner():
    """Background loop to prune vectors once a day."""
    while True:
        # Wait 5 minutes on boot before running to prevent startup blocking
        await asyncio.sleep(300) 
        db = SessionLocal()
        try:
            await prune_vectors_task(db)
        except Exception as e:
            print(f"Daily vector pruner failed: {e}")
        finally:
            db.close()
        # Wait the remaining 24 hours
        await asyncio.sleep(86100)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the database tables on startup
    Base.metadata.create_all(bind=engine)
    
    # Log which database backend is active
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        print(f"🗄️  Using SQLite database at {SQLALCHEMY_DATABASE_URL.replace('sqlite:///', '')}")
    else:
        print(f"🗄️  Using PostgreSQL database")
    
    # Run one-time Neon → SQLite migration if configured
    _run_one_time_migration()
    
    # Auto-requeue any stuck/failed cards on boot
    db = SessionLocal()
    try:
        failed_cards = db.query(GeminiSource).filter(
            GeminiSource.title.like("%Processing Failed%")
        ).all()
        
        # Unlock any cards that got permanently stuck in the "Processing 🔄" state due to a crash
        stuck_cards = db.query(GeminiSource).filter(GeminiSource.title.startswith('Processing 🔄')).all()
        for c in stuck_cards:
            c.title = c.title.replace('Processing 🔄 ', '')
            c.processed = False
        
        if failed_cards:
            print(f"🔄 Auto-requeuing {len(failed_cards)} failed cards on startup...")
            from datetime import datetime, timedelta
            old_time = datetime.utcnow() - timedelta(days=365)
            for card in failed_cards:
                card.processed = False
                card.timestamp = old_time # prioritize them to front of queue
            db.commit()
    except Exception as e:
        print("Failed to auto-requeue cards:", e)
    finally:
        db.close()
    
    asyncio.create_task(background_processor())
    asyncio.create_task(daily_vector_pruner())
    yield
    # Any cleanup could go here

app = FastAPI(title="Gemini Sources API", lifespan=lifespan)

# Enable CORS for extensions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific origins (e.g., your extension's ID)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and set up templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ---------------------------------------------------------
# WebSocket Manager
# ---------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

class CircuitBreakerException(Exception):
    pass

async def check_circuit_breaker(user_id: int, db: Session, limit: float = 2.00):
    from datetime import datetime
    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    total_cost = db.query(func.sum(TokenLog.cost)).filter(
        TokenLog.user_id == user_id,
        TokenLog.timestamp >= start_of_day
    ).scalar() or 0.0
    
    if total_cost >= limit:
        raise CircuitBreakerException(f"Daily API Budget Exceeded")

async def log_token_usage(db: Session, action: str, model: str, res, project_id: int = None, user_id: int = 1):
    if hasattr(res, 'usage_metadata') and res.usage_metadata:
        in_toks = getattr(res.usage_metadata, 'prompt_token_count', 0) or 0
        out_toks = getattr(res.usage_metadata, 'candidates_token_count', 0) or 0
        
        cost = 0.0
        if "flash" in model.lower():
            if in_toks <= 128000:
                cost = (in_toks / 1000000.0) * 0.075 + (out_toks / 1000000.0) * 0.30
            else:
                cost = (in_toks / 1000000.0) * 0.15 + (out_toks / 1000000.0) * 0.60
        elif "pro" in model.lower():
            if in_toks <= 128000:
                cost = (in_toks / 1000000.0) * 1.25 + (out_toks / 1000000.0) * 5.00
            else:
                cost = (in_toks / 1000000.0) * 2.50 + (out_toks / 1000000.0) * 10.00
            
        final_user_id = user_id
        if project_id:
            proj = db.query(Project).filter(Project.id == project_id).first()
            if proj and proj.user_id:
                final_user_id = proj.user_id
            
        record = TokenLog(
            user_id=final_user_id,
            project_id=project_id,
            action=action,
            model_name=model,
            prompt_tokens=in_toks,
            completion_tokens=out_toks,
            cost=cost
        )
        db.add(record)
        db.commit()
        await manager.broadcast("token_update")
# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# ---------------------------------------------------------
# Auth Endpoints
# ---------------------------------------------------------
@app.post("/api/auth/register", response_model=Token)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user_in.password)
    new_user = User(username=user_in.username, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

from sqlalchemy import func

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    clean_username = form_data.username.strip().lower()
    user = db.query(User).filter(func.lower(User.username) == clean_username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/change-password")
async def change_password(req: PasswordChangeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    hashed_password = get_password_hash(req.new_password)
    db.query(User).filter(User.id == current_user.id).update({"password_hash": hashed_password})
    db.commit()
    return {"status": "success"}

@app.get("/api/me")
async def get_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "is_admin": current_user.is_admin}

# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """Serve the NotebookLM-style frontend interaction page."""
    return templates.TemplateResponse(request=request, name="index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def get_current_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or not owned by user")
    return project

@app.get("/api/projects")
def get_projects(response: Response, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.timestamp.desc()).all()

@app.post("/api/projects", response_model=ProjectResponse)
def create_project(req: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = Project(user_id=current_user.id, name=req.name)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def truncate_context_for_tokens(context: str, max_chars: int = 2500000) -> str:
    """Truncates context to avoid exceeding token limits while preserving the beginning and end of the payload."""
    if len(context) <= max_chars:
        return context
    
    half_limit = max_chars // 2
    truncation_warning = "\n\n...[TRUNCATED TO PREVENT TOKEN LIMIT ERROR]...\n\n"
    return context[:half_limit] + truncation_warning + context[-half_limit:]

@app.put("/api/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, req: ProjectUpdate, db: Session = Depends(get_db), project: Project = Depends(get_current_project)):
    project.name = req.name
    db.commit()
    db.refresh(project)
    return project

async def perform_consistency_check(project_id: int):
    db = SessionLocal()
    try:
        themes = db.query(ProjectTheme).filter(ProjectTheme.project_id == project_id).all()
        if not themes:
            return {"status": "error", "message": "No themes found for consistency check"}
        
        compiled_themes = ""
        for t in themes:
            compiled_themes += f"\n\n--- THEME: {t.theme_name} ---\n{t.content}"

        prompt = f"""
        You are an expert systems architect. The following are distinct architectural themes generated asynchronously for a project.
        Because they were generated separately, there may be overlaps, redundant information, or direct technical contradictions across them.
        
        Your job is to perform a Global Consistency Check.
        1. Resolve any contradictions (e.g., if one theme says PostgreSQL and another says MongoDB, synthesize a unified approach or flag the discrepancy clearly if unresolvable).
        2. Deduplicate overlapping sections cleanly.
        3. Ensure the macro-architecture is cohesive.
        
        CURRENT THEMES:
        {compiled_themes}
        
        CRITICAL INSTRUCTIONS: 
        1. Return ONLY a valid JSON object. 
        2. The keys MUST be the EXACT original theme names. 
        3. The values MUST be the newly cleaned, consistent markdown content for that theme. 
        4. ALL backslashes within the markdown content MUST be properly escaped (e.g., use \\\\ instead of \\) to prevent JSON parsing errors.
        """

        await manager.broadcast(json.dumps({"type": "progress", "progress": 20, "message": "Analyzing Architecture for consistency..."}))

        res = await gemini_client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json'
            }
        )
        
        clean_res = res.text.strip()
        updated_data = json.loads(clean_res)
        
        for t in themes:
            if t.theme_name in updated_data:
                t.content = updated_data[t.theme_name]
                
        db.query(Project).filter(Project.id == project_id).update({"is_consistent": True})        
        db.commit()
        await manager.broadcast(json.dumps({"type": "progress", "progress": 100, "message": "Consistency check complete!"}))
        await manager.broadcast("themes_updated")
        return {"status": "success"}
    except Exception as e:
        await manager.broadcast(json.dumps({"type": "progress", "progress": 100, "message": f"Consistency check failed: {e}"}))
        print("Consistency Check Failed:", e)
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@app.post("/api/projects/{project_id}/consistency-check")
async def run_consistency_check(background_tasks: BackgroundTasks, project: Project = Depends(get_current_project), db: Session = Depends(get_db)):
    themes = db.query(ProjectTheme).filter(ProjectTheme.project_id == project.id).all()
    if not themes:
        raise HTTPException(status_code=400, detail="No themes found for consistency check")
    
    background_tasks.add_task(perform_consistency_check, project.id)
    return {"status": "queued"}

@app.get("/api/projects/{project_id}/sources")
def get_project_sources(response: Response, project: Project = Depends(get_current_project), db: Session = Depends(get_db)):
    """Return all ingested sources for a specific project."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    sources = db.query(GeminiSource).filter(GeminiSource.project_id == project.id).order_by(GeminiSource.timestamp.asc()).all()
    return sources

@app.get("/api/projects/{project_id}/documents")
def get_project_documents(response: Response, project: Project = Depends(get_current_project), db: Session = Depends(get_db)):
    """Returns lists of intelligence reports and architecture blueprints for this project."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    reports = db.query(GeneratedReport).filter(GeneratedReport.project_id == project.id).order_by(GeneratedReport.timestamp.desc()).all()
    blueprints = db.query(ArchitectBlueprint).filter(ArchitectBlueprint.project_id == project.id).order_by(ArchitectBlueprint.timestamp.desc()).all()
    
    return {
        "intelligence": [{"id": r.id, "timestamp": r.timestamp, "data": json.loads(r.report_data)} for r in reports],
        "blueprints": [{"id": b.id, "timestamp": b.timestamp, "data": b.blueprint_data} for b in blueprints],
        "current_vibe_step": project.current_vibe_step if project else 0,
        "followup_history": json.loads(project.followup_history) if project and project.followup_history else []
    }

@app.post("/api/projects/{project_id}/vibe-step")
def update_vibe_step(update: VibeStepUpdate, project: Project = Depends(get_current_project), db: Session = Depends(get_db)):
    project.current_vibe_step = update.step
    db.commit()
    return {"status": "success", "step": update.step}

@app.get("/api/projects/{project_id}/themes_dashboard")
def get_themes_dashboard(response: Response, project: Project = Depends(get_current_project), db: Session = Depends(get_db)):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    themes = db.query(ProjectTheme).filter(ProjectTheme.project_id == project.id).all()
    
    active_themes = [t.theme_name for t in themes]
    suggested_themes = []
    
    if project and project.suggested_themes:
        try:
            suggested_themes = json.loads(project.suggested_themes)
        except:
            pass
            
    return {
        "active_themes": active_themes,
        "suggested_themes": suggested_themes,
        "is_consistent": project.is_consistent if project else False,
        "onboarding_config": project.onboarding_config if project else None
    }

async def prune_vectors_task(db: Session):
    """Background task to synchronize Pinecone with SQLite."""
    if pinecone_index is None:
        return
        
    try:
        print("🧹 Starting Vector Drift Pruning...")
        all_themes = db.query(ProjectTheme).all()
        
        # Phase 2: Heal missing vectors
        theme_ids = [f"theme_{t.id}" for t in all_themes]
        existing_pinecone_ids = set()
        
        for i in range(0, len(theme_ids), 100):
            batch = theme_ids[i:i+100]
            try:
                fetch_res = await asyncio.to_thread(pinecone_index.fetch, ids=batch, namespace="synapseip_themes")
                existing_pinecone_ids.update(fetch_res.get('vectors', {}).keys())
            except Exception as e:
                print(f"Warning: Pinecone fetch failed: {e}")
                
        missing_in_pinecone = []
        for theme in all_themes:
            if f"theme_{theme.id}" not in existing_pinecone_ids:
                missing_in_pinecone.append(theme)
                
        if missing_in_pinecone and gemini_client:
            print(f"🩹 Healing {len(missing_in_pinecone)} missing vectors into Pinecone...")
            for theme in missing_in_pinecone:
                try:
                    res = await gemini_client.aio.models.embed_content(
                        model='gemini-embedding-2',
                        contents=f"Topic: {theme.theme_name}\n\n{theme.content}"
                    )
                    vector = res.embeddings[0].values
                    await asyncio.to_thread(
                        pinecone_index.upsert,
                        vectors=[(f"theme_{theme.id}", vector, {"title": theme.theme_name, "content": theme.content})],
                        namespace="synapseip_themes"
                    )
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"Failed to heal vector for theme {theme.id}: {e}")
                    
        # Phase 1: Try to delete orphans using list()
        orphans_to_delete = []
        try:
            for ids in pinecone_index.list(namespace="synapseip_themes"):
                for pid in ids:
                    if pid.startswith("theme_"):
                        try:
                            db_id = int(pid.split("_")[1])
                            if not any(t.id == db_id for t in all_themes):
                                orphans_to_delete.append(pid)
                        except:
                            pass
            if orphans_to_delete:
                print(f"🗑️ Deleting {len(orphans_to_delete)} orphan vectors from Pinecone...")
                await asyncio.to_thread(pinecone_index.delete, ids=orphans_to_delete, namespace="synapseip_themes")
        except Exception as e:
            pass # pod-based index list() not supported
            
        print("✅ Vector Drift Pruning Complete.")
    except Exception as e:
        print(f"❌ Vector pruning failed: {e}")

@app.post("/api/admin/prune-vectors")
async def trigger_prune_vectors(background_tasks: BackgroundTasks):
    bg_db = SessionLocal()
    async def task_wrapper():
        try:
            await prune_vectors_task(bg_db)
        finally:
            bg_db.close()
    background_tasks.add_task(task_wrapper)
    return {"message": "Vector pruning task started in the background."}

@app.get("/api/admin/diagnostics")
def get_diagnostics():
    db = SessionLocal()
    try:
        failed = db.query(GeminiSource).filter(GeminiSource.title.like("⚠️ Processing Failed%")).all()
        processing = db.query(GeminiSource).filter(GeminiSource.title.like("Processing 🔄%")).all()
        pending = db.query(GeminiSource).filter(GeminiSource.processed == False).all()
        
        qp_cards = db.query(GeminiSource).filter(GeminiSource.project_id == 4).count()
        qp_themes = db.query(ProjectTheme).filter(ProjectTheme.project_id == 4).count()
        total_themes = db.query(ProjectTheme).count()
        
        return {
            "failed": [{"id": f.id, "title": f.title} for f in failed],
            "processing": [{"id": p.id, "title": p.title} for p in processing],
            "pending_count": len(pending),
            "qingpath_total_cards": qp_cards,
            "qingpath_total_themes": qp_themes,
            "total_themes_all_projects": total_themes
        }
    finally:
        db.close()

@app.post("/api/admin/pull-legacy-cards")
def pull_legacy_cards(source_url: str = None):
    import os
    from sqlalchemy import create_engine, text
    
    neon_url = source_url or os.environ.get("DATABASE_URL")
    if not neon_url or "postgres" not in neon_url:
        return {"error": "Neon DATABASE_URL not configured or provided"}
        
    try:
        pg_engine = create_engine(neon_url)
        with pg_engine.connect() as pg_conn:
            # Get all sources from Neon
            rows = pg_conn.execute(text("SELECT * FROM gemini_sources")).fetchall()
            columns = pg_conn.execute(text("SELECT * FROM gemini_sources LIMIT 0")).keys()
            col_names = list(columns)
            
            # Map Neon Project IDs to Names
            pg_projects = pg_conn.execute(text("SELECT id, name FROM projects")).fetchall()
            neon_id_to_name = {r.id: r.name for r in pg_projects}
            
        db = SessionLocal()
        added_count = 0
        try:
            # Map SQLite Project Names to IDs
            sqlite_projects = {p.name.lower(): p.id for p in db.query(Project).all()}
            
            for row in rows:
                row_dict = dict(zip(col_names, row))
                # Check if it already exists by content to avoid ID collisions
                existing = db.query(GeminiSource).filter(GeminiSource.content == row_dict.get('content')).first()
                if not existing:
                    neon_proj_name = neon_id_to_name.get(row_dict.get('project_id'))
                    sqlite_proj_id = sqlite_projects.get(neon_proj_name.lower()) if neon_proj_name else row_dict.get('project_id')
                    
                    # Create new SQLite record (omit id so it autoincrements)
                    new_source = GeminiSource(
                        user_id=row_dict.get('user_id'),
                        project_id=sqlite_proj_id,
                        title=row_dict.get('title'),
                        content=row_dict.get('content'),
                        timestamp=row_dict.get('timestamp'),
                        source_url=row_dict.get('source_url'),
                        processed=False, # Force false so the worker picks them up
                        short_memory=row_dict.get('short_memory')
                    )
                    db.add(new_source)
                    added_count += 1
            db.commit()
            return {"status": "success", "cards_imported": added_count}
        finally:
            db.close()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/admin/sync-pinecone")
async def sync_pinecone():
    """Force sync all SQLite themes to Pinecone."""
    if pinecone_index is None or gemini_client is None:
        return {"error": "Pinecone or Gemini not initialized"}
        
    db = SessionLocal()
    try:
        themes = db.query(ProjectTheme).all()
        upserted_count = 0
        failed_themes = []
        
        for theme in themes:
            try:
                # Generate fresh embedding for the theme
                embed_res = await gemini_client.aio.models.embed_content(
                    model='gemini-embedding-2',
                    contents=f"Topic: {theme.theme_name}\n\n{theme.content}"[:10000] # Safe truncate
                )
                vector = embed_res.embeddings[0].values
                
                # Upsert to Pinecone
                import asyncio
                await asyncio.to_thread(
                    pinecone_index.upsert,
                    vectors=[(f"theme_{theme.id}", vector, {"title": theme.theme_name, "content": theme.content[:10000]})],
                    namespace="synapseip_themes"
                )
                upserted_count += 1
                await asyncio.sleep(1) # Prevent rate limits
            except Exception as e:
                failed_themes.append({"id": theme.id, "name": theme.theme_name, "length": len(theme.content), "error": str(e)})
                
        return {"status": "success", "themes_synced": upserted_count, "total_db_themes": len(themes), "failed_themes": failed_themes}
    finally:
        db.close()

@app.post("/api/admin/reformat-intel")
def reformat_intel():
    """Quick fix to reformat the most recent Intel Report without regenerating."""
    import re
    import json
    import traceback
    
    try:
        db = SessionLocal()
        try:
            report = db.query(GeneratedReport).order_by(GeneratedReport.id.desc()).first()
            if not report:
                return {"error": "No reports found"}
                
            data = json.loads(report.report_data)
            
            # Helper to fix spacing
            def fix_spacing(text):
                if not text: return text
                t = str(text)
                t = t.replace("###", "\n\n###")
                t = t.replace("**Strengths:**", "\n\n**Strengths:**\n")
                t = t.replace("**Weaknesses:**", "\n\n**Weaknesses:**\n")
                t = t.replace("**Opportunities:**", "\n\n**Opportunities:**\n")
                t = t.replace("**Threats:**", "\n\n**Threats:**\n")
                t = t.replace("**Benefits:**", "\n\n**Benefits:**\n")
                t = t.replace("**Costs:**", "\n\n**Costs:**\n")
                t = t.replace("Benefits:", "\n\n**Benefits:**\n")
                t = t.replace("Costs:", "\n\n**Costs:**\n")
                t = t.replace("* ", "\n* ")
                # clean up multiple newlines
                t = re.sub(r'\n{3,}', '\n\n', t)
                return t.strip()
                
            if "market_analysis" in data:
                data["market_analysis"] = fix_spacing(data["market_analysis"])
            if "swot" in data:
                data["swot"] = fix_spacing(data["swot"])
            if "cost_benefit" in data:
                data["cost_benefit"] = fix_spacing(data["cost_benefit"])
                
            report.report_data = json.dumps(data)
            db.commit()
            return {"status": "success", "fixed_id": report.id}
        finally:
            db.close()
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

@app.get("/api/projects/{project_id}/themes")
def get_project_themes(response: Response, project: Project = Depends(get_current_project), db: Session = Depends(get_db)):
    """Return all active themes for this project."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    themes = db.query(ProjectTheme).filter(ProjectTheme.project_id == project.id).all()
    return [{"id": t.id, "theme_name": t.theme_name, "content": t.content} for t in themes]

@app.put("/api/projects/{project_id}/themes/{theme_id}")
async def update_project_theme(theme_id: int, update: ThemeUpdateRequest, project: Project = Depends(get_current_project), db: Session = Depends(get_db)):
    """Update a theme manually and re-embed to Pinecone."""
    theme = db.query(ProjectTheme).filter(ProjectTheme.id == theme_id, ProjectTheme.project_id == project.id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
        
    theme.content = update.content
    db.commit()
    
    # Re-embed to Pinecone
    if pinecone_index is not None and gemini_client is not None:
        try:
            embed_res = await gemini_client.aio.models.embed_content(
                model='gemini-embedding-2',
                contents=f"Topic: {theme.theme_name}\n\n{theme.content}"
            )
            vector = embed_res.embeddings[0].values
            await asyncio.to_thread(
                pinecone_index.upsert,
                vectors=[(f"theme_{theme.id}", vector, {"title": theme.theme_name, "content": theme.content})],
                namespace="synapseip_themes"
            )
        except Exception as e:
            print("Failed to re-embed theme manually:", e)
            
    await manager.broadcast("themes_updated")
    return {"status": "success"}

@app.post("/api/projects/{project_id}/clear-onboarding")
def clear_onboarding(project: Project = Depends(get_current_project), db: Session = Depends(get_db)):
    project.onboarding_config = None
    db.commit()
    return {"status": "success"}

@app.get("/api/sources")
def get_sources(response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Fallback for old requests
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    active_project = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.timestamp.desc()).first()
    if not active_project:
        return []
    sources = db.query(GeminiSource).filter(GeminiSource.project_id == active_project.id).order_by(GeminiSource.timestamp.asc()).all()
    return sources

@app.delete("/api/sources/{source_id}")
async def delete_source(source_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_source = db.query(GeminiSource).join(Project).filter(GeminiSource.id == source_id, Project.user_id == current_user.id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found or not owned by user")
    db.delete(db_source)
    db.commit()
    await manager.broadcast(json.dumps({"type": "sources_deleted"}))
    return {"status": "success"}

@app.post("/api/sources/bulk-delete")
async def bulk_delete_sources(req: BulkDeleteRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not req.source_ids:
        return {"status": "success", "deleted_count": 0}
        
    db_sources = db.query(GeminiSource).join(Project).filter(GeminiSource.id.in_(req.source_ids), Project.user_id == current_user.id).all()
    source_ids_to_delete = [s.id for s in db_sources]
    
    if source_ids_to_delete:
        db.query(GeminiSource).filter(GeminiSource.id.in_(source_ids_to_delete)).delete(synchronize_session=False)
        db.commit()
        await manager.broadcast(json.dumps({"type": "sources_deleted"}))
        
    return {"status": "success", "deleted_count": len(source_ids_to_delete)}

@app.post("/api/sources/{source_id}/reprocess")
def reprocess_source(source_id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        source = db.query(GeminiSource).filter(GeminiSource.id == source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        # Ensure only project owners or admins can reprocess
        project = db.query(Project).filter(Project.id == source.project_id).first()
        if project.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        source.processed = False
        db.commit()
        return {"status": "success", "message": "Source queued for reprocessing"}
    finally:
        db.close()

@app.post("/api/projects/{project_id}/retry-missed")
def retry_missed_sources(project_id: int, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        # Re-queue sources that are stuck (either never processed, or look like they stalled)
        stalled_sources = db.query(GeminiSource).filter(
            GeminiSource.project_id == project_id,
            (GeminiSource.processed == False) | (GeminiSource.title.like("AI Source Node%"))
        ).all()
        
        for s in stalled_sources:
            s.processed = False
            background_tasks.add_task(generate_short_memory, str(s.id))
            
        db.commit()
        return {"status": "success", "queued": len(stalled_sources)}
    finally:
        db.close()

@app.post("/api/admin/reprocess-all")
def reprocess_all_sources(project_id: Optional[int] = None, current_user: User = Depends(get_current_user)):
    """Admin endpoint to force all sources to be reprocessed through the new theme pipeline."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db = SessionLocal()
    try:
        query = db.query(GeminiSource)
        if project_id:
            query = query.filter(GeminiSource.project_id == project_id)
            
        sources = query.all()
        for s in sources:
            s.processed = False
            
        db.commit()
        
        return {"status": "success", "message": f"Successfully marked {len(sources)} sources for reprocessing. The background worker will pick them up shortly."}
    finally:
        db.close()

@app.post("/api/admin/diagnose-card/{card_id}")
async def diagnose_card(card_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Triggers the Diagnostics Agent to analyze a permanently failed card and suggest a fix."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    card = db.query(GeminiSource).filter(GeminiSource.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
        
    if "⚠️ Processing Failed" not in card.title:
        return {"status": "skipped", "message": "Card is not currently in a failed state."}
        
    diag_prompt = f"""
    You are an expert AI Data Diagnostics Agent.
    The following input card failed to process in our backend pipeline.
    
    CARD CONTENT & TRACEBACK:
    {card.content[-5000:]}
    
    Please analyze the failure. Provide a concise, human-readable post-mortem:
    1. **Root Cause**: Why did it fail? (e.g. "Rate limit hit", "Text is purely code and couldn't be parsed", "Database timeout").
    2. **Recoverability**: What parts of the original raw note can be salvaged?
    3. **Recommended Action**: What should the admin do? (e.g. "Just click Re-queue, it was a temporary timeout", "Delete the card, it is garbage data").
    
    Keep it professional, structured, and brief. Use markdown.
    """
    
    try:
        diag_res = await gemini_client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=diag_prompt
        )
        
        # Append the diagnostic report to the card content for the user to see
        card.content += f"\n\n=========================\n🤖 DIAGNOSTICS AGENT REPORT\n=========================\n{diag_res.text.strip()}"
        db.commit()
        
        return {"status": "success", "message": "Diagnostic report generated successfully.", "report": diag_res.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnostics Agent failed: {e}")

# ---------------------------------------------------------
# Extension API Endpoints (lightweight, for Chrome Extension overlay)
# ---------------------------------------------------------
@app.get("/api/ext/projects")
def ext_get_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lightweight project list for the Chrome Extension overlay."""
    projects = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.timestamp.desc()).all()
    return [{"id": p.id, "name": p.name} for p in projects]

@app.post("/api/ext/projects")
def ext_create_project(req: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new project from the Chrome Extension overlay."""
    p = Project(user_id=current_user.id, name=req.name)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": p.id, "name": p.name}

@app.post("/ingest", response_model=SourceResponse)
async def ingest_source(source: SourceCreate, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Accepts JSON from Chrome Extension and saves it to the designated project (or most recent as fallback)."""
    
    active_project = None
    
    # If the extension explicitly specified a project, validate ownership and use it
    if source.project_id:
        active_project = db.query(Project).filter(
            Project.id == source.project_id,
            Project.user_id == current_user.id
        ).first()
    
    # Fallback: use the most recently created project
    if not active_project:
        active_project = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.timestamp.desc()).first()
    
    if not active_project:
        active_project = Project(user_id=current_user.id, name="Default Project")
        db.add(active_project)
        db.commit()
        db.refresh(active_project)

    # Duplicate prevention: Check if exact content already exists in this project
    existing_source = db.query(GeminiSource).filter(
        GeminiSource.project_id == active_project.id,
        GeminiSource.content == source.content
    ).first()

    if existing_source:
        # Return success with the existing source to satisfy the extension, but don't insert a duplicate or trigger background tasks
        return SourceResponse(
            id=existing_source.id,
            title=existing_source.title,
            content=existing_source.content,
            source_url=existing_source.source_url,
            timestamp=existing_source.timestamp,
            processed=existing_source.processed
        )

    db_source = GeminiSource(
        user_id=current_user.id,
        project_id=active_project.id,
        title=source.title, # Respecting chronological numbering extracted by Chrome sub-agent
        content=source.content,
        source_url=source.source_url,
        timestamp=datetime.utcnow(),
        processed=False
    )
    db.add(db_source)
    active_project.is_consistent = False
    db.commit()
    db.refresh(db_source)
    
    # Background generation for short-term memory optimizations
    background_tasks.add_task(generate_short_memory, str(db_source.id))
    
    total = db.query(GeminiSource).filter(GeminiSource.project_id == active_project.id).count()
    
    # Notify connected real-time UI components
    await manager.broadcast("new_source")
    
    return SourceResponse(
        id=db_source.id,
        title=db_source.title,
        content=db_source.content,
        timestamp=db_source.timestamp,
        source_url=db_source.source_url,
        total_count=total,
        processed=db_source.processed
    )

@app.post("/api/ext/sources/vision")
async def ingest_vision_source(
    req: VisionSourceCreate, 
    background_tasks: BackgroundTasks, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Extension endpoint to capture UI designs, run vision extraction, and save as a standard text source."""
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini client not initialized")
        
    try:
        # Decode base64 image (stripping data URL scheme if present)
        b64_str = req.image_base64
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        image_bytes = base64.b64decode(b64_str)
        
        prompt = "You are an expert UI/UX Engineer. Analyze this UI screenshot. Extract the layout constraints, styling rules, typography hints, and exact hex color palettes. Output a structured markdown design token summary."
        
        response = await gemini_client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                prompt
            ]
        )
        
        extracted_content = response.text.strip()
        
        db_source = GeminiSource(
            user_id=current_user.id,
            project_id=req.project_id,
            title=f"Vision Extraction: {req.source_url[:30]}...",
            content=extracted_content,
            source_url=req.source_url,
            timestamp=datetime.utcnow(),
            processed=False
        )
        db.add(db_source)
        project = db.query(Project).filter(Project.id == req.project_id).first()
        if project:
            project.is_consistent = False
        db.commit()
        db.refresh(db_source)
        
        background_tasks.add_task(generate_short_memory, str(db_source.id))
        await manager.broadcast("new_source")
        
        return {"status": "success", "source_id": db_source.id}
    except Exception as e:
        print(f"Vision ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def semantic_search(q: str, current_user: User = Depends(get_current_user)):
    """Hits the vector database, dynamically maps query text to math via Gemini, and finds connections."""
    if pinecone_index is None or gemini_client is None:
        raise HTTPException(status_code=500, detail="Pinecone DB is natively disabled.")
    
    try:
        res = gemini_client.models.embed_content(
            model='gemini-embedding-2',
            contents=q,
        )
        vector = res.embeddings[0].values
        
        results = pinecone_index.query(
            vector=vector,
            top_k=20,
            namespace="synapseip_notes",
            include_metadata=True
        )
        return {"status": "success", "results": results.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/followup")
async def followup_chat(req: FollowupRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini SDK improperly configured.")
        
    project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or not owned by user")
    
    # Identify the related Intelligence Report
    report = db.query(GeneratedReport).filter(GeneratedReport.project_id == project.id).order_by(GeneratedReport.timestamp.desc()).first()
    
    if not report:
        report_context = "No Intelligence Report generated yet."
    else:
        report_context = json.loads(report.report_data).get("swot", "No SWOT found.")
        
    history_str = "\n".join([f"{msg.role.upper()}: {msg.content}" for msg in req.history])
    if not req.history:
        history_str = "(Conversation just started. The user is waiting.)"
        
    prompt = f"""
    You are the SynapseIP Follow-Up Architect. The user has just finished reading their Intelligence Report for this project.
    Your mission is to act as both a Technical Advisor and a Business Strategist.
    
    Intelligence Context (SWOT / Weaknesses / Blindspots):
    {report_context}
    
    Goals:
    1. Discuss the weaknesses and blindspots of their app idea.
    2. Suggest third-party APIs they might need to make this app function properly (e.g. Stripe, OpenAI, Google Maps).
    3. If they need an API, provide them with instructions or links on how to register for those API keys. 
    4. Remind them NOT to share their actual API keys with you in this chat, but assure them the Architect Blueprint will leave placeholders for their IDE.
    
    Current Conversation History:
    {history_str}
    
    Respond exclusively as the agent speaking directly to the user in the conversational flow. Use Markdown.
    """
    
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # Save to database
        if project:
            new_history = [{"role": msg.role, "content": msg.content} for msg in req.history]
            new_history.append({"role": "model", "content": response.text})
            project.followup_history = json.dumps(new_history)
            db.commit()
            
        return {"message": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/onboarding")
async def onboarding_chat(req: OnboardingRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini SDK improperly configured. Check API key.")
        
    project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or not owned by user")
        
    project_name = project.name if project else "SynapseIP Target App"

    sources = db.query(GeminiSource).filter(GeminiSource.project_id == project.id).order_by(GeminiSource.timestamp.asc()).all()
    
    if len(req.history) == 0:
        memories = []
        for s in sources:
            mem = s.short_memory if s.short_memory else "(Memory processing...)"
            memories.append(f"Source Memory: {s.title}\n{mem}")
        context_text = "\n\n".join(memories) if memories else "No sources provided yet."
    else:
        last_query = req.history[-1].content
        relevant_ids = []
        if pinecone_index is not None and gemini_client is not None:
            try:
                res = gemini_client.models.embed_content(
                    model='gemini-embedding-2',
                    contents=last_query,
                )
                vector = res.embeddings[0].values
                pinecone_query = pinecone_index.query(vector=vector, top_k=20, namespace="synapseip_themes")
                relevant_ids = [int(match['id'].split("_")[1]) for match in pinecone_query.get('matches', []) if match['id'].startswith("theme_")]
            except Exception as e:
                print("Pinecone warning on onboarding:", e)
                
        memories = []
        if project and relevant_ids:
            # Inject relevant synthesized themes
            db_themes = db.query(ProjectTheme).filter(ProjectTheme.id.in_(relevant_ids), ProjectTheme.project_id == project.id).all()
            for t in db_themes:
                memories.append(f"RELEVANT ARCHITECTURE THEME: {t.theme_name}\n{t.content}")
        
        # Also include short memories from raw cards for broad context
        for s in sources:
            mem = s.short_memory if s.short_memory else "(Memory processing...)"
            memories.append(f"Raw Source Context: {s.title}\n{mem}")
            
        context_text = "\n\n".join(memories) if memories else "No sources provided yet."
    
    context_text = truncate_context_for_tokens(context_text)
    
    history_str = "\n".join([f"{msg.role.upper()}: {msg.content}" for msg in req.history])
    if not req.history:
        history_str = "(Conversation just started. The user is waiting.)"
    
    prompt = f"""
    You are the SynapseIP Onboarding Agent. Your mission is to chat with the user to slowly extract 10 required parameters: Designer Name, App Name, Core Purpose, Target Audience (with location/region), App Type ('Personal' or 'Commercial'), Budget/Subscription Tier (e.g. Free Tier prototyping vs Paid Enterprise), AI Integration/Function, Security & Authentication Strategy, Build Environment (Greenfield vs Brownfield), and Standout Features.
    
    CRITICAL OVERRIDE: The user has ALREADY officially designated the App Name as "{project_name}". 
    You MUST NOT ask the user what the App Name is, and you MUST EXACTLY output "{project_name}" for the App Name parameter.
    
    IMPORTANT PACING RULES: 
    - This is a natural conversation. DO NOT interrogate the user or ask a massive block of questions at once.
    - Ask a MAXIMUM of 1 to 2 questions per message. Take your time.
    - Gather information passively. If they provide details without being explicitly asked, intelligently map those details to the required parameters.
    
    FLOW:
    - If the conversation just started, enthusiastically welcome them, quickly evaluate the summary of their brainstorm sources (below) in a sentence or two, and elegantly ask who is designing it and what its core purpose is. (Just those two to start!)
    - As the conversation continues, gently probe for the remaining missing parameters (Target Audience, Personal/Commercial, Budget, AI functions, Security/Auth, Greenfield/Brownfield, Standout Features). Remember: ONLY 1 OR 2 QUESTIONS PER MESSAGE.
    - Keep your responses relatively concise.
    
    Once ALL 10 required parameters are clearly established, set is_complete=True and output a concluding launch message.
    
    Database Brainstorm Context:
    {context_text}
    
    Conversation History:
    {history_str}
    
    Respond based on the exact JSON schema requested.
    AGENT:
    """
    
    try:
        res = await gemini_client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': OnboardingResponseSchema,
            }
        )
        await log_token_usage(db, "Onboarding Chat", "gemini-2.5-flash", res, project_id=req.project_id)
        parsed_res = json.loads(res.text)
        if parsed_res.get("is_complete") and project:
            project.onboarding_config = res.text
            db.commit()
        return parsed_res
    except Exception as e:
        print("Logic router architecture unhandled:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/selectors")
def get_selectors_config(db: Session = Depends(get_db)):
    configs = db.query(SystemConfig).filter(SystemConfig.key.startswith("selector_")).all()
    if not configs:
        defaults = {
            "selector_chatgpt.com": "article",
            "selector_claude.ai": ".font-claude-message",
            "selector_gemini.google.com": "message-content, .message-content, [data-message-author=\"model\"], div[class*=\"model-response\"]",
            "selector_www.perplexity.ai": ".prose",
            "selector_chat.deepseek.com": ".ds-markdown",
            "selector_kimi.moonshot.cn": ".markdown-body, .markdown",
            "selector_www.doubao.com": ".markdown-body, .markdown, [data-testid='chat-message-text'], div[class*='message-content'], div[class*='conversation-msg']"
        }
        for k, v in defaults.items():
            db.add(SystemConfig(key=k, value=v))
        db.commit()
        return {k.replace("selector_", ""): v for k, v in defaults.items()}
        
    return {c.key.replace("selector_", ""): c.value for c in configs}

@app.post("/api/report-change")
async def report_change(req: ReportChangeRequest, db: Session = Depends(get_db)):
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini backend unconfigured.")
    
    prompt = f"""
    You are the SynapseIP Sentinel. The target website ({req.hostname}) changed its DOM scheme for the AI chat responses. 
    I need you to identify the NEW CSS QuerySelector that encapsulates an individual AI text response. 
    Here is the raw DOM HTML of the new website format:
    
    {req.html_payload}
    
    Examine the HTML. Output ONLY the raw CSS Selector string that selects the chat bubbles where the AI response lives, nothing else. Do not use markdown. Do not explain. Just the exact query selector string.
    """
    
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        new_selector = response.text.strip().strip('`')
        
        target_key = f"selector_{req.hostname}"
        config_entry = db.query(SystemConfig).filter(SystemConfig.key == target_key).first()
        if not config_entry:
            config_entry = SystemConfig(key=target_key, value=new_selector)
            db.add(config_entry)
        else:
            config_entry.value = new_selector
        db.commit()
        
        return {"status": "success", "new_selector": new_selector}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_sources(req: AnalyzeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini SDK improperly configured. Check API key.")
        
    project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or not owned by user")
        
    sources = db.query(GeminiSource).filter(GeminiSource.project_id == project.id).order_by(GeminiSource.timestamp.asc()).all()
    themes = db.query(ProjectTheme).filter(ProjectTheme.project_id == project.id).all()
    
    if not sources and not themes:
        raise HTTPException(status_code=400, detail="No sources or themes found to analyze.")
        
    memories = []
    
    # Primary Context: High-Fidelity Themes
    if themes:
        memories.append("### High-Fidelity Synthesized Architecture Themes ###")
        for t in themes:
            memories.append(f"Theme: {t.theme_name}\nContent:\n{t.content}")
    
    # Fallback Context: Raw Sources (if no themes exist)
    if not themes and sources:
        memories.append("### Raw Uploaded Source Snippets ###")
        for s in sources:
            if s.short_memory:
                memories.append(f"Source: {s.title}\nSummary: {s.short_memory}")
            else:
                memories.append(f"Source: {s.title}\nContent snippet: {s.content[:500]}...")
                
    context_text = "\n\n".join(memories)
    context_text = truncate_context_for_tokens(context_text)
    
    if req.app_type and req.app_type.lower() == "personal":
        rubric_text = """
    1. Calculate a Utility Health Score (viability_score) between 0-100 based strictly on these 4 pillars for Personal Apps:
       - Workflow Friction (30 Points): Initial Pain Intensity (15 pts: "extremely annoying manual task" vs "mild inconvenience") + Task Frequency (15 pts).
       - Automation Potential (25 Points): Data Consistency (15 pts) + API Accessibility (10 pts).
       - Personal ROI (25 Points): Time Saved (15 pts) + Cognitive Load Reduction (10 pts).
       - Technical Feasibility (20 Points): Edge Reliability (10 pts) + Complexity (10 pts).
    - CRITICAL for market_analysis: Since this is for PERSONAL USE, do NOT focus on Blue Ocean revenue loops. Instead, analyze existing off-the-shelf tooling (like Excel, Notion, zapier) and explicitly argue why a custom-coded vibe-app is far superior to those generic tools for the user's specific workflow.
        """
    else:
        rubric_text = """
    1. Calculate an Idea Health Score (viability_score) between 0-100 based strictly on these 4 pillars for Commercial Apps:
       - Market Gravitational Pull (30 Points): Pain Intensity (15 pts: "hair on fire" vs "nice to have") + Market Growth (15 pts).
       - The "Moat" Potential (25 Points): Uncopyability (15 pts) + Data/Workflow Lock-in (10 pts).
       - Economic Scalability (25 Points): Unit Economics (15 pts) + Frequency/Retention (10 pts).
       - Technical Feasibility (20 Points): Edge Reliability (10 pts) + Complexity (10 pts).
    - CRITICAL for market_analysis: You MUST write a comprehensive, highly-detailed multi-paragraph assessment! Explore multiple competitors, deep service differences, and elaborate on the exact 'Blue Ocean' viability.
        """

    prompt = f"""
    You are SynapseIP, a ruthless, highly skeptical Business Intelligence Architect and Venture Capitalist. Your goal is to critically evaluate new app concepts.
    CRITICAL ANTI-SYCOPHANCY RULE: You must NEVER blindly validate the user's ideas to appease their ego. Do not artificially inflate the viability score. Be brutally honest about market saturation, technical hurdles, and bad product ideas. Your job is to protect the user from wasting time on unviable projects, not to be a cheerleader.
    Project Name: {req.app_name}
    Designer Name: {req.designer_name}
    Core Purpose: {req.app_purpose}
    Target Audience/Region: {req.target_audience}
    App Type: {req.app_type}
    Security & Authentication: {req.security_auth}
    Standout Features: {", ".join(req.standout_features)}
    
    Your priority is to evaluate the viability of this idea.
    Analyze the following brainstorm notes and output a rigorous structured analysis based on the exact JSON schema requested.
    DO NOT generate an expected coding pipeline, build steps, or outline here. This report is strictly for Business & Viability analysis. 
    
    For every idea submitted:
    {rubric_text}
    2. The Harsh Truth: Identify the single biggest 'Flop Risk' or 'Utility Failure Risk' for this build.
    3. The Pivot Path: Suggest one structural change to the idea that would increase its health score by at least 20 points.
    4. Verdict: Output as exactly 'Green Light (Build)', 'Yellow Light (Refine)', or 'Red Light (Pivot/Abandon)'.
    
    Strict Formatting Rules:
    1. Use `#` ONLY for the Title of the entire document.
    2. Use `##` for Chapter Titles / Core Categories.
    3. Use `###` for all Sub-headers. 
    4. Use `---` (horizontal rules) to separate distinct logic blocks.
    5. VERY IMPORTANT: You must use double line breaks (`\n\n`) to separate paragraphs and ideas! DO NOT output massive walls of text. Use bullet points (`* `) extensively for high readability.
    - Format `market_analysis` properly: Start each competitor/alternative section with a strict `### Target Competitor Name` header on its own line, followed by double line breaks (`\n\n`), and then detailed bullet points underneath. Do NOT nest headers inside bullets!
    - Format `swot` properly: MUST be formatted in Markdown with bold categories (**Strengths:**), bullet points under each category, and double line breaks (`\n\n`) separating them.
    - Format `cost_benefit` properly: MUST be formatted in Markdown with two distinct headers (**Benefits** and **Costs**), with a bulleted list (`* `) under each. Use double line breaks (`\n\n`) between items!
    - Format `blindspots` properly: MUST be formatted as a Markdown bulleted list, with double line breaks (`\n\n`) between each bullet point.
    
    Brainstorm Context:
    {context_text}
    """
    
    try:
        response = await gemini_client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': AnalysisSchema,
            },
        )
        await log_token_usage(db, "Intelligence Report", "gemini-2.5-flash", response, project_id=req.project_id)
        generated_json = response.text
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Analysis Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
    # Save generic generated report
    new_report = GeneratedReport(project_id=req.project_id, report_data=generated_json, timestamp=datetime.utcnow())
    db.add(new_report)
    db.commit()
    
    # Notify UI
    await manager.broadcast("new_report")
    
    return json.loads(generated_json)
    
@app.get("/api/reports/latest")
def get_latest_report(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    report = db.query(GeneratedReport).join(Project).filter(Project.user_id == current_user.id).order_by(GeneratedReport.timestamp.desc()).first()
    if report:
        return json.loads(report.report_data)
    return None

@app.post("/api/mockup/generate")
async def generate_mockup_prompt(req: MockupPromptRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini SDK improperly configured.")
    
    project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or not owned by user")
        
    report = db.query(GeneratedReport).filter(GeneratedReport.project_id == project.id).order_by(GeneratedReport.timestamp.desc()).first()
    if not report:
        raise HTTPException(status_code=404, detail="No intelligence report found for this project.")
        
    report_data = json.loads(report.report_data)
    summary = report_data.get('summary', 'No summary available.')
    standout_features = report_data.get('standout_features', [])
    
    prompt = f"""
    Act as a Master AI Image Prompt Engineer. You are bridging a backend MVP blueprint into a visual mockup.
    I need you to write a single, highly-detailed prompt meant to be pasted directly into DALL-E 3, Midjourney, or Gemini Advanced.
    
    The prompt should command the image AI to generate a '3-shot Dribbble-style UI presentation frame'. It must feature modern UI glassmorphism elements, vibrant deep gradients, and high fidelity.
    
    App Summary context:
    {summary}
    
    Output ONLY the raw image-generation prompt text. Do not include any conversational filler, markdown formatting, or quotes around the prompt itself. It must be instantly ready to copy-paste.
    """
    
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {"prompt": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return None

async def verify_npm_packages(packages: List[str]) -> List[str]:
    """Queries the NPM registry and returns a list of packages that returned 404 (hallucinated)."""
    invalid_packages = []
    async with httpx.AsyncClient() as client:
        for pkg in packages:
            # Strip versions (e.g. "lucide-react@0.2.1" -> "lucide-react")
            base_pkg = pkg.split('@')[0] if not pkg.startswith('@') else '@' + pkg[1:].split('@')[0]
            try:
                res = await client.get(f"https://registry.npmjs.org/{base_pkg}", timeout=5.0)
                if res.status_code == 404:
                    invalid_packages.append(pkg)
            except Exception as e:
                print(f"NPM validation failed for {pkg}: {e}")
                # Assume valid if registry times out
    return invalid_packages

async def generate_architect_report(project_id: int, source_texts: str, platform: str, designer: str, app_name: str, app_purpose: str, budget_constraints: str, ai_integration: str, security_auth: str, build_environment: str, loop0_draft: str = "", loop1_draft: str = "", loop2_draft: str = ""):
    db = SessionLocal()
    try:
        await manager.broadcast(json.dumps({"type": "progress", "message": "Initializing Architect Framework...", "progress": 10}))
    
        outline_prompt = f"""
        You are an expert technical and business architect defining an MVP build process for a new app.
        App Name: {app_name}
        App Purpose: {app_purpose}
        Designer: {designer}
        Target Vibe Coding Platform: {platform}
        Budget / Hosting Constraints: {budget_constraints}
        AI Role & Functionality: {ai_integration}
        Security & Authentication Strategy: {security_auth}
        Build Environment: {build_environment}
        
        APPROVED LOOP 0 (Layman's Overview):
        {loop0_draft}
        
        APPROVED LOOP 1 (System Workflow):
        {loop1_draft}
        
        APPROVED LOOP 2 (Tech Stack):
        {loop2_draft}
    
        Analyze the raw notes below and output a strict structural outline. 
        The outline must be restricted to logical MVP feature building steps following 2026 Vibe Coding best practices (Intent -> Plan -> Generate -> Vibe-Check). Include chronological layer-building: Data schema first -> API next -> UI/Frontend components last.
        
        CRITICAL RULES FOR QUALITY OVER QUANTITY:
        - Build Environment Rule: You must tailor your steps to the "{build_environment}" classification. If it is "Greenfield (New)", provide foundational setup instructions (e.g., 'Initialize Next.js project', 'Setup base database schemas'). If it is "Brownfield (Existing)", you MUST assume the core project already exists. Focus your outline exclusively on safely integrating new features into the existing architecture, requiring adapter patterns, non-breaking schema migrations, and heavy regression-testing rules.
        - Do NOT ignore Agentic Memory. The very first step MUST be establishing `.cursorrules` or `AGENTS.md` context files with strict guardrails ("Never edit >3 files without confirmed plan. Always run tsc").
        - Build Efficiently & Thoroughly. Break down the architecture into logical, cohesive steps. Do not enforce a strict quota or cap on the number of steps, but ensure the outline is concise enough to avoid excessive verbosity, while remaining thorough enough to securely build the MVP. Ensure high quality.
        - Artifact Locking: Dictate explicitly where the user should execute a "Pre-Flight Impact Analysis" to force the agent to write an `implementation_plan.md` detailing "Dependency Risks" and "Verification Strategy" before risking regression on core components.
        - Chapter titles MUST be written in extremely simple, concise layman's terms (e.g., "User Login Screen", "Database Setup", "Save Button Logic"). Do not use overly technical jargon or long run-on sentences for the title.
        - Separation of AI Concerns (Crucial): You MUST structurally isolate AI Generator tasks from AI Evaluator tasks into entirely separate, distinct chapters. If a feature requires the AI to generate content (e.g. an article, a quiz, code) AND evaluate that content (e.g. grading, scoring, validation), these CANNOT be in the same chapter. Separate them into "Chapter X: Generate Content" and "Chapter Y: Evaluate Content" to prevent the Self-Grading Homework fallacy.
        - Because you know the Budget/Hosting Constraints: During the infrastructure architecture phase, you MUST explicitly recommend whether they should use platforms like Render, Vercel, Supabase, Pinecone, or other alternatives based exactly on their Budget ({budget_constraints}) and Target Audience. Explain the tradeoff briefly.
        - Because you know the AI Role & Functionality: You MUST explicitly recommend which specific AI foundation models (e.g., Claude 3.5 Sonnet, Gemini 2.5 Flash/Pro, GPT-4o, Llama 3) would be mathematically ideal for these isolated tasks. If multiple AI models are needed, explain which AI is most efficient at each specific task.
        
        MANDATORY EARLY CHAPTERS (you must include these in the outline before any UI/feature steps):
        - One of the first 3 chapters MUST be "Define Database Schema" where the exact DDL/SQL/Prisma schema is written out with all table names, column names, types, and relationships.
        - One of the first 5 chapters MUST be "Define API Contracts" where the exact REST/GraphQL endpoints, request payloads, and response shapes are documented as strict JSON interface contracts.
        - One early chapter MUST be "Define Directory Structure" where the complete project folder tree is output so every subsequent step knows exactly where files live.
        - One early chapter MUST be "Environment Variables & Secrets" where a complete `.env.example` file is defined with every required API key, database URL, and configuration variable.
    
        Raw Notes:
        {source_texts}
        """
    
        try:
            outline_res = await gemini_client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=outline_prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': OutlineSchema,
                },
            )
            await log_token_usage(db, "Architect Generation", "gemini-2.5-flash", outline_res, project_id=project_id)
            outline_data = json.loads(outline_res.text)
            import re
            raw_chapters = outline_data.get('chapters', [])
            chapters = [re.sub(r'^(Step\s*\d+[\.\:]?\s*|\d+[\.\:]\s*)', '', c.strip(), flags=re.IGNORECASE) for c in raw_chapters]
        except Exception as e:
            await manager.broadcast(json.dumps({"type": "error", "message": f"Outline generation failed: {str(e)}"}))
            return

        # Start Markdown Document
        current_date = datetime.utcnow().strftime('%Y-%m-%d')
        markdown_content = f"# {app_name} - Master Blueprint\n\n"
        markdown_content += f"**Designer:** {designer}\n\n"
        markdown_content += f"**Target Platform:** {platform}\n\n"
        markdown_content += f"**Version:** 1.0.0\n\n"
        markdown_content += f"**Date:** {current_date}\n\n"
        markdown_content += "---\n\n"
        markdown_content += f"## Executive Purpose\n{app_purpose}\n\n"
        markdown_content += "---\n\n"
        markdown_content += "## 🧭 How to Use This Blueprint\n\n"
        markdown_content += "> [!IMPORTANT]\n"
        markdown_content += "> **The Backend-First Approach:** Because this application requires a robust data foundation, this blueprint is designed 'Backend-First'. This is different from a typical 'UI-First' vibe coding approach where you start with a visual mockup.\n> \n"
        markdown_content += "> **What to expect:** For the first half of this blueprint, you are building the 'engine'—database schemas, APIs, and background pipelines. **You will not see a visual user interface during these steps.** Once the engine is secure, the later steps will guide you to build the frontend UI that connects to it.\n\n"
        markdown_content += "### 💡 Copy-Paste Workflow\n"
        markdown_content += "Every step in this document contains **Copy & Paste blocks** for your IDE's AI (like Cursor, Windsurf, or OpenClaw).\n"
        markdown_content += "1. Copy the **Phase 1: Planning** block and paste it into your AI chat.\n"
        markdown_content += "2. Wait for the AI to generate an `implementation_plan.md` and review it.\n"
        markdown_content += "3. Once approved, copy the **Phase 2: Execution** block to instruct the AI to write the actual code.\n\n"
        markdown_content += "---\n\n"
        markdown_content += "## Table of Contents\n\n"
    
        # Generate TOC
        markdown_content += "- [ ] [Step 0: Initialize Project Rules](#step-0-initialize-project-rules)\n"
        for idx, chapter in enumerate(chapters):
            # Generate safe anchor
            anchor = chapter.lower().replace(' ', '-').replace('.', '').replace(':', '')
            markdown_content += f"- [ ] [Step {idx + 1}: {chapter}](#step-{idx+1}-{anchor})\n"
        
        markdown_content += "\n---\n\n"
        
        # ----------------------------------------------------
        # Step 0: Generate PROJECT_RULES.md (Templated)
        # ----------------------------------------------------
        await manager.broadcast(json.dumps({"type": "progress", "message": "Normalizing framework platform...", "progress": 12}))
        
        norm_prompt = f"Normalize this platform name into a standard category string (e.g. 'Next.js (App Router)', 'React Native (Expo)', 'Vue/Nuxt'). If unknown, just return the exact name. Input: {platform}"
        norm_res = await gemini_client.aio.models.generate_content(model='gemini-2.5-flash', contents=norm_prompt)
        normalized_platform = norm_res.text.strip()
        
        template_record = db.query(FrameworkTemplate).filter(FrameworkTemplate.normalized_name == normalized_platform).first()
        
        if not template_record:
            await manager.broadcast(json.dumps({"type": "progress", "message": f"Generating expert {normalized_platform} template via Pro...", "progress": 14}))
            pro_prompt = f"""
            You are an elite software architect.
            Define the golden standard `PROJECT_RULES.md` for a {normalized_platform} project.
            This will be used as a master template.
            
            [CRITICAL SYSTEM RULE: THE TECH STACK MATRIX]
            You are generating an architecture blueprint. Before writing Step 0 or any subsequent steps, you must select ONE cohesive technology stack optimized for {normalized_platform} and strictly adhere to it across the entire document.
            You must explicitly define STACK A at the very top:
            - Framework: (e.g., Next.js, React Native, etc.)
            - UI: (e.g., React .tsx files)
            - Styling: (e.g., Tailwind CSS)
            - State: (e.g., Zustand)
            
            BANNED BEHAVIOR: You must NEVER mix concepts, file extensions, or state managers from conflicting frameworks (e.g., never mix Vue/Nuxt/Pinia rules if the platform is React/Next.js). If you mix ecosystems, the system architecture will fail.

            Include: 1. Tech Stack Version Lock (MUST include a strict 'Tech Matrix' explicitly declaring the chosen Frontend, Backend, Database, Deployment, and AI Provider), 2. Project Directory Structure (ASCII), 3. Component Modularity (150 lines max), 4. Data Fetching, 5. State Management (Explicitly define the architecture for Global vs Local state, and mandate that all UI components clearly declare which state they consume), 6. UI/Styling constraints, 7. Testing Requirements (Must explicitly mandate testing for both 'happy paths' (successful execution) AND 'error boundaries/edge cases' (failures), detailing unit vs integration strategies), 8. API & Data Conventions, 9. Environment Variables Template, 10. Agent Safety Guardrails (Must include mandatory verification checkpoints after each major sub-task, instructing the AI to run automated verification checks—like unit tests or tsc compile checks—to verify success before proceeding), 11. Data Validation Standards (Define how constraints like min/max lengths, required fields, and regex matching should be handled across the database, API, and frontend), 12. Error Handling & Edge Cases (Must define a standardized API error response schema, exact HTTP status codes to use, and conventions for handling edge cases like duplicate records or rate limits), 13. Infrastructure Physics (Use standard serverless API routes for simple tasks like streaming text, but establish an asynchronous 'Long-Running Task' pattern—e.g., background workers—ONLY for truly heavy processing like bulk scraping), 14. Separation of AI Concerns (NEVER allow an AI to grade or self-evaluate its own output. To prevent the 'Self-Grading Homework' fallacy, any task requiring content generation AND quality evaluation must be split into two distinct API calls: a Generator worker and an Evaluator worker. Complex multi-step tasks, like writing an article AND generating a quiz, must also be separated into distinct AI pipeline steps to avoid context dilution.), 15. Deterministic Data Contracts (When an AI feature returns data for a database or UI, you MUST mandate SDK-level Structured Outputs with strict JSON Schema definitions—e.g., passing a Zod schema to the AI provider API. Never rely on basic string prompting like 'Please return JSON').
            Output ONLY the raw text for the file. Do not wrap in markdown fences.
            """
            pro_res = await gemini_client.aio.models.generate_content(model='gemini-2.5-pro', contents=pro_prompt)
            await log_token_usage(db, "Template Pro Generation", "gemini-2.5-pro", pro_res, project_id=project_id)
            master_template = pro_res.text.strip()
            if master_template.startswith("```markdown"): master_template = master_template[11:]
            if master_template.startswith("```"): master_template = master_template[3:]
            if master_template.endswith("```"): master_template = master_template[:-3]
            master_template = master_template.strip()
            
            try:
                new_template = FrameworkTemplate(normalized_name=normalized_platform, content=master_template)
                db.add(new_template)
                db.commit()
            except Exception as e:
                db.rollback()
                print("Failed to save template:", e)
        else:
            master_template = template_record.content
            
        await manager.broadcast(json.dumps({"type": "progress", "message": "Injecting project logic into standard template...", "progress": 15}))
        rules_prompt = f"""
        You are a principal architect defining the `PROJECT_RULES.md` for a new project.
        App Name: {app_name}
        Purpose: {app_purpose}
        Environment: {build_environment}
        Raw Notes/Themes: {source_texts}
        
        Here is the GOLDEN STANDARD TEMPLATE for this framework ({normalized_platform}):
        ---
        {master_template}
        ---
        
        [CRITICAL SYSTEM RULE: THE TECH STACK MATRIX]
        Before writing Step 0 or any subsequent steps, you must select ONE cohesive technology stack optimized for {normalized_platform} and strictly adhere to it across the entire document.
        You must explicitly define STACK A at the very top:
        - Framework: (e.g., Next.js, React Native, etc.)
        - UI: (e.g., React .tsx files)
        - Styling: (e.g., Tailwind CSS)
        - State: (e.g., Zustand)
        BANNED BEHAVIOR: You must NEVER mix concepts, file extensions, or state managers from conflicting frameworks.
        
        Your job is to read the standard template and INJECT the user's specific business logic, color palettes, data schemas, and requirements into it.
        DO NOT alter the core directory structure or framework rules from the template. Just fill in the placeholders and add specific business rules.
        Output ONLY the text meant to go inside the file, no markdown code fences or surrounding chatter.
        """
        try:
            rules_res = await gemini_client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=rules_prompt
            )
            await log_token_usage(db, "Project Rules Injection", "gemini-2.5-flash", rules_res, project_id=project_id)
            rules_text = rules_res.text.strip()
            
            # --- Devil's Advocate Subagent ---
            da_retries = 0
            while da_retries < 2:
                da_prompt = f"""
                You are a Senior Staff Security & Architecture Reviewer. Review the following architecture draft:
                {rules_text}
                
                Look for:
                1. Missing database relationships or flawed data modeling.
                2. Impossible library combinations.
                3. Security flaws (e.g., missing auth rules).
                
                If the draft is fundamentally solid and free of major flaws, output exactly and ONLY: APPROVED
                If there are flaws, output a concise bulleted list of the flaws. Do not output the word APPROVED.
                """
                await manager.broadcast(json.dumps({"type": "progress", "message": f"Pre-Flight: Devil's Advocate QA Review (Attempt {da_retries+1})...", "progress": 16}))
                
                da_res = await gemini_client.aio.models.generate_content(
                    model='gemini-2.5-pro',
                    contents=da_prompt
                )
                await log_token_usage(db, "Devil's Advocate Review", "gemini-2.5-pro", da_res, project_id=project_id)
                da_critique = da_res.text.strip()
                
                if da_critique.strip().upper() == "APPROVED":
                    break
                    
                await manager.broadcast(json.dumps({"type": "progress", "message": "Healing Blueprint: Architect rewriting rules based on QA feedback...", "progress": 17}))
                fix_prompt = f"""
                You previously generated these project rules:
                {rules_text}
                
                The QA reviewer found the following flaws:
                {da_critique}
                
                Rewrite the precise contents of the `PROJECT_RULES.md` file to address these flaws. Maintain all required sections.
                Output ONLY the text meant to go inside the file, no markdown code fences or surrounding chatter.
                """
                fix_res = await gemini_client.aio.models.generate_content(
                    model='gemini-2.5-pro',
                    contents=fix_prompt
                )
                await log_token_usage(db, "Architect Rewrite", "gemini-2.5-pro", fix_res, project_id=project_id)
                rules_text = fix_res.text.strip()
                da_retries += 1
            # --- END Devil's Advocate Subagent ---
            
            # --- NPM Package Validation Subagent ---
            retries = 0
            while retries < 2:
                extract_prompt = f"""
                Extract all NPM package names mentioned in the following text.
                Return ONLY a JSON list of strings. If none, return [].
                Do not include versions, just the base package name (e.g. 'lucide-react', '@supabase/supabase-js').
                
                Text:
                {rules_text}
                """
                try:
                    extract_res = await gemini_client.aio.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=extract_prompt,
                        config={'response_mime_type': 'application/json'}
                    )
                    packages = json.loads(extract_res.text.strip())
                    if packages and isinstance(packages, list):
                        await manager.broadcast(json.dumps({"type": "progress", "message": f"Pre-Flight: Validating {len(packages)} NPM packages...", "progress": 18}))
                        invalid_packages = await verify_npm_packages(packages)
                        if invalid_packages:
                            await manager.broadcast(json.dumps({"type": "progress", "message": f"Healing Blueprint: Fixing hallucinated packages...", "progress": 18}))
                            fix_prompt = f"""
                            You previously generated these project rules:
                            {rules_text}
                            
                            The following packages DO NOT EXIST on NPM and are hallucinations:
                            {json.dumps(invalid_packages)}
                            
                            Rewrite the project rules to silently remove or replace these hallucinated packages with standard, popular alternatives that actually exist. Maintain all formatting.
                            """
                            fix_res = await gemini_client.aio.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=fix_prompt
                            )
                            rules_text = fix_res.text.strip()
                            retries += 1
                            continue
                except Exception as e:
                    print("NPM extraction/validation failed, bypassing:", e)
                break
            # --- END NPM Package Validation Subagent ---
            
            # --- Visual Architecture Subagent (Mermaid.js) ---
            await manager.broadcast(json.dumps({"type": "progress", "message": "Drafting visual Mermaid.js component architecture...", "progress": 19}))
            mermaid_prompt = f"""
            Based on the following PROJECT_RULES.md:
            {rules_text}
            
            Generate a Mermaid.js diagram (using flowchart TD) that visualizes the core architecture, high-level user flow, and major component tree of this application.
            Keep it clean and readable. Use standard mermaid syntax.
            CRITICAL SYNTAX RULES TO PREVENT CRASHES:
            1. You MUST enclose all node labels containing spaces, parentheses, or special characters in double quotes. Example: id["Label (Extra Info)"] instead of id[Label (Extra Info)].
            2. Avoid HTML tags entirely.
            3. Do not use unescaped characters.
            Output ONLY the raw mermaid code. Do NOT wrap it in markdown ```mermaid fences, just the code itself.
            """
            try:
                mermaid_res = await gemini_client.aio.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=mermaid_prompt
                )
                await log_token_usage(db, "Mermaid Diagram Generation", "gemini-2.5-flash", mermaid_res, project_id=project_id)
                mermaid_code = mermaid_res.text.strip()
                if mermaid_code.startswith("```mermaid"):
                    mermaid_code = mermaid_code[10:]
                if mermaid_code.startswith("```"):
                    mermaid_code = mermaid_code[3:]
                if mermaid_code.endswith("```"):
                    mermaid_code = mermaid_code[:-3]
                mermaid_code = mermaid_code.strip()
            except Exception as e:
                print("Failed to generate mermaid diagram:", e)
                mermaid_code = ""
            # --- END Visual Architecture Subagent ---
            
            markdown_content += f"<a id='step-0-initialize-project-rules'></a>\n"
            markdown_content += f"## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='-1'> Step 0: Initialize Project Rules</label>\n\n"
            if mermaid_code:
                markdown_content += f"### Architecture Overview\n```mermaid\n{mermaid_code}\n```\n\n"
            markdown_content += "### ⚠️ Don't Panic! This file is huge.\n"
            markdown_content += "The code block below contains the master architectural rules for your entire project. **You do not need to read or understand it.**\n\n"
            markdown_content += "**Instructions:**\n"
            markdown_content += "1. Create a file named `PROJECT_RULES.md` in the root folder of your project.\n"
            markdown_content += "2. Copy the *entire* text block below and paste it into that file.\n"
            markdown_content += "3. Your AI coding assistant will automatically read this file to ensure it doesn't break your architecture in future steps.\n\n"
            markdown_content += f"````text\n{rules_text}\n````\n\n---\n\n"
        except Exception as e:
            print(f"Failed to generate project rules: {e}")
    
        total_chapters = len(chapters)
        await manager.broadcast(json.dumps({"type": "progress", "message": f"Outline verified. Writing {total_chapters} MVP feature iterations...", "progress": 20}))
    
        rolling_architecture_context = "No previous architectural decisions have been made yet."
    
        for i, chapter_title in enumerate(chapters):
            prog = 20 + int((i / total_chapters) * 70)
            await manager.broadcast(json.dumps({"type": "progress", "message": f"Drafting MVP Feature {i+1}: {chapter_title}...", "progress": prog}))
            
            # ----------------------------------------------------
            # Pinecone Vector-Routing RAG
            # ----------------------------------------------------
            relevant_sources_text = "No additional raw sources found."
            if pinecone_index is not None and gemini_client is not None:
                try:
                    query_text = f"How to build {chapter_title} for {app_name}: {app_purpose}"
                    res = await gemini_client.aio.models.embed_content(
                        model='gemini-embedding-2',
                        contents=query_text
                    )
                    vector = res.embeddings[0].values
                    pinecone_query = pinecone_index.query(vector=vector, top_k=20, namespace="synapseip_themes")
                    
                    relevant_ids = [int(match['id'].split("_")[1]) for match in pinecone_query.get('matches', []) if match['id'].startswith("theme_")]
                    if relevant_ids:
                        db_themes = db.query(ProjectTheme).filter(ProjectTheme.id.in_(relevant_ids), ProjectTheme.project_id == project_id).all()
                        relevant_sources_text = "\n\n".join([f"SYNTHESIZED THEME: {t.theme_name}\n{t.content}" for t in db_themes])
                except Exception as e:
                    print("Pinecone chapter query failed:", e)
        
            chapter_prompt = f"""
            You are an expert technical architect documenting a specific MVP feature build step.
            App Name: {app_name}
            App Purpose: {app_purpose}
            Current Feature to Write: '{chapter_title}'
            Target Platform: {platform}
            Build Environment: {build_environment}
        
            Based ONLY on the following context, write a highly concise, systematic, ordered step-by-step logic guide to build this specific feature.
        
            REQUIREMENTS:
            1. Be extremely concise. Explain why this feature is needed in 1-2 sentences. Avoid all redundant boilerplate.
            2. Provide exactly what to expect if it works or fails in 1-2 sentences.
            3. Reference EXACT file paths from the project directory structure (defined in PROJECT_RULES.md). Do NOT invent or guess file paths. Use the established structure.
            4. If this step involves database operations, reference the exact table/column names from the schema defined in the earlier "Define Database Schema" step.
            5. If this step involves API calls, reference the exact endpoint paths, payload shapes, AND specific error responses (e.g., 400 Bad Request for validation failure, 404 for not found) from the "Define API Contracts" step. You MUST explicitly define how edge cases are handled.
            9. ADAPTIVE PROMPT STRUCTURE: You MUST format the copy-paste prompt block based on the Target Platform ({platform}):
               - If the platform is "Antigravity", provide a SINGLE-PHASE prompt. (Antigravity natively utilizes a 'Planning Mode' artifact system).
               - If the platform is "Cursor", "Windsurf", or "OpenClaw", you MUST break the prompt into TWO phases ("Phase 1: Planning" and "Phase 2: Execution") to prevent overwhelming the AI's context window.
            10. DATA VALIDATION MANDATE: Whenever defining a database schema, API payload, or frontend form, you MUST list explicit data constraints (e.g., required fields, maximum character lengths, enum values, and specific regex patterns for fields like email/passwords). Never just say "String".
            11. TESTING MANDATE: You MUST explicitly define exactly what needs to be tested for this step. This must include explicitly testing the 'Happy Path' (successful execution) and explicitly testing the 'Error Boundaries / Edge Cases' (failure states).
            12. VERIFICATION CHECKPOINTS: Within the prompt, you MUST insert explicit 'Verification Checkpoints'. Instruct the AI to verify its changes (e.g., run `npx tsc` or run a test script) before completing the task.
            13. GLOBAL STATE REGISTRY CONSTRAINT: You MUST read the Tech Matrix defined in the PROJECT_RULES.md. You are STRICTLY FORBIDDEN from suggesting packages, cloud providers, or architectures that are not explicitly listed in that matrix. (e.g., If the matrix says Vercel, do not suggest AWS Lambda).
            14. INFRASTRUCTURE PHYSICS: Use standard serverless API routes for simple tasks (like streaming AI chat). You should ONLY mandate a decoupled asynchronous queue pattern (e.g., background workers) for truly heavy, long-running tasks like bulk scraping.
            15. SEPARATION OF AI CONCERNS: NEVER allow an AI to grade its own output. If a task requires content generation and validation, you MUST architect distinct Generate and Evaluate operations (a secondary Evaluator AI). Complex multi-step generations must be split into separate API calls.
            16. STRUCTURED OUTPUTS MANDATE: If this step involves an AI generating structured data (like JSON), you are STRICTLY FORBIDDEN from instructing the coding AI to just use a text prompt like 'return JSON'. You MUST instruct the coding AI to define a strict JSON Schema (e.g., using Zod) and pass it directly into the AI provider's SDK to enforce deterministic structured outputs.
            17. MARKDOWN FORMATTING MANDATE: You MUST NOT wrap your entire response in a single master code block. ONLY the text meant to be copied and pasted into the IDE must be inside triple backticks (```text). The headers (Why, Expectation, Watch Out) MUST be outside any code blocks. It is a FATAL ERROR to place the "Why", "Expectation", or "Watch Out" sections inside a markdown code block.
            
            STRICT FORMATTING TEMPLATE YOU MUST FOLLOW (Adapt the `text` block section to the target IDE {platform}):
            
            <div class="manual-action-alert">
            <h4>⚠️ Manual Developer Action Required</h4>
            <ul>
                <li>[If the developer MUST do something manually outside the IDE before writing code, list the exact steps here as bullet points.]</li>
            </ul>
            </div>
            *(NOTE: Only include the above HTML block if manual actions are actually required. If no manual account setup or configuration is required, omit it completely.)*
            
            **Why:** [Layman explanation of why this step is necessary]
            
            **Expectation:** [What should happen if this succeeds]
            
            **Watch Out:** [What could go wrong or common errors]
            
            [IF TARGET IDE IS ANTIGRAVITY, use this block:]
            **Prompt (Copy & Paste this as your request to Antigravity)**
            ```text
            [Objective]
            [Write a concise technical objective for {chapter_title}.]
            
            [Target Files & Impact Analysis]
            [List the exact 2-3 files to review first.]
            Please review these files and generate an `implementation_plan.md` detailing your approach before writing any code.
            
            [Execution Constraints]
            Strictly adhere to the global project constraints defined in `PROJECT_RULES.md`.
            [List strict technical constraints specifically relevant to THIS step ONLY.]
            
            [Verification]
            After executing the plan, please run the following command to verify your changes: [Command]
            ```
            
            [IF TARGET IDE IS CURSOR/WINDSURF/OPENCLAW, use these two blocks instead:]
            **Phase 1: Planning (Copy & Paste this into your IDE first)**
            ```text
            [Objective]
            [Write a concise technical objective for {chapter_title}.]
            
            [Artifact Locking & Pre-Flight]
            Before writing ANY code, please perform an Impact Analysis by reviewing these files: [List 2-3 files].
            Output an `implementation_plan.md` detailing the files modified and commands executed. DO NOT generate code until I explicitly approve the plan.
            ```
            
            **Phase 2: Execution (Copy & Paste this into your IDE after approving the plan)**
            ```text
            [Execution Constraints]
            Strictly adhere to the global project constraints defined in `PROJECT_RULES.md`.
            [List 1-2 strict technical constraints specifically relevant to THIS step ONLY.]
            
            Now, please execute the approved `implementation_plan.md` for this step. After execution, run the following command to verify: [Command]
            ```
            
            Strict Formatting Rules:
            1. DO NOT output a `#` or `##` header for the chapter title itself. The system will handle the chapter title. Just output the content.
            2. All data points outside the text blocks MUST be in a bulleted list (`*`) or a Markdown table.
            3. In the "Copy & Paste" code blocks, REPLACE all bracketed text `[...]` with your generated, highly specific instructions for the target AI. Do not output the brackets themselves.
            4. DO NOT output massive JSON or markdown file contents inside or outside the copy-paste blocks. Keep the prompts concise.
        
            [PREVIOUS ARCHITECTURAL DECISIONS (Maintain Strict Consistency with these)]:
            {rolling_architecture_context}
            
            [DEEP-DIVE CONTEXT (Raw Notes retrieved via Vector Search for '{chapter_title}')]:
            {relevant_sources_text}
            """
        
            try:
                chap_res = await gemini_client.aio.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=chapter_prompt
                )
                await log_token_usage(db, "Architect Generation", "gemini-2.5-flash", chap_res, project_id=project_id)
                drafted_text = chap_res.text.strip()
                
                # Self-Healing Inspector Loop
                is_valid = False
                retries = 0
                rules_text = rules_res.text.strip() if 'rules_res' in locals() else "None"
                
                while not is_valid and retries < 2:
                    # 1. Zero-Token Path Validation (Regex)
                    import re
                    # Look for file paths (e.g. src/components/Button.tsx)
                    extracted_paths = set(re.findall(r"([a-zA-Z0-9_.-]+/[a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+)", drafted_text))
                    invalid_paths = [p for p in extracted_paths if p not in rules_text and not p.startswith("http")]
                    
                    path_warning = ""
                    if invalid_paths:
                        path_warning = f"CRITICAL PATH ERROR: The following paths do not exist in the PROJECT_RULES.md directory tree: {invalid_paths}. You MUST correct them to match the official tree."
                        await manager.broadcast(json.dumps({"type": "progress", "message": f"Pre-Flight: Caught {len(invalid_paths)} hallucinated paths in '{chapter_title}'...", "progress": prog}))
                    
                    inspector_prompt = f"""
                    You are the strict Architect Inspector.
                    We are drafting Chapter: '{chapter_title}' for {app_name}.
                    
                    Global Project Rules (MUST NOT BE VIOLATED):
                    {rules_text}
                    
                    Previous Architectural Decisions (MUST BE MAINTAINED):
                    {rolling_architecture_context}
                    
                    Drafted Chapter Content to Review:
                    {drafted_text}
                    
                    {path_warning}
                    
                    Does the Drafted Chapter strictly adhere to the Project Rules and Previous Context? 
                    Does it hallucinate databases, columns, NPM packages, or UI components that contradict established architecture?
                    Does it explicitly define Data Validation constraints (min/max length, required, enums) for all schemas and forms? If it defines a schema without constraints, it is a violation.
                    Does it explicitly define standard HTTP error responses and edge-case behaviors for all newly defined API endpoints? If an API contract lacks an error schema or edge-case handling, it is a violation.
                    Does it explicitly define Testing Requirements covering both successful paths and error boundaries for this step? If it omits specific testing criteria, it is a violation.
                    Does it explicitly include Verification Checkpoints instructing the coding agent to run automated verification checks (e.g., test API before building UI)? If it lacks verification checkpoints, it is a violation.
                    If the drafted step involves UI components, does it explicitly map out which state is Global vs Local? If it introduces UI state ambiguously, it is a violation.
                    Does the draft suggest any technology, package, or cloud service (e.g., AWS, OpenAI, React Native) that contradicts the locked Tech Matrix in the Project Rules? If it violates the Tech Matrix, it is a critical violation.
                    If the draft involves truly heavy processing (e.g., bulk scraping), does it use a decoupled asynchronous queue pattern? If it places heavy processing in a standard serverless API route, it is a critical violation. (Note: simple AI streaming chat in an API route is permitted).
                    Does the draft commit the 'Self-Grading Homework Fallacy'? An AI MUST NOT evaluate or score its own output. If a feature generates content and evaluates it, it MUST be split into distinct Generator and Evaluator calls. Complex multi-step generation must also be split into separate calls.
                    Does the draft instruct an AI to generate JSON by just asking for it in a text prompt? If it fails to mandate SDK-level Structured Outputs (e.g., passing a JSON Schema constraint to the provider API), it is a critical violation.
                    Does the technical instruction provided in the draft ACTUALLY accomplish the specific goal stated in its Title? You must cross-reference the Title, Rationale, and Execution blocks for semantic alignment. If the draft hallucinates instructions (e.g., instructing the agent to build a UI when the title explicitly says Database Setup), it is a critical violation.
                    { "Does it fix the hallucinated paths mentioned above?" if invalid_paths else "" }
                    
                    Return a JSON object exactly like this:
                    {{
                        "is_valid": true,
                        "violations_found": [],
                        "corrected_markdown": ""
                    }}
                    If invalid, rewrite the chapter content entirely to fix the violations and place it in corrected_markdown.
                    CRITICAL: Do NOT wrap the corrected_markdown content in a markdown code block. Escape inner quotes properly for JSON.
                    """
                    
                    # If there are no invalid paths on the first pass, we can skip the Inspector to save tokens, 
                    # OR we can still run the Inspector for logic bugs. Let's run it but it will be fast.
                    try:
                        inspector_res = await gemini_client.aio.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=inspector_prompt,
                            config={'response_mime_type': 'application/json'}
                        )
                        await log_token_usage(db, "Inspector AI", "gemini-2.5-flash", inspector_res, project_id=project_id)
                        
                        inspector_data = json.loads(inspector_res.text.strip())
                        if inspector_data.get("is_valid", True) and not invalid_paths:
                            is_valid = True
                        else:
                            if inspector_data.get("is_valid", True) and invalid_paths:
                                # The LLM ignored the path warning and said it was valid. We force retry.
                                is_valid = False
                            else:
                                await manager.broadcast(json.dumps({"type": "progress", "message": f"Healing Blueprint: Fixing errors in '{chapter_title}'...", "progress": prog}))
                                drafted_text = inspector_data.get("corrected_markdown", drafted_text)
                            retries += 1
                    except Exception as e:
                        print("Inspector AI failed, bypassing:", e)
                        break

                anchor = chapter_title.lower().replace(' ', '-').replace('.', '').replace(':', '')
                markdown_content += f"<a id='step-{i+1}-{anchor}'></a>\n"
                markdown_content += f"## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='{i}'> Step {i+1}: {chapter_title}</label>\n\n"
                markdown_content += f"{drafted_text}\n\n---\n\n"
                
                # Consistency Subagent Evaluation
                try:
                    consistency_prompt = f"""
                    You are a system architecture consistency tracker. 
                    Analyze the following newly generated architectural step and extract any concrete architectural decisions, database schema additions, file structure modifications, or library dependencies that were established.
                    Keep it extremely concise (bullet points). If no major technical decisions were made, output "None".
                    
                    Step Content:
                    {drafted_text}
                    """
                    consist_res = await gemini_client.aio.models.generate_content(
                        model='gemini-2.5-pro',
                        contents=consistency_prompt
                    )
                    await log_token_usage(db, "Consistency Subagent", "gemini-2.5-pro", consist_res, project_id=project_id)
                    
                    if consist_res.text and "None" not in consist_res.text:
                        if rolling_architecture_context == "No previous architectural decisions have been made yet.":
                            rolling_architecture_context = ""
                        rolling_architecture_context += f"\n- {chapter_title}: {consist_res.text.strip()}"
                except Exception as e:
                    print(f"Consistency subagent failed for {chapter_title}: {e}")
                    
            except Exception as e:
                print(f"Skipping chapter {chapter_title} due to error: {e}")
        
            # THROTTLE FOR 429
            await asyncio.sleep(4)

        # Save locally in a structured project folder
        safe_app_name = app_name.replace(' ', '_').replace('/', '')
        reports_dir = os.path.join(os.getcwd(), 'Reports', safe_app_name)
        os.makedirs(reports_dir, exist_ok=True)
        
        file_path = os.path.join(reports_dir, f"{safe_app_name}_Master_Blueprint_{current_date}.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        # Also keep a static copy for local testing
        os.makedirs('static/reports', exist_ok=True)
        static_file_path = "static/reports/SynapseIP_Master_Plan.md"
        with open(static_file_path, "w", encoding="utf-8") as static_file:
            static_file.write(markdown_content)
            
        # Hook it into the actual database for persistence! 
        new_bp = ArchitectBlueprint(project_id=project_id, blueprint_data=markdown_content, timestamp=datetime.utcnow())
        db.add(new_bp)
        db.commit()
    
        await manager.broadcast(json.dumps({
            "type": "architect_complete",
            "message": "Architect Framework fully mapped and saved to your project.",
            "progress": 100,
            "markdown_content": markdown_content
        }))
    
    except Exception as e:
        print(f"Architect pipeline crashed: {e}")
        try:
            await manager.broadcast(json.dumps({"type": "error", "message": f"Architect Pipeline Error: {str(e)}"}))
        except Exception:
            pass

    finally:
        db.close()

@app.get("/api/admin/fix-blueprint/{project_id}")
def fix_blueprint_markdown(project_id: int, db: Session = Depends(get_db)):
    import re
    blueprint = db.query(ArchitectBlueprint).filter(ArchitectBlueprint.project_id == project_id).order_by(ArchitectBlueprint.timestamp.desc()).first()
    if not blueprint:
        return {"error": "No blueprint found"}
        
    text = blueprint.blueprint_data
    
    # Split the document into chapters by the separator
    chapters = re.split(r'\n---\n', text)
    
    fixed_chapters = []
    for i, chap in enumerate(chapters):
        # We only care about fixing broken backticks in the chapters, which have "Why" or "Step"
        # Let's just count the number of triple backticks in this chapter.
        # But wait, we must be careful not to count quadruple backticks.
        # Find all occurrences of 3 or more backticks
        fences = re.findall(r'^```.*$', chap, flags=re.MULTILINE)
        
        # If there's an odd number of fences, it means the block wasn't closed!
        if len(fences) % 2 != 0:
            # It's missing a closing backtick at the end (because my previous script deleted it)
            chap = chap.rstrip() + "\n```\n"
            
        fixed_chapters.append(chap)
        
    # Rejoin the chapters
    text = "\n---\n".join(fixed_chapters)
    
    blueprint.blueprint_data = text
    db.commit()
    return {"message": "Blueprint repaired! The unclosed markdown blocks have been fixed. Please refresh.", "success": True}

@app.post("/api/architect/edit-blueprint")
async def edit_blueprint_segment(req: BlueprintEditRequest, db: Session = Depends(get_db)):
    try:
        blueprint = db.query(ArchitectBlueprint).filter(ArchitectBlueprint.project_id == req.project_id).order_by(ArchitectBlueprint.timestamp.desc()).first()
        if not blueprint:
            raise HTTPException(status_code=404, detail="No blueprint found to edit")
            
        full_markdown = blueprint.blueprint_data
        
        # Guardrail against sending gigantic texts if not necessary, but gemini 2.5 flash handles 1M tokens natively.
        # We will use Flash for this fast patch operation
        system_prompt = "You are a surgical technical editor. You must follow instructions precisely and return ONLY a valid JSON object."
        
        formatting_rules = ""
        if req.container_preference == "outside":
            formatting_rules = "\nFORMATTING INSTRUCTION: The user has requested this text be placed OUTSIDE the copy/paste code block. The 'new_markdown' output MUST NOT be wrapped in ``` or any code fence. Format it as plain text markdown (e.g. paragraphs, bold, lists)."
        elif req.container_preference == "inside":
            formatting_rules = "\nFORMATTING INSTRUCTION: The user has requested this text be placed INSIDE the copy/paste code block. The 'new_markdown' output MUST be formatted as a raw code block or placed inside existing ``` fences so it can be easily copied to an IDE."
        
        user_instruction_block = ""
        if req.instructions and req.instructions.strip():
            user_instruction_block = f"USER INSTRUCTION:\n{req.instructions}"
        else:
            user_instruction_block = "USER INSTRUCTION:\nJust reformat the original exact markdown corresponding to the highlighted text according to the FORMATTING INSTRUCTION below. You must preserve the internal markdown formatting (like bolding, lists, and links) of the original text, merely changing whether it sits inside or outside a code fence."
            
        user_prompt = f"""
        A developer highlighted a specific section of their architectural blueprint and requested a change.
        
        HIGHLIGHTED TEXT (This is what the user highlighted in their browser, so it may lack markdown formatting):
        {req.highlighted_text}
        
        {user_instruction_block}
        {formatting_rules}
        
        FULL MARKDOWN DOCUMENT:
        ---
        {full_markdown}
        ---
        
        TASK:
        1. Locate the EXACT raw markdown snippet in the FULL MARKDOWN DOCUMENT that corresponds to the HIGHLIGHTED TEXT. Expand your match to encompass full markdown blocks (e.g., if they highlighted half a paragraph or code block, grab the whole paragraph or code block) to ensure a clean replacement.
        2. Rewrite that specific snippet according to the USER INSTRUCTION. Keep the surrounding architecture logic consistent.
        3. Return a JSON object with exactly two keys:
           - "exact_old_markdown": The EXACT literal string from the FULL MARKDOWN DOCUMENT that needs to be replaced.
           - "new_markdown": Your rewritten replacement string.
           
        CRITICAL: The "exact_old_markdown" MUST be a perfect substring match of the FULL MARKDOWN DOCUMENT. If it is not a perfect match, the python `string.replace()` function will fail.
        """
        
        response = await gemini_client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[system_prompt, user_prompt],
            config={'response_mime_type': 'application/json'}
        )
        
        await log_token_usage(db, "Blueprint In-Place Editor", "gemini-2.5-flash", response, project_id=req.project_id)
        
        try:
            edit_data = json.loads(response.text.strip())
            old_str = edit_data.get("exact_old_markdown", "")
            new_str = edit_data.get("new_markdown", "")
            
            if not old_str:
                raise ValueError("AI returned an empty exact_old_markdown string.")
                
            if old_str not in full_markdown:
                if old_str.strip() in full_markdown:
                    old_str = old_str.strip()
                    updated_markdown = full_markdown.replace(old_str, new_str)
                elif old_str.rstrip() in full_markdown:
                    old_str = old_str.rstrip()
                    updated_markdown = full_markdown.replace(old_str, new_str)
                elif old_str.lstrip() in full_markdown:
                    old_str = old_str.lstrip()
                    updated_markdown = full_markdown.replace(old_str, new_str)
                else:
                    # Final Fallback: Whitespace-Agnostic Regex Matching
                    import re
                    # Escape the raw old_str to be safe for regex
                    pattern_str = re.escape(old_str)
                    # Replace any sequence of whitespace (escaped or literal) with \s+
                    pattern_str = re.sub(r'(\\\\[\s]|[\s])+', r'\\s+', pattern_str)
                    
                    match = re.search(pattern_str, full_markdown)
                    if match:
                        updated_markdown = full_markdown[:match.start()] + new_str + full_markdown[match.end():]
                    else:
                        raise ValueError("The AI failed to return an exact matching substring, and fuzzy matching failed. The replacement target could not be found in the document.")
            else:
                updated_markdown = full_markdown.replace(old_str, new_str)
                
            blueprint.blueprint_data = updated_markdown
            db.commit()
            
            return {"success": True, "updated_markdown": updated_markdown}
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="AI returned invalid JSON.")
        except Exception as parse_e:
            raise HTTPException(status_code=400, detail=str(parse_e))
            
    except Exception as e:
        print(f"Edit Blueprint Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/tokens")
def get_token_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from sqlalchemy import func
    total_prompt = db.query(func.sum(TokenLog.prompt_tokens)).filter(TokenLog.user_id == current_user.id).scalar() or 0
    total_comp = db.query(func.sum(TokenLog.completion_tokens)).filter(TokenLog.user_id == current_user.id).scalar() or 0
    total_cost = db.query(func.sum(TokenLog.cost)).filter(TokenLog.user_id == current_user.id).scalar() or 0.0
    
    return {
        "tokens": total_prompt + total_comp,
        "cost": total_cost
    }

@app.get("/api/admin/metrics")
def admin_metrics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    from sqlalchemy import func
    
    total_tokens = db.query(func.sum(TokenLog.prompt_tokens) + func.sum(TokenLog.completion_tokens)).scalar() or 0
    total_cost = db.query(func.sum(TokenLog.cost)).scalar() or 0.0
    
    from sqlalchemy import desc
    
    if "sqlite" in engine.url.drivername:
        hour_func = func.strftime('%Y-%m-%d %H:00:00', TokenLog.timestamp)
    else:
        hour_func = func.date_trunc('hour', TokenLog.timestamp)
    
    results = db.query(
        hour_func.label("hour_group"),
        func.max(TokenLog.timestamp).label("last_run_time"),
        TokenLog.action,
        Project.name.label("project_name"),
        User.id.label("user_id"),
        User.username.label("username"),
        func.sum(TokenLog.prompt_tokens + TokenLog.completion_tokens).label("tokens"),
        func.sum(TokenLog.cost).label("cost"),
        func.count(TokenLog.id).label("requests_count")
    ).outerjoin(Project, TokenLog.project_id == Project.id)\
     .outerjoin(User, TokenLog.user_id == User.id)\
     .group_by(hour_func, TokenLog.action, Project.name, User.id, User.username)\
     .order_by(desc("last_run_time")).all()
     
    breakdown = []
    for r in results:
        utc_timestamp = r.last_run_time.isoformat() + "Z" if r.last_run_time and hasattr(r.last_run_time, 'isoformat') else None
        breakdown.append({
            "timestamp": utc_timestamp,
            "action": r.action,
            "project": r.project_name or "Global / Unassigned",
            "user_id": r.user_id or 1,
            "username": r.username or "Anonymous User",
            "tokens": r.tokens or 0,
            "cost": r.cost or 0.0
        })
        
    return {
        "kpis": {"total_tokens": total_tokens, "total_cost": round(total_cost, 4)},
        "breakdown": breakdown
    }

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse(request=request, name="admin.html")

def get_project_context(project_id: int, db: Session):
    final_context = []
    
    themes = db.query(ProjectTheme).filter(ProjectTheme.project_id == project_id).all()
    if themes:
        theme_strings = []
        for t in themes:
            theme_content = t.content
            # Dynamically fetch unconsolidated fragments if content is missing
            if not theme_content:
                fragments = db.query(ProjectThemeFragment).filter(ProjectThemeFragment.theme_id == t.id).all()
                if fragments:
                    theme_content = "\n---\n".join([f.content for f in fragments])
            
            if theme_content:
                theme_strings.append(f"THEME: {t.theme_name}\n{theme_content}")
                
        if theme_strings:
            theme_str = "\n\n========================\n\n".join(theme_strings)
            final_context.append(f"--- HIGH FIDELITY PROJECT THEMES ---\n{theme_str}\n--- END THEMES ---")
            
    # Explicitly fetch ONLY unprocessed raw sources
    unprocessed_sources = db.query(GeminiSource).filter(GeminiSource.project_id == project_id, GeminiSource.processed == False).all()
    if unprocessed_sources:
        memories = []
        for s in unprocessed_sources:
            memories.append(f"Source: {s.title}\nContent: {s.content}")
        raw_str = "\n\n---\n\n".join(memories)
        final_context.append(f"--- UNPROCESSED RAW BRAINSTORM NOTES ---\n{raw_str}\n--- END RAW NOTES ---")
            
    latest_intel = db.query(GeneratedReport).filter(GeneratedReport.project_id == project_id).order_by(GeneratedReport.timestamp.desc()).first()
    if latest_intel:
        final_context.append(f"--- LATEST APPROVED INTELLIGENCE REPORT ---\n{latest_intel.report_data}\n--- END INTELLIGENCE REPORT ---")
        
    if not final_context:
        return "No intelligence context available."
        
    return "\n\n".join(final_context)

@app.get("/api/architect/state/{project_id}")
async def get_architect_state(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project: raise HTTPException(status_code=404, detail="Project not found")
    state = db.query(ArchitectDraftState).filter(ArchitectDraftState.project_id == project.id).first()
    if not state:
        state = ArchitectDraftState(project_id=project.id, current_loop=0)
        db.add(state)
        db.commit()
        db.refresh(state)
    return ArchitectStateResponse(
        current_loop=state.current_loop,
        loop0_draft=state.loop0_draft,
        loop1_draft=state.loop1_draft,
        loop2_draft=state.loop2_draft
    )

@app.post("/api/architect/loop0")
async def generate_loop0(req: ArchitectLoopRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        await check_circuit_breaker(current_user.id, db)
    except CircuitBreakerException as e:
        raise HTTPException(status_code=402, detail=str(e))
        
    project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == current_user.id).first()
    if not project: raise HTTPException(status_code=404)
    state = db.query(ArchitectDraftState).filter(ArchitectDraftState.project_id == project.id).first()
    if not state:
        state = ArchitectDraftState(project_id=project.id)
        db.add(state)
    
    context = truncate_context_for_tokens(get_project_context(project.id, db))
    feedback_str = f"\n\nUSER FEEDBACK / REFINEMENT:\n{req.feedback}" if req.feedback else ""
    prior_draft = f"\n\nPRIOR DRAFT TO REFINE:\n{state.loop0_draft}" if state.loop0_draft and req.feedback else ""
    
    prompt = f"""
    You are the Principal Architect. Provide a 'Layman's App Overview' (Loop 0).
    App Name: {req.app_name}
    App Purpose: {req.app_purpose}
    Target Audience: {req.target_audience if hasattr(req, 'target_audience') else 'General'}
    Standout Features: {", ".join(req.standout_features)}
    Context: {context}
    {prior_draft}
    {feedback_str}
    
    Synthesize this and output a purely Layman's summary. Format with Markdown. Do NOT write code. Just explain the app's core purpose, its target audience, and the exact features we are going to build. If there is USER FEEDBACK, you must incorporate their changes.
    """
    
    try:
        res = await gemini_client.aio.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        state.loop0_draft = res.text.strip()
        state.current_loop = 0
        db.commit()
        return {"draft": state.loop0_draft, "current_loop": state.current_loop}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/architect/loop1")
async def generate_loop1(req: ArchitectLoopRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        await check_circuit_breaker(current_user.id, db)
    except CircuitBreakerException as e:
        raise HTTPException(status_code=402, detail=str(e))
        
    state = db.query(ArchitectDraftState).filter(ArchitectDraftState.project_id == req.project_id).first()
    if not state or not state.loop0_draft: raise HTTPException(status_code=400, detail="Loop 0 not completed")
    
    feedback_str = f"\n\nUSER FEEDBACK / REFINEMENT:\n{req.feedback}" if req.feedback else ""
    prior_draft = f"\n\nPRIOR DRAFT TO REFINE:\n{state.loop1_draft}" if state.loop1_draft and req.feedback else ""
    
    prompt = f"""
    You are the Principal Architect. Provide the 'System Workflow Mapping' (Loop 1).
    Approved Features (Loop 0): {state.loop0_draft}
    {prior_draft}
    {feedback_str}
    
    Take the approved features and create a highly-visual, rigorous breakdown of how the system will operate logically.
    Discuss:
    1. **Data & Variables:** Define the core variables, database schemas, and state management required (e.g., "We need a User object containing id, email, and preferences").
    2. **Feature Mechanics:** Provide a step-by-step logical breakdown of exactly how the core features will function from a data perspective.
    3. **External Dependencies:** Where AI, 3rd-party APIs, or external services are required.
    4. **Workflow Diagram:** Generate a Mermaid.js flowchart mapping the complete logical workflow.
    Do NOT assign specific rigid frameworks (like Next.js) yet. Use Markdown. If there is USER FEEDBACK, adjust accordingly.
    """
    
    try:
        res = await gemini_client.aio.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        state.loop1_draft = res.text.strip()
        state.current_loop = 1
        db.commit()
        return {"draft": state.loop1_draft, "current_loop": state.current_loop}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/architect/loop2")
async def generate_loop2(req: ArchitectLoopRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        await check_circuit_breaker(current_user.id, db)
    except CircuitBreakerException as e:
        raise HTTPException(status_code=402, detail=str(e))
        
    state = db.query(ArchitectDraftState).filter(ArchitectDraftState.project_id == req.project_id).first()
    if not state or not state.loop1_draft: raise HTTPException(status_code=400, detail="Loop 1 not completed")
    
    feedback_str = f"\n\nUSER FEEDBACK / REFINEMENT:\n{req.feedback}" if req.feedback else ""
    prior_draft = f"\n\nPRIOR DRAFT TO REFINE:\n{state.loop2_draft}" if state.loop2_draft and req.feedback else ""
    
    prompt = f"""
    You are the Principal Architect. Provide 'The Skeleton' (Loop 2).
    Target Vibe Coding IDE / AI Agent: {req.target_platform} (NOTE: This is the IDE or AI tool the user will use to generate the code, NOT the deployment server. You must optimize your stack recommendations for AI generation ease inside this tool. AI agents typically prefer modern, well-documented stacks like Next.js/React/Supabase over obscure frameworks).
    Approved Workflow (Loop 1): {state.loop1_draft}
    {prior_draft}
    {feedback_str}
    
    1. Review the workflow. Identify 2-3 viable Tech Stack options (Framework, Database, Auth, State). Explain why they are suitable for this project and easy to "vibe-code" using an AI agent in the {req.target_platform} IDE.
    2. For each option, provide a brief analysis of its Strengths and Drawbacks (Trade-offs) specific to this project's scale and features.
    3. Conclude with your primary recommendation, but ask the user to confirm or choose an option via the refinement box.
    4. Provide a preliminary high-level directory structure based on your primary recommendation.
    If there is USER FEEDBACK selecting an option, lock it in and draft the PROJECT_RULES.md for that stack. Use Markdown.
    """
    
    try:
        res = await gemini_client.aio.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        state.loop2_draft = res.text.strip()
        state.current_loop = 2
        db.commit()
        return {"draft": state.loop2_draft, "current_loop": state.current_loop}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/architect/loop3_4")
async def generate_loop3_4(req: ArchitectLoopRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        await check_circuit_breaker(current_user.id, db)
    except CircuitBreakerException as e:
        raise HTTPException(status_code=402, detail=str(e))
        
    state = db.query(ArchitectDraftState).filter(ArchitectDraftState.project_id == req.project_id).first()
    if not state or not state.loop2_draft: raise HTTPException(status_code=400, detail="Loop 2 not completed")
    
    state.current_loop = 3
    db.commit()
    
    context = truncate_context_for_tokens(get_project_context(req.project_id, db))
    
    # We pass the previously approved state directly into the background task so it can synthesize the final blueprint
    background_tasks.add_task(generate_architect_report, req.project_id, context, req.target_platform, req.designer_name, req.app_name, req.app_purpose, req.budget_constraints, req.ai_integration, req.security_auth, req.build_environment, state.loop0_draft, state.loop1_draft, state.loop2_draft)
    
    return {"status": "started", "message": "Final compilation started."}

class ThemeConsolidateRequest(BaseModel):
    project_id: int

@app.get("/api/projects/{project_id}/themes")
async def get_project_themes(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project: raise HTTPException(status_code=404)
    themes = db.query(ProjectTheme).filter(ProjectTheme.project_id == project_id).all()
    
    result = []
    for t in themes:
        fragments = db.query(ProjectThemeFragment).filter(ProjectThemeFragment.theme_id == t.id).count()
        result.append({
            "id": t.id,
            "theme_name": t.theme_name,
            "content": t.content,
            "has_unconsolidated_fragments": fragments > 0
        })
    return result

@app.post("/api/architect/consolidate-themes")
async def consolidate_themes(req: ThemeConsolidateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        await check_circuit_breaker(current_user.id, db)
    except CircuitBreakerException as e:
        raise HTTPException(status_code=402, detail=str(e))
        
    project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == current_user.id).first()
    if not project: raise HTTPException(status_code=404)
    
    themes = db.query(ProjectTheme).filter(ProjectTheme.project_id == req.project_id).all()
    consolidated_count = 0
    
    for theme in themes:
        fragments = db.query(ProjectThemeFragment).filter(ProjectThemeFragment.theme_id == theme.id).all()
        if not fragments:
            continue # Already consolidated or empty
            
        fragment_text = "\n---\n".join([f.content for f in fragments])
        
        prompt = (
            f"You are a Principal Software Architect. We are writing a master theme document for a new application.\n"
            f"Theme Category: {theme.theme_name}\n\n"
            f"Below is a bucket of raw, unorganized brainstorm fragments and notes captured by the user related to this theme:\n"
            f"{fragment_text}\n\n"
            f"Write a highly cohesive, professional, and well-structured \"High-Fidelity Explanation\" of this theme based on the fragments.\n"
            f"Organize it logically. Remove redundancies. Format beautifully with Markdown."
        )
        
        try:
            res = await gemini_client.aio.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            theme.content = res.text.strip()
            
            # Delete fragments since they are now consolidated
            db.query(ProjectThemeFragment).filter(ProjectThemeFragment.theme_id == theme.id).delete()
            db.commit()
            
            if pinecone_index is not None:
                try:
                    final_embed = await gemini_client.aio.models.embed_content(
                        model='gemini-embedding-2',
                        contents=f"Topic: {theme.theme_name}\n\n{theme.content}"
                    )
                    final_vector = final_embed.embeddings[0].values
                    await asyncio.to_thread(
                        pinecone_index.upsert,
                        vectors=[(f"theme_{theme.id}", final_vector, {"title": theme.theme_name, "content": theme.content})],
                        namespace="synapseip_themes"
                    )
                except Exception as e:
                    print("Upsert consolidated theme failed:", e)
                    
            consolidated_count += 1
            await asyncio.sleep(2) # rate limit protection
        except Exception as e:
            print(f"Failed to consolidate theme {theme.id}: {e}")
            
    return {"status": "success", "consolidated_themes": consolidated_count}

# To run: uvicorn main:app --reload
