#Gemini
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
import os
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
# --- Choose which LLM you want ---
# Option 1: Emergent AI
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Option 2: Gemini (Google Generative AI)
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Env vars
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "promptmaster_db")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Setup DB
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Setup FastAPI
app = FastAPI(title="PromptMaster API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS.split(",") if CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PromptOptimizeRequest(BaseModel):
    original_prompt: str
    category: str

class PromptOptimizeResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_prompt: str
    optimized_prompt: str
    category: str
    timestamp: str

class PromptHistory(PromptOptimizeResponse):
    pass

class Template(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    title: str
    template: str
    description: str

# --- Category Guidance ---
CATEGORY_GUIDANCE = {
    "text_summarization": "Focus on creating a prompt that generates clear, structured summaries with key points highlighted.",
    "code_generation": "Optimize for specific programming requirements, including language, functionality, error handling, and coding standards.",
    "content_creation": "Enhance for engaging content with clear structure, audience considerations, and SEO optimization.",
    "data_analysis": "Improve for comprehensive data analysis with insights, trend identification, and recommendations.",
    "chatbot_response": "Optimize for conversational AI with tone, context awareness, and user-friendly responses.",
    "creative_writing": "Enhance for storytelling with characters, plot structure, and vivid description.",
    "email_templates": "Optimize for professional communication with clear purpose, tone, and call-to-action.",
    "social_media": "Improve for engagement with hashtags, audience targeting, and shareability.",
    "academic_writing": "Enhance for scholarly writing with proper citations, tone, and methodology.",
    "marketing_copy": "Optimize for persuasive content with benefits, customer pain points, and conversion goals."
}

# --- Get LLM Response ---
async def generate_optimized_prompt(prompt_text: str):
    """Switch between Emergent AI and Gemini here."""
    if EMERGENT_LLM_KEY:
        # Use Emergent AI
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id="prompt_optimizer",
            system_message="You are an expert prompt optimizer. Return ONLY the optimized prompt."
        ).with_model("openai", "gpt-4o")

        user_message = UserMessage(text=prompt_text)
        response = await chat.send_message(user_message)

        # Extract text
        if isinstance(response, dict):
            return response.get("output", {}).get("text", "")
        return str(response)

    elif GEMINI_API_KEY:
        # Use Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt_text)
        return response.text

    else:
        raise Exception("No LLM key found. Please set EMERGENT_LLM_KEY or GEMINI_API_KEY")

# --- Routes ---
@app.get("/")
async def root():
    return {"message": "PromptMaster API is running"}

@app.post("/api/optimize", response_model=PromptOptimizeResponse)
async def optimize_prompt(request: PromptOptimizeRequest):
    try:
        guidance = CATEGORY_GUIDANCE.get(request.category, "Optimize this prompt for better AI results.")
        optimization_request = f"""
Category: {request.category.replace('_',' ').title()}
Special focus: {guidance}

Original prompt:
{request.original_prompt}
"""

        optimized_text = await generate_optimized_prompt(optimization_request)

        result = PromptOptimizeResponse(
            original_prompt=request.original_prompt,
            optimized_prompt=optimized_text.strip(),
            category=request.category,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        # Save history
        await db.prompt_history.insert_one(result.dict())
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing prompt: {str(e)}")

@app.get("/api/history", response_model=List[PromptHistory])
async def get_history(limit: int = 50):
    cursor = db.prompt_history.find().sort("timestamp", -1).limit(limit)
    history = await cursor.to_list(length=limit)
    return [PromptHistory(**item) for item in history]

@app.delete("/api/history/{prompt_id}")
async def delete_history_item(prompt_id: str):
    result = await db.prompt_history.delete_one({"id": prompt_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted successfully"}

@app.get("/api/categories")
async def get_categories():
    return {"categories": [{"id": k, "name": k.replace("_"," ").title()} for k in CATEGORY_GUIDANCE.keys()]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)






# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from motor.motor_asyncio import AsyncIOMotorClient
# from typing import List, Optional
# import os
# import uuid
# from datetime import datetime, timezone
# from dotenv import load_dotenv
# from emergentintegrations.llm.chat import LlmChat, UserMessage

# # Load environment variables
# load_dotenv()
# EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY")
# print("Loaded EMERGENT_LLM_KEY:", bool(EMERGENT_LLM_KEY))
# app = FastAPI(title="PromptMaster API")

# # Environment variables
# MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
# DB_NAME = os.environ.get("DB_NAME", "promptmaster_db")
# CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
# EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
# # MONGO_URL=mongodb://localhost:27017
# # DB_NAME=promptmaster_db
# # CORS_ORIGINS=http://localhost:3000   # or "*" if you prefer
# # EMERGENT_LLM_KEY=your_emergent_llm_api_key

# # MongoDB client
# client = AsyncIOMotorClient(MONGO_URL)
# db = client[DB_NAME]

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=CORS_ORIGINS.split(",") if CORS_ORIGINS != "*" else ["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Pydantic models
# class PromptOptimizeRequest(BaseModel):
#     original_prompt: str
#     category: str

# class PromptOptimizeResponse(BaseModel):
#     id: str = Field(default_factory=lambda: str(uuid.uuid4()))
#     original_prompt: str
#     optimized_prompt: str
#     category: str
#     timestamp: str

# class PromptHistory(BaseModel):
#     id: str = Field(default_factory=lambda: str(uuid.uuid4()))
#     original_prompt: str
#     optimized_prompt: str
#     category: str
#     timestamp: str

# class Template(BaseModel):
#     id: str = Field(default_factory=lambda: str(uuid.uuid4()))
#     category: str
#     title: str
#     template: str
#     description: str

# # Initialize LLM Chat for prompt optimization
# async def get_llm_chat():
#     return LlmChat(
#         api_key=EMERGENT_LLM_KEY,
#         session_id="prompt_optimizer",
#         system_message="""You are an expert prompt optimization specialist. Your job is to take user prompts and make them significantly better by:

# 1. Making them more specific and detailed
# 2. Improving clarity and structure  
# 3. Adding relevant context and examples
# 4. Ensuring they follow best practices for the given category

# For each prompt, provide a comprehensive optimized version that will produce much better results from AI models. Focus on:
# - Clear instructions and expectations
# - Specific formatting requirements when relevant
# - Context that helps the AI understand the task better
# - Examples when they would be helpful
# - Appropriate tone and style for the category

# Return ONLY the optimized prompt, no explanations or additional text."""
#     ).with_model("openai", "gpt-4o")

# # Predefined templates for each category
# PREDEFINED_TEMPLATES = [
#     {
#         "category": "text_summarization",
#         "title": "Article Summarizer",
#         "template": "Please provide a comprehensive summary of the following text. Focus on the main points, key arguments, and important conclusions. Structure your summary with clear headings and bullet points where appropriate. Keep the summary to approximately [X] words while maintaining all critical information.\n\nText to summarize:\n[INSERT TEXT HERE]",
#         "description": "Template for summarizing articles, documents, or long-form content"
#     },
#     {
#         "category": "code_generation", 
#         "title": "Function Generator",
#         "template": "Create a [PROGRAMMING LANGUAGE] function that [SPECIFIC FUNCTIONALITY]. The function should:\n\n- Accept the following parameters: [LIST PARAMETERS]\n- Return: [EXPECTED RETURN TYPE]\n- Include proper error handling for [POTENTIAL ERRORS]\n- Follow [CODING STANDARDS] conventions\n- Include clear comments and docstrings\n\nAdditional requirements:\n[LIST ANY SPECIFIC REQUIREMENTS]",
#         "description": "Template for generating code functions with specific requirements"
#     },
#     {
#         "category": "content_creation",
#         "title": "Blog Post Creator", 
#         "template": "Write a comprehensive blog post about [TOPIC] for [TARGET AUDIENCE]. The post should:\n\n- Have an engaging headline\n- Include an introduction that hooks the reader\n- Cover these key points: [LIST KEY POINTS]\n- Be approximately [WORD COUNT] words\n- Include practical examples or case studies\n- End with a clear call-to-action\n- Use an [TONE] tone throughout\n\nSEO keywords to incorporate: [LIST KEYWORDS]",
#         "description": "Template for creating engaging blog posts and articles"
#     },
#     {
#         "category": "data_analysis",
#         "title": "Data Insights Generator",
#         "template": "Analyze the following dataset and provide insights. Please:\n\n1. Summarize the key statistics and trends\n2. Identify any patterns or anomalies\n3. Provide actionable recommendations based on the data\n4. Highlight the most significant findings\n5. Suggest areas for further investigation\n\nData context: [DESCRIBE THE DATA]\nSpecific questions to address: [LIST QUESTIONS]\n\nDataset:\n[INSERT DATA HERE]",
#         "description": "Template for analyzing data and generating insights"
#     },
#     {
#         "category": "chatbot_response",
#         "title": "Customer Service Bot",
#         "template": "You are a helpful customer service representative for [COMPANY NAME]. Respond to the following customer inquiry with:\n\n- A warm, professional tone\n- Clear and helpful information\n- Specific steps or solutions when applicable\n- Appropriate empathy for any concerns\n- Offer to escalate if needed\n\nCompany policies to keep in mind: [LIST RELEVANT POLICIES]\n\nCustomer inquiry:\n[INSERT CUSTOMER MESSAGE HERE]",
#         "description": "Template for creating customer service chatbot responses"
#     },
#     {
#         "category": "creative_writing",
#         "title": "Story Generator",
#         "template": "Write a [GENRE] story that includes:\n\n- Setting: [TIME PERIOD/LOCATION]\n- Main character: [CHARACTER DESCRIPTION]\n- Central conflict: [DESCRIBE CONFLICT]\n- Tone: [TONE/MOOD]\n- Word count: Approximately [NUMBER] words\n- Must include these elements: [LIST SPECIFIC ELEMENTS]\n\nThe story should have a clear beginning, middle, and end with engaging dialogue and vivid descriptions.",
#         "description": "Template for generating creative stories and narratives"
#     },
#     {
#         "category": "email_templates",
#         "title": "Professional Email",
#         "template": "Compose a professional email with the following details:\n\n- Purpose: [EMAIL PURPOSE]\n- Recipient: [WHO YOU'RE WRITING TO]\n- Tone: [FORMAL/CASUAL/FRIENDLY]\n- Key points to cover: [LIST MAIN POINTS]\n- Desired action from recipient: [WHAT YOU WANT THEM TO DO]\n- Context/background: [RELEVANT BACKGROUND INFO]\n\nInclude an appropriate subject line and professional closing.",
#         "description": "Template for creating professional email communications"
#     },
#     {
#         "category": "social_media",
#         "title": "Social Media Post",
#         "template": "Create a [PLATFORM] post about [TOPIC] that:\n\n- Engages [TARGET AUDIENCE]\n- Uses an [TONE] tone\n- Includes relevant hashtags (suggest 5-10)\n- Has a clear call-to-action\n- Fits platform character limits\n- Encourages engagement (likes, shares, comments)\n\nKey message: [MAIN MESSAGE]\nHashtag strategy: [SPECIFIC HASHTAG REQUIREMENTS]",
#         "description": "Template for creating engaging social media content"
#     },
#     {
#         "category": "academic_writing",
#         "title": "Research Paper Section",
#         "template": "Write a [SECTION TYPE] for an academic paper on [RESEARCH TOPIC]. This section should:\n\n- Follow [CITATION STYLE] format\n- Be approximately [WORD COUNT] words\n- Include relevant citations and references\n- Maintain an objective, scholarly tone\n- Address these key points: [LIST KEY POINTS]\n- Connect to the broader research question: [RESEARCH QUESTION]\n\nTarget journal/audience: [PUBLICATION TARGET]",
#         "description": "Template for academic writing and research papers"
#     },
#     {
#         "category": "marketing_copy",
#         "title": "Product Launch Copy",
#         "template": "Create compelling marketing copy for [PRODUCT/SERVICE] that:\n\n- Highlights key benefits: [LIST BENEFITS]\n- Addresses target customer pain points: [LIST PAIN POINTS]\n- Includes social proof or testimonials\n- Has a strong call-to-action\n- Uses persuasive language appropriate for [TARGET AUDIENCE]\n- Emphasizes unique selling proposition: [USP]\n- Fits [FORMAT] format requirements\n\nBrand voice: [BRAND PERSONALITY]",
#         "description": "Template for creating effective marketing and sales copy"
#     }
# ]

# @app.on_event("startup")
# async def startup_event():
#     # Initialize templates in database
#     templates_collection = db.templates
#     existing_templates = await templates_collection.count_documents({})
    
#     if existing_templates == 0:
#         for template_data in PREDEFINED_TEMPLATES:
#             template = Template(
#                 category=template_data["category"],
#                 title=template_data["title"],
#                 template=template_data["template"],
#                 description=template_data["description"]
#             )
#             await templates_collection.insert_one(template.dict())

# @app.get("/")
# async def root():
#     return {"message": "PromptMaster API is running"}

# @app.post("/api/optimize", response_model=PromptOptimizeResponse)
# async def optimize_prompt(request: PromptOptimizeRequest):
#     try:
#         # Get LLM chat instance
#         chat = await get_llm_chat()
        
#         # Create optimization prompt based on category
#         category_guidance = {
#             "text_summarization": "Focus on creating a prompt that will generate clear, structured summaries with key points highlighted.",
#             "code_generation": "Optimize for specific programming requirements, including language, functionality, error handling, and coding standards.",
#             "content_creation": "Enhance for engaging content with clear structure, target audience considerations, and SEO optimization.",
#             "data_analysis": "Improve for comprehensive data analysis with statistical insights, trend identification, and actionable recommendations.",
#             "chatbot_response": "Optimize for conversational AI with appropriate tone, context awareness, and user-friendly responses.",
#             "creative_writing": "Enhance for storytelling with character development, plot structure, and vivid descriptive elements.",
#             "email_templates": "Optimize for professional communication with clear purpose, appropriate tone, and effective call-to-action.",
#             "social_media": "Improve for platform-specific engagement with hashtags, audience targeting, and shareability.",
#             "academic_writing": "Enhance for scholarly writing with proper citations, objective tone, and research methodology.",
#             "marketing_copy": "Optimize for persuasive content with benefit-focused messaging, customer pain points, and conversion optimization."
#         }
        
#         guidance = category_guidance.get(request.category, "Optimize this prompt for better AI model results.")
        
#         optimization_request = f"""Category: {request.category.replace('_', ' ').title()}
        
# Special focus for this category: {guidance}

# Original prompt to optimize:
# {request.original_prompt}"""

#         # Send to LLM for optimization
#         user_message = UserMessage(text=optimization_request)
#         optimized_response = await chat.send_message(user_message)

#         # Extract text if response is dict/object
#         if isinstance(optimized_response, dict):
#             optimized_text = optimized_response.get("output", {}).get("text", "")
#         else:
#             optimized_text = str(optimized_response)

#         result = PromptOptimizeResponse(
#             original_prompt=request.original_prompt,
#             optimized_prompt=optimized_text,
#             category=request.category,
#             timestamp=datetime.now(timezone.utc).isoformat()
#         )

#         # optimized_response = await chat.send_message(user_message)
        
#         # # Create response object
#         # result = PromptOptimizeResponse(
#         #     original_prompt=request.original_prompt,
#         #     optimized_prompt=optimized_response,
#         #     category=request.category,
#         #     timestamp=datetime.now(timezone.utc).isoformat()
#         # )
        
#         # Save to history
#         history_item = result.dict()
#         await db.prompt_history.insert_one(history_item)
        
#         return result
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error optimizing prompt: {str(e)}")

# @app.get("/api/history", response_model=List[PromptHistory])
# async def get_history(limit: int = 50):
#     try:
#         cursor = db.prompt_history.find().sort("timestamp", -1).limit(limit)
#         history = await cursor.to_list(length=limit)
        
#         return [PromptHistory(**item) for item in history]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

# @app.get("/api/templates", response_model=List[Template])
# async def get_templates(category: Optional[str] = None):
#     try:
#         query = {"category": category} if category else {}
#         cursor = db.templates.find(query)
#         templates = await cursor.to_list(length=None)
        
#         return [Template(**template) for template in templates]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")

# @app.delete("/api/history/{prompt_id}")
# async def delete_history_item(prompt_id: str):
#     try:
#         result = await db.prompt_history.delete_one({"id": prompt_id})
#         if result.deleted_count == 0:
#             raise HTTPException(status_code=404, detail="History item not found")
#         return {"message": "History item deleted successfully"}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error deleting history item: {str(e)}")

# @app.get("/api/categories")
# async def get_categories():
#     return {
#         "categories": [
#             {"id": "text_summarization", "name": "Text Summarization", "icon": "📄"},
#             {"id": "code_generation", "name": "Code Generation", "icon": "💻"},
#             {"id": "content_creation", "name": "Content Creation", "icon": "✍️"},
#             {"id": "data_analysis", "name": "Data Analysis", "icon": "📊"},
#             {"id": "chatbot_response", "name": "Chatbot Response", "icon": "🤖"},
#             {"id": "creative_writing", "name": "Creative Writing", "icon": "🎨"},
#             {"id": "email_templates", "name": "Email Templates", "icon": "📧"},
#             {"id": "social_media", "name": "Social Media", "icon": "🌐"},
#             {"id": "academic_writing", "name": "Academic Writing", "icon": "🎓"},
#             {"id": "marketing_copy", "name": "Marketing Copy", "icon": "📢"}
#         ]
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)