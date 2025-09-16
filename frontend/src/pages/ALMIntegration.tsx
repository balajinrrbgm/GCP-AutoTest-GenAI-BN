import React from 'react';
import { Box, Typography, List, ListItem, ListItemText, Paper } from '@mui/material';

const ALMIntegration: React.FC = () => {
  const platforms = [
    'Jira',
    'Polarion',
    'Azure DevOps',
    'TestLink', 
    'Xray'
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        ALM Integration
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Connect with enterprise Application Lifecycle Management platforms
      </Typography>
      
      <Paper sx={{ mt: 3, p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Supported Platforms:
        </Typography>
        <List>
          {platforms.map((platform, index) => (
            <ListItem key={index}>
              <ListItemText primary={platform} />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default ALMIntegration;