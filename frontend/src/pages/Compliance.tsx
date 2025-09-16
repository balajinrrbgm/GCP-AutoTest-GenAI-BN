import React from 'react';
import { Box, Typography, List, ListItem, ListItemText, Paper } from '@mui/material';

const Compliance: React.FC = () => {
  const standards = [
    'FDA 21 CFR Part 820',
    'IEC 62304', 
    'ISO 9001',
    'ISO 13485',
    'ISO 27001',
    'GDPR'
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Compliance Validation
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Validate test cases against healthcare regulatory standards
      </Typography>
      
      <Paper sx={{ mt: 3, p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Supported Standards:
        </Typography>
        <List>
          {standards.map((standard, index) => (
            <ListItem key={index}>
              <ListItemText primary={standard} />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default Compliance;