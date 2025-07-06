import os
import sys
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from dotenv import load_dotenv
import uvicorn
import subprocess

# Import our custom modules
from mcp_server.llm_client import llm_client
from prompts.rag_prompt import get_rag_prompt, get_tool_prompt
from rag.retrieval import retrieve

load_dotenv()

app = FastAPI(
    title="Career Coach AI MCP Server",
    description="AI-powered career coaching assistant with RAG and tools",
    version="1.0.0"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Request Models ---
class ResumeRequest(BaseModel):
    resume_text: str
    use_llm: bool = True

class InterviewRequest(BaseModel):
    position: str
    use_llm: bool = True

class GuideRequest(BaseModel):
    query: str
    top_k: int = 3
    use_llm: bool = True

class ChatRequest(BaseModel):
    message: str
    use_rag: bool = True
    use_tools: bool = True

# --- Tool 1: Enhanced Resume Analysis ---
@app.post("/tools/analyze_resume")
def analyze_resume(req: ResumeRequest):
    """
    Analyze resume text and provide detailed feedback.
    
    This tool analyzes resumes for:
    - Content quality and relevance
    - Structure and formatting
    - Keyword optimization
    - Industry-specific improvements
    - Action verb usage
    - Quantifiable achievements
    """
    try:
        if req.use_llm and llm_client.is_available():
            # Use LLM for enhanced analysis
            prompt = get_tool_prompt("analyze_resume", req.resume_text)
            response = llm_client.generate_response(prompt)
            return {
                "feedback": response,
                "analysis_type": "llm_enhanced",
                "resume_length": len(req.resume_text)
            }
        else:
            # Fallback to rule-based analysis
            text = req.resume_text.lower()
            feedback = []
            
            # Content analysis
            if len(req.resume_text) < 500:
                feedback.append("Your resume is quite short. Consider adding more detail about your experience and skills.")
            elif len(req.resume_text) > 2000:
                feedback.append("Your resume might be too long. Consider condensing to 1-2 pages.")
            
            # Structure analysis
            if 'objective' not in text and 'summary' not in text:
                feedback.append("Consider adding an Objective or Summary section to highlight your career goals.")
            
            if 'experience' not in text and 'work' not in text:
                feedback.append("Make sure to include your work experience section.")
            
            # Skills analysis
            if 'skill' in text:
                feedback.append("Good inclusion of skills section.")
            else:
                feedback.append("Consider adding a dedicated skills section.")
            
            # Action verbs
            action_verbs = ['developed', 'managed', 'created', 'implemented', 'led', 'designed', 'analyzed']
            found_verbs = [verb for verb in action_verbs if verb in text]
            if found_verbs:
                feedback.append(f"Good use of action verbs: {', '.join(found_verbs)}")
            else:
                feedback.append("Consider using more action verbs to describe your achievements.")
            
            if not feedback:
                feedback.append("Your resume looks well-structured. Consider tailoring it for each job application.")
            
            return {
                "feedback": feedback,
                "analysis_type": "rule_based",
                "resume_length": len(req.resume_text)
            }
    
    except Exception as e:
        logger.error(f"Resume analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {str(e)}")

# --- Tool 2: Enhanced Mock Interview ---
@app.post("/tools/mock_interview")
def mock_interview(req: InterviewRequest):
    """
    Generate role-specific interview questions and preparation tips.
    
    This tool provides:
    - Technical questions for the specific role
    - Behavioral questions
    - Industry-specific scenarios
    - Preparation tips and strategies
    """
    try:
        if req.use_llm and llm_client.is_available():
            # Use LLM for enhanced interview questions
            prompt = get_tool_prompt("mock_interview", req.position)
            response = llm_client.generate_response(prompt)
            return {
                "questions": response,
                "position": req.position,
                "generation_type": "llm_enhanced"
            }
        else:
            # Fallback to predefined questions
            pos = req.position.lower()
            
            # Enhanced role-specific questions
            role_questions = {
                "software engineer": [
                    "Describe a challenging software bug you fixed and how you approached it.",
                    "How do you ensure code quality in your projects?",
                    "Explain a time you worked in a team to deliver a project on time.",
                    "What is your experience with version control systems like Git?",
                    "How do you keep your technical skills up to date?",
                    "Describe a time you had to learn a new technology quickly.",
                    "How do you handle conflicting requirements from stakeholders?",
                    "What's your approach to code review and feedback?"
                ],
                "data scientist": [
                    "Describe a machine learning project you've worked on from start to finish.",
                    "How do you handle missing or inconsistent data?",
                    "Explain the difference between supervised and unsupervised learning with examples.",
                    "How do you evaluate model performance beyond accuracy?",
                    "What tools and libraries do you use for data analysis?",
                    "Describe a time you had to explain complex technical concepts to non-technical stakeholders.",
                    "How do you stay updated with the latest developments in data science?",
                    "What's your approach to feature engineering?"
                ],
                "product manager": [
                    "How do you prioritize product features when resources are limited?",
                    "Describe a time you managed conflicting stakeholder interests.",
                    "How do you define and measure product success?",
                    "Explain your experience with agile methodologies.",
                    "How do you gather and incorporate user feedback?",
                    "Describe a product launch you managed and the challenges you faced.",
                    "How do you handle scope creep in projects?",
                    "What's your approach to competitive analysis?"
                ],
                "marketing": [
                    "Describe a successful marketing campaign you've managed.",
                    "How do you measure the ROI of marketing activities?",
                    "What tools do you use for marketing analytics?",
                    "How do you stay updated with marketing trends?",
                    "Describe a time you had to work with a limited budget.",
                    "How do you approach target audience segmentation?",
                    "What's your experience with digital marketing channels?",
                    "How do you handle negative feedback on marketing campaigns?"
                ]
            }
            
            # Find matching role
            for role, questions in role_questions.items():
                if role in pos:
                    return {
                        "questions": questions,
                        "position": req.position,
                        "generation_type": "predefined"
                    }
            
            # Default generic questions
            return {
                "questions": [
                    "Tell me about yourself and your background.",
                    "Why are you interested in this position and our company?",
                    "What are your greatest strengths and areas for improvement?",
                    "Describe a significant challenge you've overcome in your career.",
                    "Where do you see yourself in five years?",
                    "What motivates you in your work?",
                    "Describe a time you had to work with a difficult colleague.",
                    "How do you handle stress and pressure?"
                ],
                "position": req.position,
                "generation_type": "generic"
            }
    
    except Exception as e:
        logger.error(f"Mock interview generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Mock interview generation failed: {str(e)}")

# --- Resource: Enhanced Career Guides ---
@app.post("/resources/career_guides/featured")
def career_guides_featured(req: GuideRequest):
    """
    Retrieve curated career tips and advice from the knowledge base.
    
    This resource provides:
    - Relevant career guidance based on user queries
    - Curated tips from expert sources
    - Personalized advice using RAG
    """
    try:
        # Retrieve relevant documents using RAG
        retrieved_docs = retrieve(req.query, req.top_k)
        
        if req.use_llm and llm_client.is_available():
            # Use LLM to synthesize the retrieved information
            context = "\n\n".join([doc['chunk'] for doc in retrieved_docs])
            prompt = get_rag_prompt(context, req.query)
            response = llm_client.generate_response(prompt)
            
            return {
                "tips": response,
                "sources": [doc['metadata']['file'] for doc in retrieved_docs],
                "query": req.query,
                "generation_type": "rag_enhanced"
            }
        else:
            # Return raw retrieved content
            tips = [doc['chunk'][:500] + "..." for doc in retrieved_docs]
            return {
                "tips": tips,
                "sources": [doc['metadata']['file'] for doc in retrieved_docs],
                "query": req.query,
                "generation_type": "raw_retrieval"
            }
    
    except Exception as e:
        logger.error(f"Career guides retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Career guides retrieval failed: {str(e)}")

# --- Chat Endpoint with ReAct Pattern ---
@app.post("/chat")
def chat_with_assistant(req: ChatRequest):
    """
    Main chat endpoint implementing ReAct pattern.
    
    This endpoint:
    - Analyzes user intent
    - Decides whether to use tools, RAG, or both
    - Implements ReAct pattern for reasoning
    - Provides comprehensive responses
    """
    try:
        # Step 1: Analyze user intent
        intent_prompt = f"""
        Analyze this user query and determine the best approach:
        Query: "{req.message}"
        
        Options:
        1. Use resume analysis tool (if asking about resume feedback)
        2. Use mock interview tool (if asking about interview preparation)
        3. Use RAG retrieval (if asking for general career advice)
        4. Use both tools and RAG (if complex query)
        
        Respond with just the number (1-4) and a brief reason.
        """
        
        intent_response = llm_client.generate_response(intent_prompt, max_tokens=int(os.getenv('INTENT_ANALYSIS_MAX_TOKENS', '100')))
        
        # Step 2: Execute based on intent
        if "1" in intent_response and "resume" in req.message.lower():
            # Resume analysis
            return {
                "response": "I'll analyze your resume. Please paste your resume text in the next message.",
                "suggested_action": "resume_analysis",
                "reasoning": "User appears to need resume feedback"
            }
        
        elif "2" in intent_response and "interview" in req.message.lower():
            # Interview preparation
            return {
                "response": "I'll help you prepare for interviews. What position are you interviewing for?",
                "suggested_action": "mock_interview",
                "reasoning": "User appears to need interview preparation"
            }
        
        elif req.use_rag:
            # Use RAG for general career advice
            retrieved_docs = retrieve(req.message, int(os.getenv('CHAT_RAG_TOP_K', '3')))
            context = "\n\n".join([doc['chunk'] for doc in retrieved_docs])
            
            if llm_client.is_available():
                prompt = get_rag_prompt(context, req.message)
                response = llm_client.generate_response(prompt)
            else:
                response = f"Based on our career guides, here's what I found:\n\n{context[:1000]}..."
            
            return {
                "response": response,
                "sources": [doc['metadata']['file'] for doc in retrieved_docs],
                "reasoning": "Used RAG to provide relevant career advice"
            }
        
        else:
            # Generic response
            return {
                "response": "I'm here to help with your career development! I can assist with resume feedback, interview preparation, and general career advice. What would you like to work on?",
                "reasoning": "Provided general guidance"
            }
    
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

# --- Health Check and Info Endpoints ---
@app.get("/")
def root():
    """Root endpoint with service information."""
    return {
        "service": "Career Coach AI MCP Server",
        "version": "1.0.0",
        "tools": [
            {
                "name": "analyze_resume",
                "description": "Analyze resume text and provide detailed feedback",
                "endpoint": "/tools/analyze_resume"
            },
            {
                "name": "mock_interview", 
                "description": "Generate role-specific interview questions and preparation tips",
                "endpoint": "/tools/mock_interview"
            }
        ],
        "resources": [
            {
                "name": "career_guides://featured",
                "description": "Retrieve curated career tips and advice",
                "endpoint": "/resources/career_guides/featured"
            }
        ],
        "llm_status": llm_client.get_provider_info()
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "llm_available": llm_client.is_available(),
        "llm_providers": llm_client.get_provider_info()
    }

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=os.getenv('MCP_SERVER_HOST', '0.0.0.0'), 
        port=int(os.getenv('MCP_SERVER_PORT', 8000))
    ) 