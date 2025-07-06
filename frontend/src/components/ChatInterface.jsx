import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  IconButton,
  Chip,
  Divider,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Card,
  CardContent
} from '@mui/material';
import {
  Send as SendIcon,
  FormatBold as FormatBoldIcon,
  Code as CodeIcon,
  TextFields as TextFieldsIcon,
  Refresh as RefreshIcon,
  AutoAwesome as AutoAwesomeIcon
} from '@mui/icons-material';
import MarkdownRenderer from './MarkdownRenderer';
import axios from 'axios';

const API_BASE = '/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [formatPreference, setFormatPreference] = useState('markdown');
  const [autoToolSelection, setAutoToolSelection] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (content, role = 'user', metadata = {}) => {
    const newMessage = {
      id: Date.now(),
      content,
      role,
      timestamp: new Date(),
      ...metadata
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);

    // Add user message
    addMessage(userMessage, 'user');

    try {
      // Prepare conversation history for context
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await axios.post(`${API_BASE}/chat/enhanced`, {
        message: userMessage,
        conversation_history: conversationHistory,
        format_preference: formatPreference,
        auto_tool_selection: autoToolSelection
      });

      const { response: assistantResponse, action, tools_used, reasoning } = response.data;

      // Add assistant message with metadata
      addMessage(assistantResponse, 'assistant', {
        action,
        toolsUsed: tools_used || [],
        reasoning
      });

    } catch (error) {
      console.error('Chat error:', error);
      addMessage(
        'Sorry, I encountered an error while processing your request. Please try again.',
        'assistant',
        { action: 'error' }
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const renderMessage = (message) => {
    const isUser = message.role === 'user';
    
    return (
      <Box
        key={message.id}
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2
        }}
      >
        <Paper
          sx={{
            p: 2,
            maxWidth: '70%',
            bgcolor: isUser ? 'primary.main' : 'grey.50',
            color: isUser ? 'white' : 'text.primary',
            position: 'relative'
          }}
        >
          {isUser ? (
            <Typography>{message.content}</Typography>
          ) : (
            <Box>
              {formatPreference === 'markdown' ? (
                <MarkdownRenderer>{message.content}</MarkdownRenderer>
              ) : formatPreference === 'code' ? (
                <Box
                  component="pre"
                  sx={{
                    bgcolor: 'grey.100',
                    p: 2,
                    borderRadius: 1,
                    overflow: 'auto',
                    fontSize: '0.875rem'
                  }}
                >
                  {message.content}
                </Box>
              ) : (
                <Typography sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </Typography>
              )}
              
              {/* Show metadata for assistant messages */}
              {message.toolsUsed && message.toolsUsed.length > 0 && (
                <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {message.toolsUsed.map((tool, index) => (
                    <Chip
                      key={index}
                      label={tool}
                      size="small"
                      color="secondary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              )}
            </Box>
          )}
        </Paper>
      </Box>
    );
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header with controls */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AutoAwesomeIcon />
              AI Career Coach Chat
            </Typography>
            <IconButton onClick={clearChat} size="small" title="Clear chat">
              <RefreshIcon />
            </IconButton>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Format</InputLabel>
              <Select
                value={formatPreference}
                label="Format"
                onChange={(e) => setFormatPreference(e.target.value)}
              >
                <MenuItem value="markdown">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <FormatBoldIcon fontSize="small" />
                    Markdown
                  </Box>
                </MenuItem>
                <MenuItem value="plain">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TextFieldsIcon fontSize="small" />
                    Plain Text
                  </Box>
                </MenuItem>
                <MenuItem value="code">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CodeIcon fontSize="small" />
                    Code
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>
            
            <Chip
              label={autoToolSelection ? 'Auto Tools ON' : 'Auto Tools OFF'}
              color={autoToolSelection ? 'success' : 'default'}
              variant="outlined"
              size="small"
              onClick={() => setAutoToolSelection(!autoToolSelection)}
              clickable
            />
          </Box>
        </CardContent>
      </Card>

      {/* Messages area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 2,
          bgcolor: 'grey.50',
          borderRadius: 1,
          mb: 2
        }}
      >
        {messages.length === 0 ? (
          <Box sx={{ textAlign: 'center', color: 'text.secondary', mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Welcome to Career Coach AI!
            </Typography>
            <Typography variant="body2">
              I can help you with resume analysis, interview preparation, and career advice.
              <br />
              Just ask me anything about your career development!
            </Typography>
          </Box>
        ) : (
          messages.map(renderMessage)
        )}
        
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Box>

      {/* Input area */}
      <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          variant="outlined"
          placeholder="Ask me about resume analysis, interview preparation, or career advice..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
          sx={{ flex: 1 }}
        />
        <Button
          variant="contained"
          onClick={handleSendMessage}
          disabled={loading || !input.trim()}
          sx={{ minWidth: 56, height: 56 }}
        >
          {loading ? <CircularProgress size={24} /> : <SendIcon />}
        </Button>
      </Box>

      {/* Quick action suggestions */}
      {messages.length === 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Try asking:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {[
              "Can you analyze my resume?",
              "Help me prepare for a software engineer interview",
              "How do I transition to data science?",
              "What are good networking strategies?"
            ].map((suggestion, index) => (
              <Chip
                key={index}
                label={suggestion}
                size="small"
                variant="outlined"
                clickable
                onClick={() => setInput(suggestion)}
              />
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default ChatInterface; 