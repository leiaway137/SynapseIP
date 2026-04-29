import re
import json
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://neondb_owner:npg_dyko7SLcmeO8@ep-tiny-queen-an1qw5a7.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProjectIntel(Base):
    __tablename__ = 'project_intel'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    report_data = Column(Text)
    timestamp = Column(String)

db = SessionLocal()
report = db.query(ProjectIntel).order_by(ProjectIntel.id.desc()).first()
if report:
    data = json.loads(report.report_data)
    
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
    print("Successfully patched Intel Report ID:", report.id)
else:
    print("No report found.")
