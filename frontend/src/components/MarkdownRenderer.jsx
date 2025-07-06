import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Box, Typography, Link } from '@mui/material';

const MarkdownRenderer = ({ children }) => {
  return (
    <ReactMarkdown
      components={{
        // Customize heading styles
        h1: ({ children }) => (
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mt: 2, mb: 1 }}>
            {children}
          </Typography>
        ),
        h2: ({ children }) => (
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mt: 2, mb: 1 }}>
            {children}
          </Typography>
        ),
        h3: ({ children }) => (
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mt: 1, mb: 0.5 }}>
            {children}
          </Typography>
        ),
        h4: ({ children }) => (
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 1 }}>
            {children}
          </Typography>
        ),
        
        // Customize paragraph styles
        p: ({ children }) => (
          <Typography variant="body1" sx={{ mb: 1, lineHeight: 1.6 }}>
            {children}
          </Typography>
        ),
        
        // Customize list styles
        ul: ({ children }) => (
          <Box component="ul" sx={{ pl: 2, mb: 1 }}>
            {children}
          </Box>
        ),
        ol: ({ children }) => (
          <Box component="ol" sx={{ pl: 2, mb: 1 }}>
            {children}
          </Box>
        ),
        li: ({ children }) => (
          <Typography component="li" variant="body1" sx={{ mb: 0.5 }}>
            {children}
          </Typography>
        ),
        
        // Customize code blocks
        code: ({ node, inline, className, children, ...props }) => {
          const match = /language-(\w+)/.exec(className || '');
          return !inline ? (
            <Box
              component="pre"
              sx={{
                bgcolor: 'grey.100',
                p: 2,
                borderRadius: 1,
                overflow: 'auto',
                fontSize: '0.875rem',
                fontFamily: 'monospace',
                mb: 1,
                border: '1px solid',
                borderColor: 'grey.300'
              }}
              {...props}
            >
              {children}
            </Box>
          ) : (
            <Box
              component="code"
              sx={{
                bgcolor: 'grey.100',
                px: 0.5,
                py: 0.25,
                borderRadius: 0.5,
                fontSize: '0.875rem',
                fontFamily: 'monospace',
                border: '1px solid',
                borderColor: 'grey.300'
              }}
              {...props}
            >
              {children}
            </Box>
          );
        },
        
        // Customize blockquotes
        blockquote: ({ children }) => (
          <Box
            sx={{
              borderLeft: '4px solid',
              borderColor: 'primary.main',
              pl: 2,
              ml: 0,
              my: 1,
              bgcolor: 'grey.50',
              py: 1
            }}
          >
            <Typography variant="body1" sx={{ fontStyle: 'italic' }}>
              {children}
            </Typography>
          </Box>
        ),
        
        // Customize links
        a: ({ href, children }) => (
          <Link href={href} target="_blank" rel="noopener noreferrer" sx={{ color: 'primary.main' }}>
            {children}
          </Link>
        ),
        
        // Customize strong text
        strong: ({ children }) => (
          <Typography component="span" sx={{ fontWeight: 'bold' }}>
            {children}
          </Typography>
        ),
        
        // Customize emphasis text
        em: ({ children }) => (
          <Typography component="span" sx={{ fontStyle: 'italic' }}>
            {children}
          </Typography>
        ),
        
        // Customize horizontal rules
        hr: () => (
          <Box
            sx={{
              border: 'none',
              borderTop: '1px solid',
              borderColor: 'grey.300',
              my: 2
            }}
          />
        ),
        
        // Customize table styles
        table: ({ children }) => (
          <Box
            component="table"
            sx={{
              width: '100%',
              borderCollapse: 'collapse',
              mb: 2,
              border: '1px solid',
              borderColor: 'grey.300'
            }}
          >
            {children}
          </Box>
        ),
        th: ({ children }) => (
          <Box
            component="th"
            sx={{
              border: '1px solid',
              borderColor: 'grey.300',
              p: 1,
              bgcolor: 'grey.100',
              fontWeight: 'bold',
              textAlign: 'left'
            }}
          >
            {children}
          </Box>
        ),
        td: ({ children }) => (
          <Box
            component="td"
            sx={{
              border: '1px solid',
              borderColor: 'grey.300',
              p: 1
            }}
          >
            {children}
          </Box>
        )
      }}
    >
      {children}
    </ReactMarkdown>
  );
};

export default MarkdownRenderer; 