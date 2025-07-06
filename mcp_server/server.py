import os
import sys
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from dotenv import load_dotenv
import uvicorn
import subprocess
import json
import asyncio

# Import our custom modules
from mcp_server.llm_client import llm_client
from prompts.rag_prompt import get_rag_prompt, get_tool_prompt, get_clean_rag_prompt
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

class EnhancedChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict]] = []
    format_preference: Optional[str] = "markdown"  # markdown, plain, code
    auto_tool_selection: bool = True

class StreamingChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict]] = []
    format_preference: Optional[str] = "markdown"
    auto_tool_selection: bool = True

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

# --- Enhanced Chat Endpoint with Auto Tool Selection ---
@app.post("/chat/enhanced")
async def enhanced_chat_with_assistant(req: EnhancedChatRequest):
    """
    Enhanced chat endpoint with automatic tool selection and formatting options.
    
    This endpoint:
    - Automatically detects user intent and selects appropriate tools
    - Supports multiple formatting options (markdown, plain, code)
    - Maintains conversation context
    - Provides structured responses with tool usage information
    """
    try:
        # Build context from conversation history
        context = ""
        if req.conversation_history:
            context = "\n".join([
                f"{'User' if msg.get('role') == 'user' else 'Assistant'}: {msg.get('content', '')}"
                for msg in req.conversation_history[-5:]  # Last 5 messages for context
            ])
        
        # Enhanced intent analysis with context
        intent_prompt = f"""
        Analyze this user query and determine the best action to take.
        
        Conversation Context:
        {context}
        
        Current Query: "{req.message}"
        
        Available Tools:
        1. analyze_resume - For resume feedback and analysis
        2. mock_interview - For interview preparation and questions
        3. career_guides - For general career advice and guidance
        
        Determine the intent and required action:
        - If user wants resume analysis: return "RESUME_ANALYSIS"
        - If user wants interview help: return "INTERVIEW_PREP"
        - If user asks for career advice: return "CAREER_ADVICE"
        - If user provides resume text: return "ANALYZE_RESUME_TEXT"
        - If user provides position for interview: return "GENERATE_INTERVIEW_QUESTIONS"
        - If unclear or general question: return "GENERAL_CHAT"
        
        Respond with just the action type.
        """
        
        intent_response = llm_client.generate_response(intent_prompt, max_tokens=50).strip()
        
        # Execute based on detected intent
        if "RESUME_ANALYSIS" in intent_response:
            return {
                "response": "I'd be happy to analyze your resume! Please paste your resume text below, and I'll provide detailed feedback on structure, content, and improvements.",
                "action": "request_resume_text",
                "format": req.format_preference,
                "tools_used": [],
                "reasoning": "User requested resume analysis"
            }
        
        elif "ANALYZE_RESUME_TEXT" in intent_response:
            # Extract resume text from message (assuming it's the main content)
            resume_text = req.message.strip()
            if len(resume_text) < 50:
                return {
                    "response": "I need more resume content to provide meaningful analysis. Please paste your complete resume text.",
                    "action": "request_more_resume_text",
                    "format": req.format_preference,
                    "tools_used": [],
                    "reasoning": "Insufficient resume content provided"
                }
            
            # Call resume analysis tool
            try:
                analysis_result = analyze_resume(ResumeRequest(resume_text=resume_text))
                
                if req.format_preference == "markdown":
                    response = f"""## Resume Analysis Results

**Analysis Type:** {analysis_result.get('analysis_type', 'Unknown')}
**Resume Length:** {analysis_result.get('resume_length', 0)} characters

### Feedback:
{analysis_result.get('feedback', 'No feedback available')}

---
*Analysis completed using AI-enhanced tools*"""
                elif req.format_preference == "code":
                    # Handle feedback properly for JSON
                    feedback = analysis_result.get('feedback', 'No feedback available')
                    if isinstance(feedback, list):
                        feedback_str = str(feedback)
                    else:
                        feedback_str = str(feedback)
                    response = f"""```json
{{
  "analysis_type": "{analysis_result.get('analysis_type', 'Unknown')}",
  "resume_length": {analysis_result.get('resume_length', 0)},
  "feedback": {feedback_str}
}}
```"""
                else:
                    response = f"Resume Analysis Results:\n\nAnalysis Type: {analysis_result.get('analysis_type', 'Unknown')}\nResume Length: {analysis_result.get('resume_length', 0)} characters\n\nFeedback:\n{analysis_result.get('feedback', 'No feedback available')}"
                
                return {
                    "response": response,
                    "action": "resume_analysis_complete",
                    "format": req.format_preference,
                    "tools_used": ["analyze_resume"],
                    "reasoning": "Successfully analyzed resume using AI tools"
                }
            except Exception as e:
                return {
                    "response": f"Sorry, I encountered an error while analyzing your resume: {str(e)}",
                    "action": "error",
                    "format": req.format_preference,
                    "tools_used": [],
                    "reasoning": f"Resume analysis failed: {str(e)}"
                }
        
        elif "INTERVIEW_PREP" in intent_response:
            return {
                "response": "I can help you prepare for interviews! What position are you interviewing for? I'll generate relevant questions and preparation tips.",
                "action": "request_interview_position",
                "format": req.format_preference,
                "tools_used": [],
                "reasoning": "User requested interview preparation"
            }
        
        elif "GENERATE_INTERVIEW_QUESTIONS" in intent_response:
            # Extract position from message
            position = req.message.strip()
            if len(position) < 3:
                return {
                    "response": "Please specify the position you're interviewing for so I can provide relevant questions.",
                    "action": "request_interview_position",
                    "format": req.format_preference,
                    "tools_used": [],
                    "reasoning": "Position not specified"
                }
            
            # Call mock interview tool
            try:
                interview_result = mock_interview(InterviewRequest(position=position))
                
                if req.format_preference == "markdown":
                    questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(interview_result.get('questions', []))])
                    response = f"""## Interview Questions for {position}

**Generation Type:** {interview_result.get('generation_type', 'Unknown')}

### Questions:
{questions_text}

### Preparation Tips:
- Practice your responses out loud
- Use the STAR method for behavioral questions
- Research the company and role thoroughly
- Prepare questions to ask the interviewer

---
*Questions generated using AI-enhanced tools*"""
                elif req.format_preference == "code":
                    response = f"""```json
{{
  "position": "{position}",
  "generation_type": "{interview_result.get('generation_type', 'Unknown')}",
  "questions": {interview_result.get('questions', [])}
}}
```"""
                else:
                    questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(interview_result.get('questions', []))])
                    response = f"Interview Questions for {position}:\n\n{questions_text}"
                
                return {
                    "response": response,
                    "action": "interview_questions_generated",
                    "format": req.format_preference,
                    "tools_used": ["mock_interview"],
                    "reasoning": f"Generated interview questions for {position}"
                }
            except Exception as e:
                return {
                    "response": f"Sorry, I encountered an error while generating interview questions: {str(e)}",
                    "action": "error",
                    "format": req.format_preference,
                    "tools_used": [],
                    "reasoning": f"Interview question generation failed: {str(e)}"
                }
        
        elif "CAREER_ADVICE" in intent_response:
            # Use RAG for career advice
            try:
                # Retrieve relevant documents
                retrieved_docs = retrieve(req.message, 3)
                context = "\n\n".join([doc['chunk'] for doc in retrieved_docs])
                
                if llm_client.is_available():
                    prompt = get_clean_rag_prompt(context, req.message)
                    advice = llm_client.generate_response(prompt)
                else:
                    advice = f"Based on our career guides, here's what I found:\n\n{context[:1000]}..."
                
                if req.format_preference == "markdown":
                    sources_text = "\n".join([f"- {source}" for source in [doc['metadata']['file'] for doc in retrieved_docs]])
                    response = f"""## Career Advice

{advice}

### Sources:
{sources_text}

---
*Advice generated using RAG-enhanced knowledge base*"""
                elif req.format_preference == "code":
                    # Escape quotes properly for JSON
                    escaped_advice = advice.replace('"', '\\"').replace('\n', '\\n')
                    response = f"""```json
{{
  "advice": "{escaped_advice}",
  "sources": {[doc['metadata']['file'] for doc in retrieved_docs]}
}}
```"""
                else:
                    response = f"Career Advice:\n\n{advice}\n\nSources: {', '.join([doc['metadata']['file'] for doc in retrieved_docs])}"
                
                return {
                    "response": response,
                    "action": "career_advice_provided",
                    "format": req.format_preference,
                    "tools_used": ["career_guides"],
                    "reasoning": "Provided career advice using RAG"
                }
            except Exception as e:
                return {
                    "response": f"Sorry, I encountered an error while retrieving career advice: {str(e)}",
                    "action": "error",
                    "format": req.format_preference,
                    "tools_used": [],
                    "reasoning": f"Career advice retrieval failed: {str(e)}"
                }
        
        else:
            # General chat response
            general_response = "I'm here to help with your career development! I can assist with:\n\n- **Resume Analysis**: Get detailed feedback on your resume\n- **Interview Preparation**: Receive role-specific interview questions\n- **Career Advice**: Access expert guidance on career transitions and development\n\nWhat would you like to work on today?"
            
            if req.format_preference == "markdown":
                response = f"""## Welcome to Career Coach AI!

{general_response}

---
*Ready to help with your career goals*"""
            elif req.format_preference == "code":
                response = f"""```json
{{
  "message": "Welcome to Career Coach AI!",
  "capabilities": [
    "Resume Analysis",
    "Interview Preparation", 
    "Career Advice"
  ]
}}
```"""
            else:
                response = general_response
            
            return {
                "response": response,
                "action": "general_chat",
                "format": req.format_preference,
                "tools_used": [],
                "reasoning": "Provided general welcome and capabilities overview"
            }
    
    except Exception as e:
        logger.error(f"Enhanced chat processing failed: {e}")
        return {
            "response": f"I apologize, but I encountered an error while processing your request: {str(e)}",
            "action": "error",
            "format": req.format_preference,
            "tools_used": [],
            "reasoning": f"Enhanced chat processing failed: {str(e)}"
        }

# --- Streaming Chat Endpoint ---
@app.post("/chat/stream")
async def streaming_chat_with_assistant(req: StreamingChatRequest):
    """
    Streaming chat endpoint with real-time responses.
    
    This endpoint:
    - Provides real-time streaming responses
    - Automatically detects user intent and selects appropriate tools
    - Supports multiple formatting options
    - Uses Server-Sent Events (SSE) for streaming
    """
    
    async def generate_stream():
        try:
            # Build context from conversation history
            context = ""
            if req.conversation_history:
                context = "\n".join([
                    f"{'User' if msg.get('role') == 'user' else 'Assistant'}: {msg.get('content', '')}"
                    for msg in req.conversation_history[-5:]  # Last 5 messages for context
                ])
            
            # Send initial thinking message
            yield f"data: {json.dumps({'type': 'thinking', 'content': 'Analyzing your request...'})}\n\n"
            
            # Enhanced intent analysis with context
            intent_prompt = f"""
            Analyze this user query and determine the best action to take.
            
            Conversation Context:
            {context}
            
            Current Query: "{req.message}"
            
            Available Tools:
            1. analyze_resume - For resume feedback and analysis
            2. mock_interview - For interview preparation and questions
            3. career_guides - For general career advice and guidance
            
            Determine the intent and required action:
            - If user wants resume analysis: return "RESUME_ANALYSIS"
            - If user wants interview help: return "INTERVIEW_PREP"
            - If user asks for career advice: return "CAREER_ADVICE"
            - If user provides resume text: return "ANALYZE_RESUME_TEXT"
            - If user provides position for interview: return "GENERATE_INTERVIEW_QUESTIONS"
            - If unclear or general question: return "GENERAL_CHAT"
            
            Respond with just the action type.
            """
            
            intent_response = llm_client.generate_response(intent_prompt, max_tokens=50).strip()
            
            # Send intent detection message
            yield f"data: {json.dumps({'type': 'intent', 'content': f'Detected intent: {intent_response}'})}\n\n"
            
            # Execute based on detected intent
            if "RESUME_ANALYSIS" in intent_response:
                response = "I'd be happy to analyze your resume! Please paste your resume text below, and I'll provide detailed feedback on structure, content, and improvements."
                action = "request_resume_text"
                tools_used = []
                reasoning = "User requested resume analysis"
                
            elif "ANALYZE_RESUME_TEXT" in intent_response:
                # Extract resume text from message
                resume_text = req.message.strip()
                if len(resume_text) < 50:
                    response = "I need more resume content to provide meaningful analysis. Please paste your complete resume text."
                    action = "request_more_resume_text"
                    tools_used = []
                    reasoning = "Insufficient resume content provided"
                else:
                    # Send processing message
                    yield f"data: {json.dumps({'type': 'processing', 'content': 'Analyzing your resume...'})}\n\n"
                    
                    # Call resume analysis tool
                    try:
                        # Show tool call step
                        yield f"data: {json.dumps({'type': 'tool_call', 'content': '📄 Calling resume analysis tool...'})}\n\n"
                        
                        analysis_result = analyze_resume(ResumeRequest(resume_text=resume_text))
                        
                        # Show tool result
                        analysis_type = analysis_result.get('analysis_type', 'Unknown')
                        yield f"data: {json.dumps({'type': 'tool_result', 'content': f'✅ Resume analysis completed using {analysis_type} method'})}\n\n"
                        
                        if req.format_preference == "markdown":
                            response = f"""## Resume Analysis Results

**Analysis Type:** {analysis_result.get('analysis_type', 'Unknown')}
**Resume Length:** {analysis_result.get('resume_length', 0)} characters

### Feedback:
{analysis_result.get('feedback', 'No feedback available')}

---
*Analysis completed using AI-enhanced tools*"""
                        elif req.format_preference == "code":
                            # Handle feedback properly for JSON
                            feedback = analysis_result.get('feedback', 'No feedback available')
                            if isinstance(feedback, list):
                                feedback_str = str(feedback)
                            else:
                                feedback_str = str(feedback)
                            response = f"""```json
{{
  "analysis_type": "{analysis_result.get('analysis_type', 'Unknown')}",
  "resume_length": {analysis_result.get('resume_length', 0)},
  "feedback": {feedback_str}
}}
```"""
                        else:
                            response = f"Resume Analysis Results:\n\nAnalysis Type: {analysis_result.get('analysis_type', 'Unknown')}\nResume Length: {analysis_result.get('resume_length', 0)} characters\n\nFeedback:\n{analysis_result.get('feedback', 'No feedback available')}"
                        
                        action = "resume_analysis_complete"
                        tools_used = ["analyze_resume"]
                        reasoning = "Successfully analyzed resume using AI tools"
                        
                    except Exception as e:
                        response = f"Sorry, I encountered an error while analyzing your resume: {str(e)}"
                        action = "error"
                        tools_used = []
                        reasoning = f"Resume analysis failed: {str(e)}"
            
            elif "INTERVIEW_PREP" in intent_response:
                response = "I can help you prepare for interviews! What position are you interviewing for? I'll generate relevant questions and preparation tips."
                action = "request_interview_position"
                tools_used = []
                reasoning = "User requested interview preparation"
            
            elif "GENERATE_INTERVIEW_QUESTIONS" in intent_response:
                # Extract position from message
                position = req.message.strip()
                if len(position) < 3:
                    response = "Please specify the position you're interviewing for so I can provide relevant questions."
                    action = "request_interview_position"
                    tools_used = []
                    reasoning = "Position not specified"
                else:
                    # Send processing message
                    yield f"data: {json.dumps({'type': 'processing', 'content': f'Generating interview questions for {position}...'})}\n\n"
                    
                    # Call mock interview tool
                    try:
                        # Show tool call step
                        yield f"data: {json.dumps({'type': 'tool_call', 'content': f'🎯 Calling mock interview tool for {position}...'})}\n\n"
                        
                        interview_result = mock_interview(InterviewRequest(position=position))
                        
                        # Show tool result
                        generation_type = interview_result.get('generation_type', 'Unknown')
                        yield f"data: {json.dumps({'type': 'tool_result', 'content': f'✅ Interview questions generated using {generation_type} method'})}\n\n"
                        
                        if req.format_preference == "markdown":
                            questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(interview_result.get('questions', []))])
                            response = f"""## Interview Questions for {position}

**Generation Type:** {interview_result.get('generation_type', 'Unknown')}

### Questions:
{questions_text}

### Preparation Tips:
- Practice your responses out loud
- Use the STAR method for behavioral questions
- Research the company and role thoroughly
- Prepare questions to ask the interviewer

---
*Questions generated using AI-enhanced tools*"""
                        elif req.format_preference == "code":
                            response = f"""```json
{{
  "position": "{position}",
  "generation_type": "{interview_result.get('generation_type', 'Unknown')}",
  "questions": {interview_result.get('questions', [])}
}}
```"""
                        else:
                            questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(interview_result.get('questions', []))])
                            response = f"Interview Questions for {position}:\n\n{questions_text}"
                        
                        action = "interview_questions_generated"
                        tools_used = ["mock_interview"]
                        reasoning = f"Generated interview questions for {position}"
                        
                    except Exception as e:
                        response = f"Sorry, I encountered an error while generating interview questions: {str(e)}"
                        action = "error"
                        tools_used = []
                        reasoning = f"Interview question generation failed: {str(e)}"
            
            elif "CAREER_ADVICE" in intent_response:
                # Send processing message
                yield f"data: {json.dumps({'type': 'processing', 'content': 'Searching for career advice...'})}\n\n"
                
                # Use RAG for career advice
                try:
                    # Show RAG retrieval step
                    yield f"data: {json.dumps({'type': 'tool_call', 'content': '🔍 Retrieving relevant career guides...'})}\n\n"
                    
                    retrieved_docs = retrieve(req.message, 3)
                    sources = [doc['metadata']['file'] for doc in retrieved_docs]
                    
                    # Show what was found
                    sources_text = ", ".join(sources)
                    yield f"data: {json.dumps({'type': 'tool_result', 'content': f'📚 Found guides: {sources_text}'})}\n\n"
                    
                    context = "\n\n".join([doc['chunk'] for doc in retrieved_docs])
                    
                    if llm_client.is_available():
                        # Show LLM processing step
                        yield f"data: {json.dumps({'type': 'llm_processing', 'content': '🤖 Generating personalized advice using AI...'})}\n\n"
                        
                        prompt = get_clean_rag_prompt(context, req.message)
                        advice = llm_client.generate_response(prompt)
                    else:
                        advice = f"Based on our career guides, here's what I found:\n\n{context[:1000]}..."
                    
                    if req.format_preference == "markdown":
                        sources_text = "\n".join([f"- {source}" for source in [doc['metadata']['file'] for doc in retrieved_docs]])
                        response = f"""## Career Advice

{advice}

### Sources:
{sources_text}

---
*Advice generated using RAG-enhanced knowledge base*"""
                    elif req.format_preference == "code":
                        # Escape quotes properly for JSON
                        escaped_advice = advice.replace('"', '\\"').replace('\n', '\\n')
                        response = f"""```json
{{
  "advice": "{escaped_advice}",
  "sources": {[doc['metadata']['file'] for doc in retrieved_docs]}
}}
```"""
                    else:
                        response = f"Career Advice:\n\n{advice}\n\nSources: {', '.join([doc['metadata']['file'] for doc in retrieved_docs])}"
                    
                    action = "career_advice_provided"
                    tools_used = ["career_guides"]
                    reasoning = "Provided career advice using RAG"
                    
                except Exception as e:
                    response = f"Sorry, I encountered an error while retrieving career advice: {str(e)}"
                    action = "error"
                    tools_used = []
                    reasoning = f"Career advice retrieval failed: {str(e)}"
            
            else:
                # General chat response
                general_response = "I'm here to help with your career development! I can assist with:\n\n- **Resume Analysis**: Get detailed feedback on your resume\n- **Interview Preparation**: Receive role-specific interview questions\n- **Career Advice**: Access expert guidance on career transitions and development\n\nWhat would you like to work on today?"
                
                if req.format_preference == "markdown":
                    response = f"""## Welcome to Career Coach AI!

{general_response}

---
*Ready to help with your career goals*"""
                elif req.format_preference == "code":
                    response = f"""```json
{{
  "message": "Welcome to Career Coach AI!",
  "capabilities": [
    "Resume Analysis",
    "Interview Preparation", 
    "Career Advice"
  ]
}}
```"""
                else:
                    response = general_response
                
                action = "general_chat"
                tools_used = []
                reasoning = "Provided general welcome and capabilities overview"
            
            # Stream the response in chunks
            chunk_size = 50  # Characters per chunk
            for i in range(0, len(response), chunk_size):
                chunk = response[i:i + chunk_size]
                yield f"data: {json.dumps({'type': 'content', 'content': chunk, 'is_final': i + chunk_size >= len(response)})}\n\n"
                await asyncio.sleep(0.05)  # Small delay for smooth streaming
            
            # Send final metadata
            yield f"data: {json.dumps({'type': 'metadata', 'action': action, 'tools_used': tools_used, 'reasoning': reasoning, 'format': req.format_preference})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming chat processing failed: {e}")
            error_response = f"I apologize, but I encountered an error while processing your request: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'content': error_response})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

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