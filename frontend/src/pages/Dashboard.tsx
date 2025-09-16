import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
} from '@mui/material';
import {
  Description,
  Assignment,
  CheckCircle,
  Error,
  Warning,
  TrendingUp,
  Security,
  Speed,
} from '@mui/icons-material';

// Mock data - would come from API
const dashboardData = {
  stats: {
    totalRequirements: 156,
    totalTestCases: 1247,
    passedTests: 1089,
    failedTests: 23,
    pendingTests: 135,
    complianceScore: 94,
  },
  recentActivity: [
    {
      id: 1,
      action: 'Generated test cases for REQ-001',
      timestamp: '2 hours ago',
      user: 'John Doe',
      type: 'generation',
    },
    {
      id: 2,
      action: 'Compliance validation completed',
      timestamp: '4 hours ago',
      user: 'System',
      type: 'compliance',
    },
    {
      id: 3,
      action: 'New requirements uploaded',
      timestamp: '6 hours ago',
      user: 'Jane Smith',
      type: 'upload',
    },
  ],
  complianceStatus: [
    { standard: 'FDA 21 CFR Part 820', status: 'compliant', score: 98 },
    { standard: 'IEC 62304', status: 'compliant', score: 96 },
    { standard: 'ISO 13485', status: 'warning', score: 89 },
    { standard: 'GDPR', status: 'compliant', score: 95 },
  ],
};

const Dashboard: React.FC = () => {
  const { stats, recentActivity, complianceStatus } = dashboardData;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'generation':
        return <Assignment />;
      case 'compliance':
        return <Security />;
      case 'upload':
        return <Description />;
      default:
        return <Assignment />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="subtitle1" color="textSecondary" gutterBottom>
        Healthcare Test Case Generation System Overview
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <Description />
                </Avatar>
                <Box>
                  <Typography variant="h4">{stats.totalRequirements}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Requirements
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
                  <Assignment />
                </Avatar>
                <Box>
                  <Typography variant="h4">{stats.totalTestCases}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Test Cases
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <CheckCircle />
                </Avatar>
                <Box>
                  <Typography variant="h4">{stats.passedTests}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Passed Tests
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                  <Speed />
                </Avatar>
                <Box>
                  <Typography variant="h4">{stats.complianceScore}%</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Compliance Score
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Compliance Status */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Compliance Status
            </Typography>
            <List>
              {complianceStatus.map((item, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    {item.status === 'compliant' ? (
                      <CheckCircle color="success" />
                    ) : item.status === 'warning' ? (
                      <Warning color="warning" />
                    ) : (
                      <Error color="error" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.standard}
                    secondary={
                      <Box>
                        <Box display="flex" alignItems="center" mt={1}>
                          <Box width="100%" mr={1}>
                            <LinearProgress
                              variant="determinate"
                              value={item.score}
                              color={getStatusColor(item.status) as any}
                            />
                          </Box>
                          <Typography variant="body2" color="textSecondary">
                            {item.score}%
                          </Typography>
                        </Box>
                      </Box>
                    }
                  />
                  <Chip
                    label={item.status}
                    color={getStatusColor(item.status) as any}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <List>
              {recentActivity.map((activity) => (
                <ListItem key={activity.id}>
                  <ListItemIcon>{getActivityIcon(activity.type)}</ListItemIcon>
                  <ListItemText
                    primary={activity.action}
                    secondary={`${activity.user} • ${activity.timestamp}`}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Test Execution Summary */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Test Execution Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Box textAlign="center">
                  <Typography variant="h3" color="success.main">
                    {stats.passedTests}
                  </Typography>
                  <Typography variant="body1">Passed</Typography>
                  <LinearProgress
                    variant="determinate"
                    value={(stats.passedTests / stats.totalTestCases) * 100}
                    color="success"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box textAlign="center">
                  <Typography variant="h3" color="error.main">
                    {stats.failedTests}
                  </Typography>
                  <Typography variant="body1">Failed</Typography>
                  <LinearProgress
                    variant="determinate"
                    value={(stats.failedTests / stats.totalTestCases) * 100}
                    color="error"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box textAlign="center">
                  <Typography variant="h3" color="warning.main">
                    {stats.pendingTests}
                  </Typography>
                  <Typography variant="body1">Pending</Typography>
                  <LinearProgress
                    variant="determinate"
                    value={(stats.pendingTests / stats.totalTestCases) * 100}
                    color="warning"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;