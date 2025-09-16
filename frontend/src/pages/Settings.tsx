import React from 'react';
import { Box, Typography, List, ListItem, ListItemText, Paper } from '@mui/material';

const Settings: React.FC = () => {
  const configOptions = [
    'AI Model Settings',
    'Compliance Rules',
    'ALM Platform Connections',
    'User Preferences',
    'System Configuration'
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Configure system preferences and user settings
      </Typography>
      
      <Paper sx={{ mt: 3, p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Configuration Options:
        </Typography>
        <List>
          {configOptions.map((option, index) => (
            <ListItem key={index}>
              <ListItemText primary={option} />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default Settings;