import React, { useState } from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Tabs,
  Tab,
  Card,
  CardContent,
  TextField,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material'
import {
  Work as WorkIcon,
  Description as DescriptionIcon,
  School as SchoolIcon,
  Send as SendIcon,
  Chat as ChatIcon,
  Stream as StreamIcon
} from '@mui/icons-material'
import axios from 'axios'
import ChatInterface from './components/ChatInterface'
import StreamingChatInterface from './components/StreamingChatInterface'

const API_BASE = '/api'

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

function App() {
  const [tabValue, setTabValue] = useState(0)
  const [loading, setLoading] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [resumeText, setResumeText] = useState('')
  const [position, setPosition] = useState('')

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue)
    setMessages([])
  }

  const addMessage = (text, isUser = false, data = null) => {
    setMessages(prev => [...prev, { text, isUser, data, timestamp: new Date() }])
  }

  const handleResumeAnalysis = async () => {
    if (!resumeText.trim()) return
    
    setLoading(true)
    addMessage(resumeText, true)
    
    try {
      const response = await axios.post(`${API_BASE}/tools/analyze_resume`, {
        resume_text: resumeText
      })
      
      const feedback = response.data.feedback
      addMessage('Resume Analysis Results:', false, feedback)
    } catch (error) {
      addMessage('Error analyzing resume. Please try again.', false)
      console.error('Resume analysis error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleMockInterview = async () => {
    if (!position.trim()) return
    
    setLoading(true)
    addMessage(`I need interview questions for: ${position}`, true)
    
    try {
      const response = await axios.post(`${API_BASE}/tools/mock_interview`, {
        position: position
      })
      
      const questions = response.data.questions
      addMessage('Mock Interview Questions:', false, questions)
    } catch (error) {
      addMessage('Error getting interview questions. Please try again.', false)
      console.error('Mock interview error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCareerAdvice = async () => {
    if (!input.trim()) return
    
    setLoading(true)
    addMessage(input, true)
    
    try {
      const response = await axios.post(`${API_BASE}/resources/career_guides/featured`, {
        query: input,
        top_k: 3
      })
      
      const tips = response.data.tips
      addMessage('Career Advice:', false, tips)
    } catch (error) {
      addMessage('Error getting career advice. Please try again.', false)
      console.error('Career advice error:', error)
    } finally {
      setLoading(false)
      setInput('')
    }
  }

  const renderMessage = (message) => {
    if (message.isUser) {
      return (
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'primary.light', color: 'white' }}>
          <Typography>{message.text}</Typography>
        </Paper>
      )
    }

    return (
      <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
        <Typography variant="h6" gutterBottom>{message.text}</Typography>
        {message.data && (
          <Box>
            {Array.isArray(message.data) ? (
              <List>
                {message.data.map((item, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={item} />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography>{message.data}</Typography>
            )}
          </Box>
        )}
      </Paper>
    )
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <WorkIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Career Coach AI
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="career coach tabs">
            <Tab icon={<DescriptionIcon />} label="Resume Analysis" />
            <Tab icon={<SchoolIcon />} label="Mock Interview" />
            <Tab icon={<WorkIcon />} label="Career Advice" />
            <Tab icon={<ChatIcon />} label="Chat" />
            <Tab icon={<StreamIcon />} label="Streaming Chat" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Resume Analysis
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={8}
                variant="outlined"
                label="Paste your resume here"
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                sx={{ mb: 2 }}
              />
              <Button
                variant="contained"
                onClick={handleResumeAnalysis}
                disabled={loading || !resumeText.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
              >
                Analyze Resume
              </Button>
            </CardContent>
          </Card>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Mock Interview Preparation
              </Typography>
              <TextField
                fullWidth
                variant="outlined"
                label="Enter the position you're interviewing for"
                value={position}
                onChange={(e) => setPosition(e.target.value)}
                sx={{ mb: 2 }}
                placeholder="e.g., Software Engineer, Data Scientist, Product Manager"
              />
              <Button
                variant="contained"
                onClick={handleMockInterview}
                disabled={loading || !position.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
              >
                Get Interview Questions
              </Button>
            </CardContent>
          </Card>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Career Advice Q&A
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  fullWidth
                  variant="outlined"
                  label="Ask a career question"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="e.g., How do I transition from marketing to data science?"
                />
                <Button
                  variant="contained"
                  onClick={handleCareerAdvice}
                  disabled={loading || !input.trim()}
                  startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                >
                  Ask
                </Button>
              </Box>
            </CardContent>
          </Card>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <ChatInterface />
        </TabPanel>

        <TabPanel value={tabValue} index={4}>
          <StreamingChatInterface />
        </TabPanel>

        {messages.length > 0 && tabValue !== 3 && tabValue !== 4 && (
          <Card sx={{ mt: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Conversation History
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {messages.map((message, index) => (
                <Box key={index}>
                  {renderMessage(message)}
                </Box>
              ))}
            </CardContent>
          </Card>
        )}
      </Container>
    </Box>
  )
}

export default App 