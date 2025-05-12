
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import os
import logging
import uuid
from datetime import datetime
import json
import google.generativeai as genai
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
try:
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'website_builder')]
    logger.info("Connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Create the main app
app = FastAPI(title="AI Website Builder API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class WebsiteIdea(BaseModel):
    idea: str
    api_key: str

class WebsiteAnalysis(BaseModel):
    idea: str
    analysis: dict
    api_key: str

class WebsitePlan(BaseModel):
    idea: str
    plan: dict
    api_key: str

class WebsiteFile(BaseModel):
    name: str
    content: str
    file_type: str

class WebsiteTestRequest(BaseModel):
    files: List[WebsiteFile]
    api_key: str

class DeploymentRequest(BaseModel):
    files: List[WebsiteFile]
    test_results: dict
    api_key: str

# Gemini API integration
def get_gemini_client(api_key: str):
    try:
        genai.configure(api_key=api_key)
        return genai
    except Exception as e:
        logger.error(f"Failed to initialize Gemini: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid API key or Gemini API error: {str(e)}")

# Helper function to run Gemini model
async def generate_with_gemini(prompt: str, api_key: str, model_name: str = "gemini-pro"):
    gemini = get_gemini_client(api_key)
    try:
        model = gemini.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

# Routes
@api_router.get("/")
async def root():
    return {"message": "AI Website Builder API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/analyze-idea")
async def analyze_idea(request: WebsiteIdea):
    prompt = f"""
    You are an expert website analyzer. Analyze the following website idea and provide a detailed analysis.
    Website idea: {request.idea}
    
    Provide a JSON response with the following structure:
    {{
        "website_type": "Type of website (e-commerce, blog, portfolio, etc.)",
        "target_audience": "Description of target audience",
        "key_features": ["Feature 1", "Feature 2", "Feature 3"],
        "pages": ["Page 1", "Page 2", "Page 3"],
        "technologies": {{
            "frontend": ["Technology 1", "Technology 2"],
            "backend": ["Technology 1", "Technology 2"],
            "database": ["Technology 1"]
        }},
        "design_suggestions": {{
            "color_scheme": ["Color 1", "Color 2"],
            "layout": "Description of layout",
            "typography": "Font suggestions"
        }}
    }}
    
    Return ONLY the JSON with no additional text.
    """
    
    try:
        response_text = await generate_with_gemini(prompt, request.api_key)
        analysis = json.loads(response_text)
        
        # Save to database
        await db.website_analyses.insert_one({
            "id": str(uuid.uuid4()),
            "idea": request.idea,
            "analysis": analysis,
            "timestamp": datetime.utcnow()
        })
        
        return {"analysis": analysis}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON response from Gemini: {response_text}")
        raise HTTPException(status_code=500, detail="Failed to parse Gemini response")

@api_router.post("/plan-website")
async def plan_website(request: WebsiteAnalysis):
    analysis_json = json.dumps(request.analysis, indent=2)
    
    prompt = f"""
    You are an expert website planner. Create a detailed plan for building a website based on the following idea and analysis.
    
    Website idea: {request.idea}
    
    Analysis: {analysis_json}
    
    Provide a JSON response with the following structure:
    {{
        "file_structure": {{
            "directories": ["directory1", "directory2"],
            "files": [
                {{
                    "name": "file1.html",
                    "description": "Description of file1"
                }},
                {{
                    "name": "file2.css",
                    "description": "Description of file2"
                }}
            ]
        }},
        "implementation_steps": [
            "Step 1: Description",
            "Step 2: Description"
        ],
        "data_models": [
            {{
                "name": "Model name",
                "fields": ["field1", "field2"]
            }}
        ],
        "api_endpoints": [
            {{
                "path": "/api/endpoint",
                "method": "GET/POST",
                "description": "Description"
            }}
        ],
        "third_party_integrations": [
            {{
                "name": "Integration name",
                "purpose": "Purpose description"
            }}
        ]
    }}
    
    Return ONLY the JSON with no additional text.
    """
    
    try:
        response_text = await generate_with_gemini(prompt, request.api_key)
        plan = json.loads(response_text)
        
        # Save to database
        await db.website_plans.insert_one({
            "id": str(uuid.uuid4()),
            "idea": request.idea,
            "analysis": request.analysis,
            "plan": plan,
            "timestamp": datetime.utcnow()
        })
        
        return {"plan": plan}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON response from Gemini: {response_text}")
        raise HTTPException(status_code=500, detail="Failed to parse Gemini response")

@api_router.post("/generate-code")
async def generate_code(request: WebsitePlan):
    plan_json = json.dumps(request.plan, indent=2)
    
    # Generate a list of files to create based on the plan
    files_to_generate = []
    for file_info in request.plan.get("file_structure", {}).get("files", []):
        file_name = file_info.get("name", "")
        if file_name:
            files_to_generate.append(file_name)
    
    # Generate code for each file
    generated_files = []
    
    for file_name in files_to_generate[:5]:  # Limit to 5 files for demo
        file_extension = file_name.split('.')[-1].lower()
        file_type = "html" if file_extension == "html" else \
                    "css" if file_extension == "css" else \
                    "javascript" if file_extension in ["js", "jsx"] else \
                    "python" if file_extension in ["py"] else \
                    "other"
        
        prompt = f"""
        You are an expert website developer. Generate code for the following file based on the website idea and plan.
        
        Website idea: {request.idea}
        
        Plan: {plan_json}
        
        File to generate: {file_name}
        
        Generate complete, working code for this file. Make sure the code is properly formatted and follows best practices.
        Return ONLY the code with no additional text, explanations, or markdown formatting.
        """
        
        try:
            content = await generate_with_gemini(prompt, request.api_key)
            
            # Remove markdown code blocks if they exist
            if content.startswith("```") and content.endswith("```"):
                content = content[content.find('\n')+1:content.rfind('```')]
            
            generated_files.append(WebsiteFile(
                name=file_name,
                content=content,
                file_type=file_type
            ))
            
        except Exception as e:
            logger.error(f"Error generating code for {file_name}: {str(e)}")
    
    # Save to database
    await db.generated_code.insert_one({
        "id": str(uuid.uuid4()),
        "idea": request.idea,
        "plan": request.plan,
        "files": [file.dict() for file in generated_files],
        "timestamp": datetime.utcnow()
    })
    
    return {"files": generated_files}

@api_router.post("/test-website")
async def test_website(request: WebsiteTestRequest):
    files_json = json.dumps([file.dict() for file in request.files], indent=2)
    
    prompt = f"""
    You are an expert website tester. Test the following website files and provide a detailed test report.
    
    Files:
    {files_json}
    
    Provide a JSON response with the following structure:
    {{
        "test_summary": "Overall test summary",
        "tests": [
            {{
                "file": "filename.ext",
                "issues": ["Issue 1", "Issue 2"],
                "recommendations": ["Recommendation 1", "Recommendation 2"]
            }}
        ],
        "performance_score": 85,
        "accessibility_score": 90,
        "best_practices_score": 88
    }}
    
    Return ONLY the JSON with no additional text.
    """
    
    try:
        response_text = await generate_with_gemini(prompt, request.api_key)
        test_results = json.loads(response_text)
        
        # Save to database
        await db.test_results.insert_one({
            "id": str(uuid.uuid4()),
            "files": [file.dict() for file in request.files],
            "test_results": test_results,
            "timestamp": datetime.utcnow()
        })
        
        return {"test_results": test_results}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON response from Gemini: {response_text}")
        raise HTTPException(status_code=500, detail="Failed to parse Gemini response")

@api_router.post("/prepare-deployment")
async def prepare_deployment(request: DeploymentRequest):
    files_json = json.dumps([file.dict() for file in request.files], indent=2)
    test_results_json = json.dumps(request.test_results, indent=2)
    
    prompt = f"""
    You are an expert website deployer. Prepare the following website for deployment and provide deployment instructions.
    
    Files:
    {files_json}
    
    Test Results:
    {test_results_json}
    
    Provide a JSON response with the following structure:
    {{
        "deployment_summary": "Summary of deployment readiness",
        "deployment_platforms": ["Platform 1", "Platform 2"],
        "deployment_steps": [
            "Step 1: Description",
            "Step 2: Description"
        ],
        "required_environment_variables": ["VAR1", "VAR2"],
        "estimated_deployment_time": "X minutes",
        "post_deployment_tasks": ["Task 1", "Task 2"]
    }}
    
    Return ONLY the JSON with no additional text.
    """
    
    try:
        response_text = await generate_with_gemini(prompt, request.api_key)
        deployment_info = json.loads(response_text)
        
        # Save to database
        await db.deployment_info.insert_one({
            "id": str(uuid.uuid4()),
            "files": [file.dict() for file in request.files],
            "test_results": request.test_results,
            "deployment_info": deployment_info,
            "timestamp": datetime.utcnow()
        })
        
        # Normally, we would handle actual deployment here, but for this demo, we'll just return the info
        return {
            "deployment_info": deployment_info,
            "download_url": "/api/download-website",  # This would be a real URL in production
            "preview_url": None  # This would be a real preview URL in production
        }
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON response from Gemini: {response_text}")
        raise HTTPException(status_code=500, detail="Failed to parse Gemini response")

# Include the router in the main app
app.include_router(api_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("MongoDB connection closed")
      