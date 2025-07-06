# Career Coach AI Frontend

A modern React frontend for the Career Coach AI application, built with Material UI.

## Features

- **Resume Analysis**: Upload and analyze resumes with AI-powered feedback
- **Mock Interview**: Get role-specific interview questions and preparation tips
- **Career Advice**: Ask career questions and get personalized guidance
- **Modern UI**: Beautiful, responsive interface built with Material UI
- **Real-time Chat**: Interactive conversation history with the AI assistant

## Setup

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

3. **Build for Production**:
   ```bash
   npm run build
   ```

## Usage

1. **Resume Analysis Tab**:
   - Paste your resume text in the text area
   - Click "Analyze Resume" to get feedback
   - View detailed suggestions and improvements

2. **Mock Interview Tab**:
   - Enter the position you're interviewing for
   - Click "Get Interview Questions" for role-specific questions
   - Prepare with targeted interview preparation

3. **Career Advice Tab**:
   - Ask any career-related question
   - Get personalized advice from the AI
   - View conversation history

## API Integration

The frontend connects to the MCP server running on `localhost:8000` through a proxy configuration in `vite.config.js`.

## Technologies Used

- **React 18**: Modern React with hooks
- **Material UI**: Professional UI components
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client for API calls

## Development

- **Port**: Runs on `http://localhost:3000`
- **Hot Reload**: Automatic reload on file changes
- **Proxy**: API calls are proxied to the MCP server

## Troubleshooting

- Ensure the MCP server is running on port 8000
- Check browser console for any API errors
- Verify all dependencies are installed correctly 