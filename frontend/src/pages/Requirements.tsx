import React from 'react';
import { Box, Typography, Paper, Button } from '@mui/material';

const Requirements: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Requirements Management
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Upload and manage healthcare software requirements documents
      </Typography>
      
      <Paper 
        sx={{ 
          mt: 3, 
          p: 4, 
          border: '2px dashed #ccc', 
          textAlign: 'center',
          minHeight: 200,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center'
        }}
      >
        <Typography variant="h6" gutterBottom>
          Drag & drop requirement documents here or click to browse
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Supported formats: PDF, Word, XML, Markdown
        </Typography>
        <Button variant="contained" sx={{ mt: 2, maxWidth: 200, alignSelf: 'center' }}>
          Browse Files
        </Button>
      </Paper>
    </Box>
  );
};

export default Requirements;