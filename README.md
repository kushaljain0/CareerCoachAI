# Career Coach AI

A full-stack AI assistant that helps job seekers with resume feedback, mock interview preparation, and career advice using Retrieval-Augmented Generation (RAG) and Model Context Protocol (MCP).

## Domain Selection

This project focuses on **Career Coaching and Job Search Assistance**, a domain that is particularly well-suited for RAG + tools because:

1. **Rich Knowledge Base**: Career guidance requires access to extensive, up-to-date information about resume writing, interview techniques, industry trends, and career transitions
2. **Practical Tools**: Job seekers need actionable tools like resume analysis and mock interview generation that can provide personalized feedback
3. **Dynamic Content**: Career advice needs to be current and relevant, making RAG essential for retrieving the most recent and applicable guidance
4. **Personalization**: Different career stages and industries require tailored advice, which tools can provide based on user input
5. **Measurable Impact**: Career coaching has clear success metrics (job placement, interview success, salary negotiation outcomes)

## Features

- **Resume Analysis**: Get detailed feedback on your resume with specific improvement suggestions using LLM-enhanced analysis
- **Mock Interview Preparation**: Receive role-specific interview questions and preparation tips
- **Career Advice**: Access curated career guidance from indexed documents using RAG
- **Enhanced Chat Interface**: Intelligent chat with automatic tool selection and multiple formatting options
- **Streaming Chat**: Real-time streaming responses with Server-Sent Events for better user experience
- **RAG Pipeline**: Semantic search across 20+ career documents for relevant advice
- **MCP Server**: FastMCP-based tools for seamless AI interactions
- **Modern Web UI**: Beautiful React frontend with Material UI
- **Multi-LLM Support**: Gemini (default) with OpenAI fallback
- **ReAct Pattern**: Transparent reasoning and tool usage

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Google API key for Gemini (recommended) or OpenAI API key

### 1. Set up Environment Variables
```bash
cp env.example .env
# Add your Google API key to .env for Gemini (recommended)
# Or add OpenAI API key as fallback
```

### 2. Start the Application
```bash
# Production mode
docker-compose up -d

# Development mode (with hot reload)
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 4. Stop the Application
```bash
docker compose down
```

## Manual Setup (Alternative)

### Backend Setup
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Index Documents**:
   ```bash
   python rag/indexing.py
   ```

3. **Start MCP Server**:
   ```bash
   python mcp_server/server.py
   ```

### Frontend Setup
1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

## Architecture

### RAG Pipeline
- **Document Indexing**: 20+ PDFs/markdown files on resume writing, interview strategies, and career advice
- **Vector Storage**: FAISS for efficient similarity search
- **Chunking Strategy**: Semantic chunking with overlap for better context preservation
- **Multi-query Reformulation**: Enhanced document retrieval through query expansion
- **Advanced Technique**: Multi-query reformulation with paraphrasing models

### MCP Server (FastMCP)
- **Tool 1**: `analyze_resume(resume_text)` - Comprehensive resume analysis with LLM enhancement
- **Tool 2**: `mock_interview(position)` - Role-specific interview questions and preparation tips
- **Resource**: `career_guides://featured` - Curated career tips using RAG
- **Chat Endpoint**: `/chat` - Main interface with ReAct pattern implementation

### LLM Integration
- **Default**: Google Gemini 1.5 Flash
- **Fallback**: OpenAI GPT-4o-mini
- **Prompt Engineering**: ReAct pattern with structured reasoning
- **Error Handling**: Graceful degradation with rule-based fallbacks

### Frontend
- **React 18**: Modern React with hooks
- **Material UI**: Professional UI components
- **Vite**: Fast build tool and dev server
- **Responsive Design**: Works on all devices

## Example Interactions

### 1. Resume Feedback (ReAct Pattern)
```
User: "Can you analyze my resume?"
Assistant: 
Thought: User needs resume analysis. I should call the analyze_resume tool.
Action: analyze_resume(resume_text="[user's resume]")
Observation: Tool returns detailed feedback on structure, content, and improvements
Final Answer: Here's your comprehensive resume analysis with specific improvements...
```

### 2. Mock Interview
```
User: "I have an interview for a data scientist position"
Assistant:
Thought: User needs interview preparation for a specific role. I should call the mock_interview tool.
Action: mock_interview(position="data scientist")
Observation: Tool returns role-specific technical and behavioral questions
Final Answer: Here are likely interview questions for a data scientist role...
```

### 3. Career Advice (RAG Enhanced)
```
User: "How do I transition from marketing to data science?"
Assistant:
Thought: User needs career transition advice. I should retrieve relevant information.
Action: retrieve(query="transition from marketing to data science")
Observation: RAG returns career transition and skills development guides
Final Answer: Here's a step-by-step plan to transition from marketing to data science...
```

### 4. Enhanced Chat Interface
```
User: "Can you help me with my resume?"
Assistant: I'd be happy to analyze your resume! Please paste your resume text below, and I'll provide detailed feedback on structure, content, and improvements.

User: [pastes resume text]
Assistant: 
## Resume Analysis Results

**Analysis Type:** llm_enhanced
**Resume Length:** 1,247 characters

### Feedback:
- Strong use of action verbs: developed, managed, created
- Consider adding more quantifiable achievements
- Good structure with clear sections
- Skills section could be more specific to your target role

---
*Analysis completed using AI-enhanced tools*
```

The enhanced chat interface automatically:
- Detects user intent and selects appropriate tools
- Supports markdown, plain text, and code formatting
- Maintains conversation context
- Shows which tools were used for transparency

### 5. Streaming Chat Interface
```
User: "Can you help me prepare for a data scientist interview?"
Assistant: [Streaming response appears in real-time]
🤔 Analyzing your request...
🎯 Detected intent: INTERVIEW_PREP
⚙️ Generating interview questions for data scientist...
📝 I can help you prepare for interviews! What position are you interviewing for? I'll generate relevant questions and preparation tips.
📊 Tools used: ['mock_interview']
🎯 Action: request_interview_position
✅ Streaming completed!
```

The streaming chat interface provides:
- **Real-time responses**: See responses as they're generated
- **Progress indicators**: Visual feedback during processing
- **Stream cancellation**: Stop responses mid-stream
- **Smooth UX**: No waiting for complete responses
- **Server-Sent Events**: Efficient streaming protocol

## Project Structure

```
project/
├── README.md
├── requirements.txt
├── env.example
├── docker-compose.yml
├── Dockerfile.backend
├── data/                 # 20+ Career documents (markdown)
├── rag/
│   ├── indexing.py      # Document indexing and vector storage
│   └── retrieval.py     # RAG retrieval with multi-query reformulation
├── mcp_server/
│   ├── server.py        # FastMCP server with tools and resources
│   └── llm_client.py    # Multi-LLM client (Gemini + OpenAI)
├── prompts/
│   └── rag_prompt.py    # ReAct pattern prompt engineering
├── frontend/            # React frontend
│   ├── src/
│   ├── package.json
│   └── Dockerfile.frontend
├── evaluation/
│   ├── test_queries.json # 10 test queries for evaluation
│   └── results.md       # Comprehensive evaluation results
└── examples/
    └── demo.md          # Example interactions with ReAct pattern
```

## Evaluation Results

The system has been comprehensively evaluated with:

### Performance Metrics
- **Average Relevance Score**: 4.4/5
- **Tool Accuracy**: 93.5%
- **RAG Precision**: 78%
- **Average Response Time**: 2.3 seconds

### Test Coverage
- **10 Realistic Test Queries**: Covering resume analysis, interview preparation, career transitions
- **Manual Scoring**: 1-5 scale for relevance and quality
- **Precision Metrics**: Precision@3, Precision@5, Recall, F1 Score
- **Failure Mode Analysis**: 4 identified failure modes with mitigation strategies

### Key Findings
- Strong performance in core capabilities
- Good tool selection accuracy
- Effective RAG retrieval for career advice
- Robust fallback mechanisms when LLM unavailable

## Technologies Used

- **Backend**: Python, FastAPI, FAISS, SentenceTransformers
- **Frontend**: React 18, Material UI, Vite
- **LLM**: Google Gemini 1.5 Flash (default), OpenAI GPT-4o-mini (fallback)
- **Vector Database**: FAISS
- **MCP Framework**: FastMCP
- **Prompt Engineering**: ReAct pattern with structured reasoning
- **Containerization**: Docker, Docker Compose

## Development

### Adding New Documents
1. Add markdown files to `data/` directory
2. Rebuild the backend container: `docker-compose build backend`
3. Restart: `docker-compose up -d`

### Modifying the Frontend
1. Make changes in `frontend/src/`
2. Changes will auto-reload in development mode
3. For production, rebuild: `docker-compose build frontend`

### API Development
1. Modify `mcp_server/server.py`
2. Changes will auto-reload in development mode
3. Check API docs at http://localhost:8000/docs

### LLM Configuration
- Set `GOOGLE_API_KEY` in `.env` for Gemini (recommended)
- Set `OPENAI_API_KEY` as fallback
- Change `DEFAULT_LLM` in `.env` to switch providers

## Troubleshooting

### Common Issues
- **Port conflicts**: Ensure ports 3000 and 8000 are available
- **API connection**: Check that the backend is running and accessible
- **Document indexing**: Verify that markdown files are in the `data/` directory
- **Environment variables**: Ensure `.env` file is properly configured
- **LLM availability**: Check API keys and service status

### Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
```

### Health Check
```bash
curl http://localhost:8000/health
```

## License

MIT License - see LICENSE file for details. 