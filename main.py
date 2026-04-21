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
            model='text-embedding-004',
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
            
        prompt = f"Condense the following brainstorm note into an extremely concise 2-3 sentence executive summary capturing the core intent/mechanic:\n\n{source.content}"
        
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
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
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'gemini_sources.db')}"

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
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

class ProjectResponse(BaseModel):
    id: int
    name: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class PipelineStep(BaseModel):
    prompt_text: str = Field(description="The exact text to copy-paste into Antigravity/Cursor/Claude.")
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
    standout_features: list[str] = []
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
    is_complete: bool = Field(description="True if Designer Name, App Name, Core Purpose, Target Audience, App Type, Budget/Hosting Constraints, and Standout Features are confidently identified. False otherwise.")
    designer_name: Optional[str] = Field(description="Extracted designer name.", default=None)
    app_name: Optional[str] = Field(description="Extracted app name.", default=None)
    core_purpose: Optional[str] = Field(description="Extracted core purpose.", default=None)
    target_audience: Optional[str] = Field(description="Extracted target audience and target region/location.", default=None)
    app_type: Optional[str] = Field(description="Must be exactly either 'Personal' or 'Commercial'.", default=None)
    budget_constraints: Optional[str] = Field(description="Extracted budget and hosting constraints (e.g. 'Free Tier Only', 'Paid Enterprise', 'Undecided').", default=None)
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
            unprocessed = db.query(GeminiSource).filter(GeminiSource.processed == False).order_by(GeminiSource.timestamp.asc()).first()
            if not unprocessed:
                db.close()
                await asyncio.sleep(2)
                continue
            
            # Detach payload from DB transaction to prevent SQLite full-table lock
            target_id = unprocessed.id
            raw_title = unprocessed.title
            raw_content = unprocessed.content
            db.close()

            smart_title = raw_title
            if gemini_client:
                try:
                    title_prompt = f"You are a neat summarization bot. Create a professional, catchy, 3 to 6 word title summarizing this interaction. Do not use quotes, labels, or generic prefixes. Only return the title itself.\n\nText: {raw_content[:1500]}"
                    # Run this synchronously in the threadpool if possible to not block event loop, or just let it block since it's a daemon
                    res = gemini_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=title_prompt
                    )
                    smart_title = res.text.strip().strip('"').strip("'")
                    if len(smart_title) > 100:
                        smart_title = smart_title[:100]
                except Exception as e:
                    print("Background processing title summarization failed.", e)
            
            # Reopen connection for swift instantaneous commit
            db2 = SessionLocal()
            finished_item = db2.query(GeminiSource).filter(GeminiSource.id == target_id).first()
            if finished_item:
                finished_item.title = smart_title
                finished_item.processed = True
                db2.commit()
            db2.close()

            # Notify UI to update instantly
            await manager.broadcast("new_source")
        except Exception as e:
            print("Error in background processor:", e)
        await asyncio.sleep(2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the database tables on startup
    Base.metadata.create_all(bind=engine)
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

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
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
    return {"id": current_user.id, "username": current_user.username}

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

@app.get("/api/projects")
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.timestamp.desc()).all()

@app.post("/api/projects", response_model=ProjectResponse)
def create_project(req: ProjectCreate, db: Session = Depends(get_db)):
    p = Project(user_id=1, name=req.name)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@app.get("/api/projects/{project_id}/sources")
def get_project_sources(project_id: int, response: Response, db: Session = Depends(get_db)):
    """Return all ingested sources for a specific project."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    sources = db.query(GeminiSource).filter(GeminiSource.project_id == project_id).order_by(GeminiSource.timestamp.asc()).all()
    return sources

@app.get("/api/projects/{project_id}/documents")
def get_project_documents(project_id: int, db: Session = Depends(get_db)):
    """Returns lists of intelligence reports and architecture blueprints for this project."""
    reports = db.query(GeneratedReport).filter(GeneratedReport.project_id == project_id).order_by(GeneratedReport.timestamp.desc()).all()
    blueprints = db.query(ArchitectBlueprint).filter(ArchitectBlueprint.project_id == project_id).order_by(ArchitectBlueprint.timestamp.desc()).all()
    
    return {
        "intelligence": [{"id": r.id, "timestamp": r.timestamp, "data": json.loads(r.report_data)} for r in reports],
        "blueprints": [{"id": b.id, "timestamp": b.timestamp, "data": b.blueprint_data} for b in blueprints]
    }

@app.get("/api/sources")
def get_sources(response: Response, db: Session = Depends(get_db)):
    # Fallback for old requests
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    active_project = db.query(Project).order_by(Project.timestamp.desc()).first()
    if not active_project:
        return []
    sources = db.query(GeminiSource).filter(GeminiSource.project_id == active_project.id).order_by(GeminiSource.timestamp.asc()).all()
    return sources

@app.delete("/api/sources/{source_id}")
async def delete_source(source_id: int, db: Session = Depends(get_db)):
    db_source = db.query(GeminiSource).filter(GeminiSource.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(db_source)
    db.commit()
    await manager.broadcast(json.dumps({"type": "sources_deleted"}))
    return {"status": "success"}

@app.post("/api/sources/bulk-delete")
async def bulk_delete_sources(req: BulkDeleteRequest, db: Session = Depends(get_db)):
    if not req.source_ids:
        return {"status": "success", "deleted_count": 0}
        
    db.query(GeminiSource).filter(GeminiSource.id.in_(req.source_ids)).delete(synchronize_session=False)
    db.commit()
    await manager.broadcast(json.dumps({"type": "sources_deleted"}))
    return {"status": "success", "deleted_count": len(req.source_ids)}

@app.post("/ingest", response_model=SourceResponse)
async def ingest_source(source: SourceCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Accepts JSON from Chrome Extension and saves it to the most recently created Project."""
    
    active_project = db.query(Project).order_by(Project.timestamp.desc()).first()
    if not active_project:
        active_project = Project(user_id=1, name="Default Project")
        db.add(active_project)
        db.commit()
        db.refresh(active_project)

    db_source = GeminiSource(
        user_id=1,
        project_id=active_project.id,
        title=source.title, # Respecting chronological numbering extracted by Chrome sub-agent
        content=source.content,
        source_url=source.source_url,
        timestamp=datetime.utcnow(),
        processed=False
    )
    db.add(db_source)
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
async def semantic_search(q: str):
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
async def followup_chat(req: FollowupRequest, db: Session = Depends(get_db)):
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini SDK improperly configured.")
    
    # Identify the related Intelligence Report
    report = db.query(GeneratedReport).filter(GeneratedReport.project_id == req.project_id).order_by(GeneratedReport.timestamp.desc()).first()
    
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
        return {"message": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/onboarding")
async def onboarding_chat(req: OnboardingRequest, db: Session = Depends(get_db)):
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini SDK improperly configured. Check API key.")
    project = db.query(Project).filter(Project.id == req.project_id).first()
    project_name = project.name if project else "SynapseIP Target App"

    sources = db.query(GeminiSource).filter(GeminiSource.project_id == req.project_id).order_by(GeminiSource.timestamp.asc()).all()
    
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
    
    history_str = "\n".join([f"{msg.role.upper()}: {msg.content}" for msg in req.history])
    if not req.history:
        history_str = "(Conversation just started. The user is waiting.)"
    
    prompt = f"""
    You are the SynapseIP Onboarding Agent. Your mission is to chat with the user to extract 7 required parameters: Designer Name, App Name, Core Purpose, Target Audience (with location/region), App Type ('Personal' or 'Commercial'), Budget/Subscription Tier (e.g. Free Tier prototyping vs Paid Enterprise), and Standout Features.
    CRITICAL OVERRIDE: The user has ALREADY officially designated the App Name as "{project_name}". 
    You MUST NOT ask the user what the App Name is, and you MUST EXACTLY output "{project_name}" for the App Name parameter.
    
    If the conversation just started, enthusiastically welcome them, quickly evaluate the summary of their brainstorm sources (below) in a sentence or two, and elegantly ask who is designing it, what its core purpose is, and who the target audience is (including their region, like USA vs China).
    If they've answered some but not all, ask probing but friendly questions for the remainder. 
    Crucially, determine if the app is purely for "Personal" utility/efficiency or "Commercial" mass market, and ask what their budget constraints are for hosting/database infrastructure (do they strictly want free-tiers or are they willing to pay?). Finally, ask what core features make it stand out.
    Once ALL 7 required parameters are clearly established, set is_complete=True and output a concluding launch message.
    
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
        return json.loads(res.text)
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
async def analyze_sources(req: AnalyzeRequest, db: Session = Depends(get_db)):
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini SDK improperly configured. Check API key.")
        
    sources = db.query(GeminiSource).filter(GeminiSource.project_id == req.project_id).order_by(GeminiSource.timestamp.asc()).all()
    if not sources:
        raise HTTPException(status_code=400, detail="No sources found to analyze.")
        
    context_text = "\n\n".join([f"Source: {s.title}\n{s.content}" for s in sources])
    
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
    Standout Features: {", ".join(req.standout_features)}
    
    Your priority is to ensure the resulting MVP is not just technically sound, but features a beautiful, highly usable, and modern User Interface for human users. Start the pipeline with UI exploration and scaffolding.
    Analyze the following brainstorm notes and output a rigorous structured analysis based on the exact JSON schema requested.
    The target vibe coding platform the user will use is [{req.target_platform}]. 
    Please tailor the 'vibe_coding_pipeline' prompts specifically for this platform so they can copy paste them directly into their agentic IDE.
    
    CRITICAL VIBE-CODING PROMPT ENGINEERING RULES (2026 Standards):
    1. The "Vibe Core" Workflow: Your prompts must dictate OUTCOMES (Intent), ask the agent to PLAN before coding, and include explicit VIBE-CHECKS ("verify this handles edge cases").
    2. Layered Construction: Do not ask for a full app in one prompt. Chain your prompts chronologically: Data Layer (Schema) -> API Layer (Endpoints) -> UI Layer (Components).
    3. Agentic Memory: Explicitly instruct the agent to create a `.cursorrules` or `AGENTS.md` file in the very first prompt to lock in the tech stack (e.g. Tailwind, React).
    4. Test-Driven Vibe Development (TDVD): Prompts should periodically instruct the agent to write tests FIRST, and then write the code to make those tests pass.
    
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
        await log_token_usage(db, "Analyze Blueprint", "gemini-2.5-flash", response, project_id=req.project_id)
        generated_json = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Save generic generated report
    new_report = GeneratedReport(project_id=req.project_id, report_data=generated_json, timestamp=datetime.utcnow())
    db.add(new_report)
    db.commit()
    
    # Notify UI
    await manager.broadcast("new_report")
    
    return json.loads(generated_json)
    
@app.get("/api/reports/latest")
def get_latest_report(db: Session = Depends(get_db)):
    report = db.query(GeneratedReport).order_by(GeneratedReport.timestamp.desc()).first()
    if report:
        return json.loads(report.report_data)
    return None

async def generate_architect_report(project_id: int, source_texts: str, platform: str, designer: str, app_name: str, app_purpose: str, budget_constraints: str):
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
    
        Analyze the raw notes below and output a strict structural outline. 
        The outline must be restricted to logical MVP feature building steps following 2026 Vibe Coding best practices (Intent -> Plan -> Generate -> Vibe-Check). Include chronological layer-building: Data schema first -> API next -> UI/Frontend components last.
        
        CRITICAL RULES FOR QUALITY OVER QUANTITY:
        - Do NOT ignore Agentic Memory. The very first step MUST be establishing `.cursorrules` or `AGENTS.md` context files.
        - Do NOT force a specific page count or arbitrary length. 
        - Include only the absolute essential elements needed to realistically build this project. 
        - Because you know the Budget/Hosting Constraints: During the infrastructure architecture phase, you MUST explicitly recommend whether they should use platforms like Render, Vercel, Supabase, Pinecone, or other alternatives based exactly on their Budget ({budget_constraints}) and Target Audience. Explain the tradeoff briefly.
        - Be highly precise. If this project only requires 3 core steps, output 3 steps. If it requires 15, output 15. Your goal is structural integrity, not fluff.
    
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
            chapters = outline_data.get('chapters', [])
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
            markdown_content += f"{idx + 1}. [{chapter}](#{anchor})\n"
        
        markdown_content += "\n---\n\n"
    
        total_chapters = len(chapters)
        await manager.broadcast(json.dumps({"type": "progress", "message": f"Outline verified. Writing {total_chapters} MVP feature iterations...", "progress": 20}))
    
        for i, chapter_title in enumerate(chapters):
            prog = 20 + int((i / total_chapters) * 70)
            await manager.broadcast(json.dumps({"type": "progress", "message": f"Drafting MVP Feature {i+1}: {chapter_title}...", "progress": prog}))
        
            chapter_prompt = f"""
            You are an expert technical architect documenting a specific MVP feature build step.
            App Name: {app_name}
            App Purpose: {app_purpose}
            Current Feature to Write: '{chapter_title}'
            Target Platform: {platform}
        
            Based ONLY on the following raw notes, write a highly concise, systematic, ordered step-by-step logic guide to build this specific feature.
        
            REQUIREMENTS:
            1. Explain why this feature is needed and its calculation/logic.
            2. Provide exactly what to expect if it works or fails.
            3. If this feature involves user interaction, YOU MUST explicitly include instructions for creating a beautiful, usable, modern UI component for it.
            4. Include a specific, detailed prompt that the designer can copy and paste directly into {platform} to build this.
            
            Strict Formatting Rules:
            1. Use `#` ONLY for the Title of the entire document.
            2. Use `##` for Chapter Titles.
            3. Use `###` for all Sub-headers. 
            4. Use `---` (horizontal rules) to separate distinct logic blocks.
            5. All data points MUST be in a bulleted list (`*`) or a Markdown table.
            6. DO NOT use bolding (`**`) for headers; use the appropriate `#` tag.
        
            Raw Notes:
            {source_texts}
            """
        
            try:
                chap_res = await gemini_client.aio.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=chapter_prompt
                )
                await log_token_usage(db, "Architect Generation", "gemini-2.5-flash", chap_res, project_id=project_id)
                markdown_content += f"## {chapter_title}\n\n"
                markdown_content += f"{chap_res.text}\n\n---\n\n"
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
def get_token_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    total_prompt = db.query(func.sum(TokenLog.prompt_tokens)).scalar() or 0
    total_comp = db.query(func.sum(TokenLog.completion_tokens)).scalar() or 0
    total_cost = db.query(func.sum(TokenLog.cost)).scalar() or 0.0
    
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
    
    results = db.query(
        func.date(TokenLog.timestamp).label("date"),
        TokenLog.action,
        Project.name.label("project_name"),
        User.id.label("user_id"),
        User.username.label("username"),
        func.sum(TokenLog.prompt_tokens + TokenLog.completion_tokens).label("tokens"),
        func.sum(TokenLog.cost).label("cost")
    ).outerjoin(Project, TokenLog.project_id == Project.id)\
     .outerjoin(User, TokenLog.user_id == User.id)\
     .group_by(func.date(TokenLog.timestamp), TokenLog.action, Project.name, User.id, User.username).all()
     
    breakdown = []
    for r in results:
        breakdown.append({
            "date": r.date or "N/A",
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
async def start_architect(req: AnalyzeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    sources = db.query(GeminiSource).all()
    if not sources:
        raise HTTPException(status_code=400, detail="No sources available. Sync some datanodes first.")
        
    combined_text = "\n\n---\n\n".join([f"TITLE: {s.title}\n{s.content}" for s in sources])
    background_tasks.add_task(generate_architect_report, req.project_id, combined_text, req.target_platform, req.designer_name, req.app_name, req.app_purpose, req.budget_constraints)
    
    return {"status": "started", "message": "Architect pipeline initiated."}

# To run: uvicorn main:app --reload
