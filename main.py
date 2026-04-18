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
from passlib.context import CryptContext
from jose import JWTError, jwt

# Initialize environment & LLM Client
load_dotenv()
try:
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except Exception:
    gemini_client = None
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

# ---------------------------------------------------------
# Chroma Vector DB Setup
# ---------------------------------------------------------
try:
    import chromadb
    import chromadb.utils.embedding_functions as embedding_functions

    chroma_client = chromadb.PersistentClient(path="./chroma_data")
    google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
        api_key=os.getenv("GEMINI_API_KEY"),
        task_type="RETRIEVAL_DOCUMENT"
    )
    collection = chroma_client.get_or_create_collection(
        name="synapseip_notes",
        embedding_function=google_ef
    )
    print("🧠 ChromaDB Initialized & Ready")
except Exception as e:
    print(f"⚠️ Warning: ChromaDB initialization failed: {e}")
    collection = None

def index_in_chroma(document_id: str, title: str, text: str):
    """Synchronous background task to hit Gemini Embedding API and store directly into Chroma."""
    if collection is None: return
    try:
        collection.add(
            ids=[document_id],
            documents=[text],
            metadatas=[{"title": title}]
        )
        print(f"✅ ChromaDB Indexed: [{document_id}]")
    except Exception as e:
        print(f"❌ ChromaDB Indexing Error: {e}")

# ---------------------------------------------------------
# Security Setup
# ---------------------------------------------------------
SECRET_KEY = "synapse_super_secret_matrix"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ---------------------------------------------------------
# Database Setup Setup
# ---------------------------------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./gemini_sources.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class GeminiSource(Base):
    __tablename__ = "gemini_sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_url = Column(String, index=True)
    processed = Column(Boolean, default=False)

class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    report_data = Column(Text) # Stored serialized JSON
    timestamp = Column(DateTime, default=datetime.utcnow)

class TokenLog(Base):
    __tablename__ = "token_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
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
    vibe_coding_pipeline: list[PipelineStep] = Field(description="Sequential timeline of implementation prompts.")

class AnalyzeRequest(BaseModel):
    target_platform: str = "Antigravity"
    designer_name: str = ""
    app_name: str = ""
    app_purpose: str = ""

class BulkDeleteRequest(BaseModel):
    source_ids: list[int]

class OutlineSchema(BaseModel):
    chapters: list[str]

class ChatMessage(BaseModel):
    role: str
    content: str

class OnboardingRequest(BaseModel):
    history: list[ChatMessage]

class OnboardingResponseSchema(BaseModel):
    message: str = Field(description="Your conversational reply or evaluation.")
    is_complete: bool = Field(description="True if Designer Name, App Name, and Core Purpose are confidently identified. False otherwise.")
    designer_name: Optional[str] = Field(description="Extracted designer name.", default=None)
    app_name: Optional[str] = Field(description="Extracted app name.", default=None)
    core_purpose: Optional[str] = Field(description="Extracted core purpose.", default=None)

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

# ---------------------------------------------------------
# Security Helpers
# ---------------------------------------------------------
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

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
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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

async def log_token_usage(db: Session, action: str, model: str, res):
    if hasattr(res, 'usage_metadata') and res.usage_metadata:
        in_toks = getattr(res.usage_metadata, 'prompt_token_count', 0) or 0
        out_toks = getattr(res.usage_metadata, 'candidates_token_count', 0) or 0
        
        cost = 0.0
        if "flash" in model.lower():
            cost = (in_toks / 1000000.0) * 0.075 + (out_toks / 1000000.0) * 0.30
        elif "pro" in model.lower():
            cost = (in_toks / 1000000.0) * 1.25 + (out_toks / 1000000.0) * 5.00
            
        record = TokenLog(
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

# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """Serve the NotebookLM-style frontend interaction page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/sources")
def get_sources(response: Response, db: Session = Depends(get_db)):
    """Return all ingested sources ordered chronologically."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    sources = db.query(GeminiSource).order_by(GeminiSource.timestamp.asc()).all()
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
    """Accepts JSON and saves it to the DB instantly."""
    
    db_source = GeminiSource(
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
    background_tasks.add_task(index_in_chroma, str(db_source.id), db_source.title, db_source.content)
    
    total = db.query(GeminiSource).count()
    
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
    if collection is None:
        raise HTTPException(status_code=500, detail="Chroma DB is natively disabled.")
    
    try:
        results = collection.query(
            query_texts=[q],
            n_results=5  # Top 5 most semantically relevant memories
        )
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/onboarding")
async def onboarding_chat(req: OnboardingRequest, db: Session = Depends(get_db)):
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini SDK improperly configured. Check API key.")
        
    sources = db.query(GeminiSource).order_by(GeminiSource.timestamp.asc()).all()
    context_text = "\n\n".join([f"Source: {s.title}\n{s.content}" for s in sources]) if sources else "No sources provided yet."
    
    history_str = "\n".join([f"{msg.role.upper()}: {msg.content}" for msg in req.history])
    if not req.history:
        history_str = "(Conversation just started. The user is waiting.)"
    
    prompt = f"""
    You are the SynapseIP Onboarding Agent. Your mission is to chat with the user to extract 3 required parameters: Designer Name, App Name, and Core Purpose.
    If the conversation just started, enthusiastically welcome them, quickly evaluate the summary of their brainstorm sources (below) in a sentence or two, and ask what they want to build and who is designing it.
    If they've answered some but not all, ask probing questions for the remainder. 
    Once all 3 fields are clearly established, set is_complete=True and output a concluding launch message.
    
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
        await log_token_usage(db, "Onboarding Chat", "gemini-2.5-flash", res)
        return json.loads(res.text)
    except Exception as e:
        print("Onboarding chat error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_sources(req: AnalyzeRequest, db: Session = Depends(get_db)):
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini SDK improperly configured. Check API key.")
        
    sources = db.query(GeminiSource).order_by(GeminiSource.timestamp.asc()).all()
    if not sources:
        raise HTTPException(status_code=400, detail="No sources found to analyze.")
        
    context_text = "\n\n".join([f"Source: {s.title}\n{s.content}" for s in sources])
    
    prompt = f"""
    You are an elite Software Architect and Business Analyst.
    Project Name: {req.app_name}
    Designer Name: {req.designer_name}
    Core Purpose: {req.app_purpose}
    
    Your priority is to ensure the resulting MVP is not just technically sound, but features a beautiful, highly usable, and modern User Interface for human users. Start the pipeline with UI exploration and scaffolding.
    Analyze the following brainstorm notes and output a rigorous structured analysis based on the exact JSON schema requested.
    The target vibe coding platform the user will use is [{req.target_platform}]. 
    Please tailor the 'vibe_coding_pipeline' prompts specifically for this platform so they can copy paste them directly into the tool.
    
    Strict Formatting Rules:
    1. Use `#` ONLY for the Title of the entire document.
    2. Use `##` for Chapter Titles / Core Categories.
    3. Use `###` for all Sub-headers. 
    4. Use `---` (horizontal rules) to separate distinct logic blocks.
    5. All data points MUST be in a bulleted list (`*`) or a Markdown table.
    6. DO NOT use bolding (`**`) for headers; use the appropriate `#` tag.
    
    CRITICAL for market_analysis: Format as an unordered bullet list and ALWAYS use `### Category/Competitor Name` at the start of each section instead of bolding it.
    
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
        await log_token_usage(db, "Analyze Blueprint", "gemini-2.5-flash", response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    generated_json = response.text
    
    # Save generic generated report
    new_report = GeneratedReport(report_data=generated_json, timestamp=datetime.utcnow())
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

async def generate_architect_report(source_texts: str, platform: str, designer: str, app_name: str, app_purpose: str):
    db = SessionLocal()
    try:
        await manager.broadcast(json.dumps({"type": "progress", "message": "Initializing Architect Framework...", "progress": 10}))
    
        outline_prompt = f"""
        You are an expert technical and business architect defining an MVP build process for a new app.
        App Name: {app_name}
        App Purpose: {app_purpose}
        Designer: {designer}
        Target Vibe Coding Platform: {platform}
    
        Analyze the raw notes below and output a strict structural outline. 
        The outline must be restricted to logical MVP feature building steps. CRITICAL: Do NOT ignore the UI. The first foundational steps MUST involve UI Exploration, evaluating standard layouts, and prompting the vibe coder to generate frontend scaffolding/mockups to ensure the MVP is immediately usable by humans.
        Be concise.
    
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
            await log_token_usage(db, "Architect Outlining", "gemini-2.5-flash", outline_res)
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
                await log_token_usage(db, f"Architect Step {i+1}", "gemini-2.5-flash", chap_res)
                markdown_content += f"## {chapter_title}\n\n"
                markdown_content += f"{chap_res.text}\n\n---\n\n"
            except Exception as e:
                print(f"Skipping chapter {chapter_title} due to error: {e}")
        
            # THROTTLE FOR 429
            await asyncio.sleep(4)

        os.makedirs('static/reports', exist_ok=True)
        file_path = "static/reports/SynapseIP_Master_Plan.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
    
        await manager.broadcast(json.dumps({
            "type": "architect_complete",
            "message": "Markdown MVP Document compiled and saved.",
            "progress": 100,
            "download_url": f"/{file_path}"
        }))
    
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

@app.post("/api/architect/start")
async def start_architect(req: AnalyzeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    sources = db.query(GeminiSource).all()
    if not sources:
        raise HTTPException(status_code=400, detail="No sources available. Sync some datanodes first.")
        
    combined_text = "\n\n---\n\n".join([f"TITLE: {s.title}\n{s.content}" for s in sources])
    background_tasks.add_task(generate_architect_report, combined_text, req.target_platform, req.designer_name, req.app_name, req.app_purpose)
    
    return {"status": "started", "message": "Architect pipeline initiated."}

# To run: uvicorn main:app --reload
