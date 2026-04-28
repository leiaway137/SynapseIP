import os
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google import genai
from main import FrameworkTemplate

DATA_DIR = os.environ.get("DATA_DIR", ".")
target_db_path = os.path.join(DATA_DIR, 'gemini_sources.db')
engine = create_engine(f"sqlite:///{target_db_path}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get('GEMINI_API_KEY')

client = genai.Client(api_key=api_key)

async def generate_template(platform_name):
    print(f"Generating expert template for: {platform_name}...")
    prompt = f"""
    You are an elite, principal software architect with 20 years of experience.
    Your task is to define the golden standard `PROJECT_RULES.md` for a {platform_name} project.
    
    This template will be used as a foundation by junior AI developers. You MUST define the absolute best practices for this framework.
    
    The document MUST contain ALL of the following sections. Use standard, universally accepted best practices:
    
    1. **Tech Stack Version Lock**: List the recommended major dependencies for {platform_name} (e.g., specific framework versions, UI libraries like Tailwind/Shadcn, State management).
    2. **Project Directory Structure**: Output a complete ASCII folder tree showing exactly where every type of file should be placed (components, pages/screens, API, utils, types, styles).
    3. **Component Modularity (150-Line Rule)**: Mandate that no component exceed 150 lines. Explain how to break them down in this specific framework.
    4. **Data Fetching Strategy**: Explicitly define the best practice for data fetching in {platform_name} (e.g., React Query, Server Components, RTK Query).
    5. **State Management Protocol**: Define the single source of truth for state. Specify the recommended library (e.g., Zustand) and strict rules for its usage.
    6. **UI/Styling Constraints**: Define how styling should be applied (e.g., Tailwind classes, StyleSheet objects) and where design tokens should be stored. (Leave placeholders for specific colors).
    7. **Testing Requirements**: Specify the recommended test runner and testing strategy.
    8. **API & Data Conventions**: Define naming conventions (e.g., camelCase vs snake_case).
    9. **Environment Variables Template**: Provide a standard `.env.example` block.
    10. **Agent Safety Guardrails**: General rules for code modifications.
    
    Output ONLY the text meant to go inside the `PROJECT_RULES.md` file. Do not wrap it in markdown fences if possible, just pure text.
    """
    
    res = await client.aio.models.generate_content(
        model='gemini-2.5-pro',
        contents=prompt
    )
    text = res.text.strip()
    if text.startswith("```markdown"):
        text = text[11:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
        
    return text.strip()

async def main():
    db = SessionLocal()
    platforms = ["Next.js (App Router)", "React Native (Expo)", "Vue/Nuxt"]
    
    for p in platforms:
        existing = db.query(FrameworkTemplate).filter(FrameworkTemplate.normalized_name == p).first()
        if existing:
            print(f"Template for {p} already exists. Skipping.")
            continue
            
        content = await generate_template(p)
        new_template = FrameworkTemplate(normalized_name=p, content=content)
        db.add(new_template)
        db.commit()
        print(f"Saved template for {p}!")
        
    db.close()
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(main())
