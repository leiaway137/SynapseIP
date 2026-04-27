from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import os
import json
import asyncio
from dotenv import load_dotenv
from google import genai
from typing import List, Optional

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
DATA_DIR = os.environ.get("DATA_DIR", ".")
# Force SQLite connection string, ignoring any legacy DATABASE_URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'gemini_sources.db')}"

# Initialize SQLite engine
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

class ProjectTheme(Base):
    __tablename__ = "project_themes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    theme_name = Column(String, index=True)
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

# ---------------------------------------------------------
# Pydantic Models for Validation
# ---------------------------------------------------------
class SourceCreate(BaseModel):
    title: str
    content: str
    source_url: str
    project_id: Optional[int] = None

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

class PipelineStep(BaseModel):
    title: str = Field(description="The name of this specific architecture step (e.g., 'Database Setup').")
    why: str = Field(description="Explanation of why this step exists.")
    expectation: str = Field(description="What the project state should look like after running it.")
    error_warnings: str = Field(description="What red flags to look out for regarding errors.")

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
    vibe_coding_pipeline: list[PipelineStep] = Field(description="Sequential timeline of implementation prompts.")

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
    is_complete: bool = Field(description="True if Designer Name, App Name, Core Purpose, Target Audience, App Type, Budget/Hosting Constraints, Security Strategy, and Standout Features are confidently identified. False otherwise.")
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
async def background_processor():
    while True:
        try:
            db = SessionLocal()
            project_id_to_check = None
            try:
                unprocessed = db.query(GeminiSource).filter(GeminiSource.processed == False).order_by(GeminiSource.timestamp.asc()).first()
                if not unprocessed:
                    # Check for consistency check
                    project_to_check = db.query(Project).filter(Project.notes_since_last_check >= 5).first()
                    if project_to_check:
                        project_id_to_check = project_to_check.id
                else:
                    # Detach payload from DB transaction to prevent SQLite full-table lock
                    target_id = unprocessed.id
                    raw_title = unprocessed.title
                    raw_content = unprocessed.content
                    target_project_id = unprocessed.project_id
            finally:
                db.close()

            if not unprocessed:
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

            smart_title = raw_title
            if gemini_client:
                try:
                    # 1. Fetch existing themes
                    db_themes = SessionLocal()
                    try:
                        existing_themes = db_themes.query(ProjectTheme).filter(ProjectTheme.project_id == target_project_id).all()
                        theme_names = [t.theme_name for t in existing_themes]
                    finally:
                        db_themes.close()
                    
                    # 2. Categorize or Create New Theme
                    categorize_prompt = f"""
                    You are a data architect categorizing a new brainstorm note.
                    Current existing themes for this project: {theme_names if theme_names else 'None'}
                    
                    New Note Content:
                    {raw_content[:2000]}
                    
                    Does this note belong to an existing theme, or does it require a completely new theme?
                    If it belongs to an existing theme, output ONLY the exact name of the existing theme.
                    If it needs a new theme, output ONLY the new theme name (e.g. 'Database Architecture', 'Monetization Strategy', 'UI/UX Guidelines').
                    Do not explain. Output only the theme name.
                    """
                    
                    title_prompt = f"You are a neat summarization bot. Create a professional, catchy, 3 to 6 word title summarizing this interaction. Do not use quotes, labels, or generic prefixes. Only return the title itself.\n\nText: {raw_content[:1500]}"
                    
                    cat_res = await gemini_client.aio.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=categorize_prompt
                    )
                    
                    # Log tokens using a temporary DB session
                    temp_db = SessionLocal()
                    try:
                        await log_token_usage(temp_db, "Note Categorization", "gemini-2.5-flash", cat_res, project_id=target_project_id)
                    finally:
                        temp_db.close()
                        
                    chosen_theme = cat_res.text.strip().strip('"').strip("'")
                    
                    title_res = await gemini_client.aio.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=title_prompt
                    )
                    
                    temp_db = SessionLocal()
                    try:
                        await log_token_usage(temp_db, "Note Titling", "gemini-2.5-flash", title_res, project_id=target_project_id)
                    finally:
                        temp_db.close()
                        
                    smart_title = title_res.text.strip().strip('"').strip("'")
                    if len(smart_title) > 100:
                        smart_title = smart_title[:100]
                        
                    # 3. Merge or Create Theme
                    db_merge = SessionLocal()
                    try:
                        theme_record = db_merge.query(ProjectTheme).filter(ProjectTheme.project_id == target_project_id, ProjectTheme.theme_name == chosen_theme).first()
                        
                        if theme_record:
                            # Intelligent Merge
                            merge_prompt = f"""
                            You are a highly analytical AI Synthesizer. Your job is to update an existing architecture document theme with new information.
                            Do NOT lose any important technical details, requirements, or insights from either text.
                            Seamlessly weave the new note's insights into the existing theme document. Do not just append it to the end; synthesize it logically.
                            
                            EXISTING THEME DOCUMENT:
                            {theme_record.content}
                            
                            NEW NOTE TO INTEGRATE:
                            {raw_content}
                            
                            Output ONLY the newly synthesized and merged Markdown document.
                            """
                            merge_res = await gemini_client.aio.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=merge_prompt
                            )
                            await log_token_usage(db_merge, "Theme Synthesis", "gemini-2.5-flash", merge_res, project_id=target_project_id)
                            theme_record.content = merge_res.text.strip()
                        else:
                            # New Theme
                            theme_record = ProjectTheme(
                                project_id=target_project_id,
                                theme_name=chosen_theme,
                                content=f"## {chosen_theme}\n\n{raw_content}"
                            )
                            db_merge.add(theme_record)
                            
                        db_merge.commit()
                    finally:
                        db_merge.close()
                    
                    # 4. Generate Suggested Themes
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
                        
                        sugg_res = await gemini_client.aio.models.generate_content(
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
                    
                except Exception as e:
                    print("Background processing theme consolidation failed.", e)
            
            # Reopen connection for swift instantaneous commit
            db2 = SessionLocal()
            try:
                finished_item = db2.query(GeminiSource).filter(GeminiSource.id == target_id).first()
                if finished_item:
                    finished_item.title = smart_title
                    finished_item.processed = True
                    
                    p = db2.query(Project).filter(Project.id == target_project_id).first()
                    if p:
                        p.notes_since_last_check += 1
                        
                    db2.commit()
            finally:
                db2.close()

            # Notify UI to update instantly
            await manager.broadcast("new_source")
        except Exception as e:
            print("Error in background processor:", e)
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
    
    asyncio.create_task(background_processor())
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

async def log_token_usage(db: Session, action: str, model: str, res, project_id: int = None, user_id: int = 1):
    if hasattr(res, 'usage_metadata') and res.usage_metadata:
        in_toks = getattr(res.usage_metadata, 'prompt_token_count', 0) or 0
        out_toks = getattr(res.usage_metadata, 'candidates_token_count', 0) or 0
        
        cost = 0.0
        if "flash" in model.lower():
            cost = (in_toks / 1000000.0) * 0.075 + (out_toks / 1000000.0) * 0.30
        elif "pro" in model.lower():
            cost = (in_toks / 1000000.0) * 1.25 + (out_toks / 1000000.0) * 5.00
            
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
        return {"status": "success", "requeued": len(stalled_sources)}
    finally:
        db.close()

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
    
    # Send off to ChromaDB for vector math
    background_tasks.add_task(index_in_pinecone, str(db_source.id), db_source.title, db_source.content)
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
        processed=False
    )

@app.get("/api/search")
async def semantic_search(q: str, current_user: User = Depends(get_current_user)):
    """Hits the vector database, dynamically maps query text to math via Gemini, and finds connections."""
    if pinecone_index is None or gemini_client is None:
        raise HTTPException(status_code=500, detail="Pinecone DB is natively disabled.")
    
    try:
        res = gemini_client.models.embed_content(
            model='text-embedding-004',
            contents=q,
        )
        vector = res.embeddings[0].values
        
        results = pinecone_index.query(
            vector=vector,
            top_k=5,
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
                    model='text-embedding-004',
                    contents=last_query,
                )
                vector = res.embeddings[0].values
                pinecone_query = pinecone_index.query(vector=vector, top_k=3, namespace="synapseip_notes")
                relevant_ids = [str(match['id']) for match in pinecone_query.get('matches', [])]
            except Exception as e:
                print("Pinecone warning on onboarding:", e)
                
        memories = []
        for s in sources:
            if str(s.id) in relevant_ids:
                memories.append(f"RELEVANT FULL SOURCE: {s.title}\n{s.content}")
            else:
                mem = s.short_memory if s.short_memory else "(Memory processing...)"
                memories.append(f"Source Outline: {s.title}\n{mem}")
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
    if not sources:
        raise HTTPException(status_code=400, detail="No sources found to analyze.")
        
    memories = []
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
    You are SynapseIP, an objective Business Intelligence Architect. Your goal is to evaluate new app concepts.
    Project Name: {req.app_name}
    Designer Name: {req.designer_name}
    Core Purpose: {req.app_purpose}
    Target Audience/Region: {req.target_audience}
    App Type: {req.app_type}
    Security & Authentication: {req.security_auth}
    Standout Features: {", ".join(req.standout_features)}
    
    Your priority is to ensure the resulting MVP is not just technically sound, but features a beautiful, highly usable, and modern User Interface for human users. Start the pipeline with UI exploration and scaffolding.
    Analyze the following brainstorm notes and output a rigorous structured analysis based on the exact JSON schema requested.
    The target vibe coding platform the user will use is [{req.target_platform}]. 
    The 'vibe_coding_pipeline' should be a PRELIMINARY high-level table of contents. DO NOT generate the actual copy-paste prompts here. The exact granular prompts will be generated later during the Master Architect Blueprint phase. Just provide the sequential timeline of steps (e.g., Step 1: Database Setup, Step 2: Authentication, etc.).
    
    CRITICAL OUTLINE ENGINEERING RULES:
    1. Layered Construction: Chain your outline chronologically: Data Layer (Schema) -> API Layer (Endpoints) -> UI Layer (Components).
    2. Atomic Scoping: Steps MUST be vertical slices ("Single Responsibility"). Never combine massive features.
    
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
    5. All data points MUST be in a bulleted list (`*`) or a Markdown table.
    - Format `market_analysis` properly: Start each competitor/alternative section with a strict `### Target Competitor Name` header on its own line, followed by detailed bullet points underneath. Do NOT nest headers inside bullets!
    - Format `swot` properly: MUST be formatted in Markdown with bold categories (**Strengths:**) and double line breaks (`\n\n`) between each category.
    - Format `cost_benefit` properly: MUST be formatted in Markdown with two distinct headers (**Benefits** and **Costs**), and the points under each must be formatted as a bulleted list.
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

async def generate_architect_report(project_id: int, source_texts: str, platform: str, designer: str, app_name: str, app_purpose: str, budget_constraints: str, ai_integration: str, security_auth: str, build_environment: str):
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
    
        Analyze the raw notes below and output a strict structural outline. 
        The outline must be restricted to logical MVP feature building steps following 2026 Vibe Coding best practices (Intent -> Plan -> Generate -> Vibe-Check). Include chronological layer-building: Data schema first -> API next -> UI/Frontend components last.
        
        CRITICAL RULES FOR QUALITY OVER QUANTITY:
        - Build Environment Rule: You must tailor your steps to the "{build_environment}" classification. If it is "Greenfield (New)", provide foundational setup instructions (e.g., 'Initialize Next.js project', 'Setup base database schemas'). If it is "Brownfield (Existing)", you MUST assume the core project already exists. Focus your outline exclusively on safely integrating new features into the existing architecture, requiring adapter patterns, non-breaking schema migrations, and heavy regression-testing rules.
        - Do NOT ignore Agentic Memory. The very first step MUST be establishing `.cursorrules` or `AGENTS.md` context files with strict guardrails ("Never edit >3 files without confirmed plan. Always run tsc").
        - Build Atomically (Chain Prompting). Break down the architecture into micro-steps. Do not try to build an entire feature in one step. An ideal project should have between 20 to 50 highly granular, atomic steps.
        - Artifact Locking: Dictate explicitly where the user should execute a "Pre-Flight Impact Analysis" to force the agent to write an `implementation_plan.md` detailing "Dependency Risks" and "Verification Strategy" before risking regression on core components.
        - Chapter titles MUST be written in extremely simple, concise layman's terms (e.g., "User Login Screen", "Database Setup", "Save Button Logic"). Do not use overly technical jargon or long run-on sentences for the title.
        - Because you know the Budget/Hosting Constraints: During the infrastructure architecture phase, you MUST explicitly recommend whether they should use platforms like Render, Vercel, Supabase, Pinecone, or other alternatives based exactly on their Budget ({budget_constraints}) and Target Audience. Explain the tradeoff briefly.
        - Because you know the AI Role & Functionality: You MUST explicitly recommend which specific AI foundation models (e.g., Claude 3.5 Sonnet, Gemini 2.5 Flash/Pro, GPT-4o, Llama 3) would be mathematically ideal for these isolated tasks. If multiple AI models are needed, explain which AI is most efficient at each specific task.
    
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
        markdown_content += "## Table of Contents\n\n"
    
        # Generate TOC
        for idx, chapter in enumerate(chapters):
            # Generate safe anchor
            anchor = chapter.lower().replace(' ', '-').replace('.', '').replace(':', '')
            markdown_content += f"- [ ] [Step {idx + 1}: {chapter}](#step-{idx+1}-{anchor})\n"
        
        markdown_content += "\n---\n\n"
    
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
                        model='text-embedding-004',
                        contents=query_text
                    )
                    vector = res.embeddings[0].values
                    pinecone_query = pinecone_index.query(vector=vector, top_k=3, namespace="synapseip_notes")
                    
                    relevant_ids = [int(match['id']) for match in pinecone_query.get('matches', []) if match['id'].isdigit()]
                    if relevant_ids:
                        db_sources = db.query(GeminiSource).filter(GeminiSource.id.in_(relevant_ids)).all()
                        relevant_sources_text = "\n\n".join([f"RAW SOURCE: {s.title}\n{s.content}" for s in db_sources])
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
            1. Explain why this feature is needed and its calculation/logic.
            2. Provide exactly what to expect if it works or fails.
            3. YOU MUST output the exact Vibe Coding prompt inside a markdown code block so the user can easily copy and paste it into their IDE.
            
            STRICT FORMATTING TEMPLATE YOU MUST FOLLOW:
            
            <div class="manual-action-alert">
            <h4>⚠️ Manual Developer Action Required</h4>
            <ul>
                <li>[If the developer MUST do something manually outside the IDE before writing code (e.g., signing up for an API account, generating an API key, creating a Supabase project, or configuring a third-party dashboard), list the exact steps here as bullet points.]</li>
            </ul>
            </div>
            *(NOTE: Only include the above HTML block if manual actions are actually required. If no manual account setup or configuration is required, omit it completely.)*
            
            **Why:** [Layman explanation of why this step is necessary]
            
            **Expectation:** [What should happen if this succeeds]
            
            **Watch Out:** [What could go wrong or common errors]
            
            **Copy & Paste this into your IDE:**
            ```text
            [System Context]
            We are building a {platform} application for {app_name}.
            
            [Objective]
            Implement the logic for {chapter_title}.
            
            [Artifact Locking & Pre-Flight]
            Before writing ANY code, please perform an Impact Analysis. Review existing files to understand the current context.
            Output an `implementation_plan.md` detailing:
            1. Which files will be modified.
            2. The exact API calls you intend to use.
            DO NOT generate code until I explicitly approve the implementation plan.
            
            [Execution Constraints]
            - Follow the existing exact style tokens.
            - The UI MUST be beautifully modern.
            - Write a unit test for validation logic BEFORE implementing the component (Test-Driven Vibe Development).
            ```
            
            Strict Formatting Rules:
            1. DO NOT output a `#` or `##` header for the chapter title itself. The system will handle the chapter title. Just output the content.
            2. All data points outside the text block MUST be in a bulleted list (`*`) or a Markdown table.
        
            [PREVIOUS ARCHITECTURAL DECISIONS (Maintain Strict Consistency with these)]:
            {rolling_architecture_context}
            
            [GLOBAL CONTEXT (Project Abstract & Themes)]:
            {source_texts}
            
            [DEEP-DIVE CONTEXT (Raw Notes retrieved via Vector Search for '{chapter_title}')]:
            {relevant_sources_text}
            """
        
            try:
                chap_res = await gemini_client.aio.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=chapter_prompt
                )
                await log_token_usage(db, "Architect Generation", "gemini-2.5-flash", chap_res, project_id=project_id)
                anchor = chapter_title.lower().replace(' ', '-').replace('.', '').replace(':', '')
                markdown_content += f"<a id='step-{i+1}-{anchor}'></a>\n"
                markdown_content += f"## <label style='cursor:pointer; display:inline-flex; align-items:center; gap:12px;'><input type='checkbox' class='blueprint-checkbox vibe-checkbox' data-idx='{i}'> Step {i+1}: {chapter_title}</label>\n\n"
                markdown_content += f"{chap_res.text}\n\n---\n\n"
                
                # Consistency Subagent Evaluation
                try:
                    consistency_prompt = f"""
                    You are a system architecture consistency tracker. 
                    Analyze the following newly generated architectural step and extract any concrete architectural decisions, database schema additions, file structure modifications, or library dependencies that were established.
                    Keep it extremely concise (bullet points). If no major technical decisions were made, output "None".
                    
                    Step Content:
                    {chap_res.text}
                    """
                    consist_res = await gemini_client.aio.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=consistency_prompt
                    )
                    await log_token_usage(db, "Consistency Subagent", "gemini-2.5-flash", consist_res, project_id=project_id)
                    
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
    
    results = db.query(
        func.date_trunc('hour', TokenLog.timestamp).label("hour_group"),
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
     .group_by(func.date_trunc('hour', TokenLog.timestamp), TokenLog.action, Project.name, User.id, User.username)\
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

@app.post("/api/architect/start")
async def start_architect(req: AnalyzeRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or not owned by user")
        
    themes = db.query(ProjectTheme).filter(ProjectTheme.project_id == project.id).all()
    
    if not themes:
        # Fallback to raw sources if no themes exist yet (e.g. legacy data)
        sources = db.query(GeminiSource).filter(GeminiSource.project_id == project.id).all()
        if not sources:
            raise HTTPException(status_code=400, detail="No sources available. Sync some datanodes first.")
        memories = []
        for s in sources:
            if s.short_memory:
                memories.append(f"Source: {s.title}\nSummary: {s.short_memory}")
            else:
                memories.append(f"Source: {s.title}\nContent snippet: {s.content[:500]}...")
        combined_text = "\n\n---\n\n".join(memories)
    else:
        combined_text = "\n\n---\n\n".join([f"THEME: {t.theme_name}\n{t.content}" for t in themes])
        
    combined_text = truncate_context_for_tokens(combined_text)
    background_tasks.add_task(generate_architect_report, req.project_id, combined_text, req.target_platform, req.designer_name, req.app_name, req.app_purpose, req.budget_constraints, req.ai_integration, req.security_auth, req.build_environment)
    
    return {"status": "started", "message": "Architect pipeline initiated."}

# To run: uvicorn main:app --reload
