import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  IconButton,
  Chip,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Alert,
  LinearProgress
} from '@mui/material';
import {
  Send as SendIcon,
  FormatBold as FormatBoldIcon,
  Code as CodeIcon,
  TextFields as TextFieldsIcon,
  Refresh as RefreshIcon,
  AutoAwesome as AutoAwesomeIcon,
  Stop as StopIcon
} from '@mui/icons-material';
import MarkdownRenderer from './MarkdownRenderer';
import axios from 'axios';

const API_BASE = '/api';

const StreamingChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [formatPreference, setFormatPreference] = useState('markdown');
  const [autoToolSelection, setAutoToolSelection] = useState(true);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const [streamingMetadata, setStreamingMetadata] = useState(null);
  const [streamingStatus, setStreamingStatus] = useState('');
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);
  const currentStreamingMessageRef = useRef('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamingMessage]);

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

  const handleStreamingChat = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);
    setStreaming(true);
    setCurrentStreamingMessage('');
    setStreamingMetadata(null);
    setStreamingStatus('');
    currentStreamingMessageRef.current = '';

    // Add user message
    addMessage(userMessage, 'user');

    // Prepare conversation history for context
    const conversationHistory = messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));

    try {
      // Create abort controller for cancellation
      abortControllerRef.current = new AbortController();

      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          conversation_history: conversationHistory,
          format_preference: formatPreference,
          auto_tool_selection: autoToolSelection
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          // If stream ends without 'done' event, save any accumulated content
          if (currentStreamingMessageRef.current.trim()) {
            addMessage(currentStreamingMessageRef.current, 'assistant', {
              action: streamingMetadata?.action,
              toolsUsed: streamingMetadata?.tools_used || [],
              reasoning: streamingMetadata?.reasoning
            });
          }
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              switch (data.type) {
                case 'thinking':
                  setStreamingStatus(data.content);
                  break;
                  
                case 'intent':
                  setStreamingStatus(data.content);
                  break;
                  
                case 'processing':
                  setStreamingStatus(data.content);
                  break;
                  
                case 'tool_call':
                  setStreamingStatus(data.content);
                  break;
                  
                case 'tool_result':
                  setStreamingStatus(data.content);
                  break;
                  
                case 'llm_processing':
                  setStreamingStatus(data.content);
                  break;
                  
                case 'content':
                  setCurrentStreamingMessage(prev => prev + data.content);
                  currentStreamingMessageRef.current += data.content;
                  setStreamingStatus(''); // Clear status when content starts
                  break;
                  
                case 'metadata':
                  setStreamingMetadata(data);
                  break;
                  
                case 'error':
                  setCurrentStreamingMessage(data.content);
                  currentStreamingMessageRef.current = data.content;
                  setStreamingStatus('');
                  break;
                  
                case 'done':
                  // Finalize the message using the ref to ensure we have the latest content
                  if (currentStreamingMessageRef.current.trim()) {
                    addMessage(currentStreamingMessageRef.current, 'assistant', {
                      action: streamingMetadata?.action,
                      toolsUsed: streamingMetadata?.tools_used || [],
                      reasoning: streamingMetadata?.reasoning
                    });
                  }
                  setCurrentStreamingMessage('');
                  setStreamingMetadata(null);
                  setStreamingStatus('');
                  currentStreamingMessageRef.current = '';
                  setStreaming(false);
                  setLoading(false);
                  return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Request was aborted');
      } else {
        console.error('Streaming chat error:', error);
        addMessage(
          'Sorry, I encountered an error while processing your request. Please try again.',
          'assistant',
          { action: 'error' }
        );
      }
    } finally {
      setStreaming(false);
      setLoading(false);
      setCurrentStreamingMessage('');
      setStreamingMetadata(null);
      setStreamingStatus('');
      currentStreamingMessageRef.current = '';
    }
  };

  const stopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleStreamingChat();
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
    setCurrentStreamingMessage('');
    setStreamingMetadata(null);
    setStreamingStatus('');
    currentStreamingMessageRef.current = '';
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header with controls */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AutoAwesomeIcon />
              AI Career Coach Chat (Streaming)
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
        {messages.length === 0 && !streaming ? (
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
          <>
            {messages.map(renderMessage)}
            
            {/* Show streaming status */}
            {streaming && streamingStatus && !currentStreamingMessage && (
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'flex-start',
                  mb: 2
                }}
              >
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '70%',
                    bgcolor: 'grey.50',
                    position: 'relative'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={16} />
                    <Typography variant="body2" color="text.secondary">
                      {streamingStatus}
                    </Typography>
                  </Box>
                </Paper>
              </Box>
            )}
            
            {/* Show streaming message */}
            {streaming && currentStreamingMessage && (
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'flex-start',
                  mb: 2
                }}
              >
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '70%',
                    bgcolor: 'grey.50',
                    position: 'relative'
                  }}
                >
                  <Box>
                    {formatPreference === 'markdown' ? (
                      <MarkdownRenderer>{currentStreamingMessage}</MarkdownRenderer>
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
                        {currentStreamingMessage}
                      </Box>
                    ) : (
                      <Typography sx={{ whiteSpace: 'pre-wrap' }}>
                        {currentStreamingMessage}
                      </Typography>
                    )}
                    
                    {/* Show streaming indicator */}
                    <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CircularProgress size={16} />
                      <Typography variant="caption" color="text.secondary">
                        AI is thinking...
                      </Typography>
                    </Box>
                  </Box>
                </Paper>
              </Box>
            )}
          </>
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
          onClick={streaming ? stopStreaming : handleStreamingChat}
          disabled={loading && !streaming}
          sx={{ minWidth: 56, height: 56 }}
        >
          {streaming ? <StopIcon /> : loading ? <CircularProgress size={24} /> : <SendIcon />}
        </Button>
      </Box>

      {/* Quick action suggestions */}
      {messages.length === 0 && !streaming && (
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

export default StreamingChatInterface; 