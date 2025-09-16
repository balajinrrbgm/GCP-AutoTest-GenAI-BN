import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { SnackbarProvider } from 'notistack';

// Components
import Navbar from './components/Layout/Navbar';
import Sidebar from './components/Layout/Sidebar';
import Dashboard from './pages/Dashboard';
import Requirements from './pages/Requirements';
import TestCases from './pages/TestCases';
import Compliance from './pages/Compliance';
import ALMIntegration from './pages/ALMIntegration';
import Settings from './pages/Settings';
import Login from './pages/Login';

// Context providers
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext';

// Styles
import { Box, Container } from '@mui/material';

// Theme configuration
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
  components: {
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1e1e1e',
          color: 'white',
        },
      },
    },
  },
});

// Protected Route component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

// Main Layout component
const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Navbar onMenuClick={handleSidebarToggle} />
      <Sidebar open={sidebarOpen} onToggle={handleSidebarToggle} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8, // Account for navbar height
          ml: sidebarOpen ? '240px' : '60px',
          transition: 'margin-left 0.3s',
        }}
      >
        <Container maxWidth="xl">
          {children}
        </Container>
      </Box>
    </Box>
  );
};

// Main App component
const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
        <AuthProvider>
          <AppProvider>
            <Router>
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={<Login />} />
                
                {/* Protected routes */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <Dashboard />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <Dashboard />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/requirements"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <Requirements />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/test-cases"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <TestCases />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/compliance"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <Compliance />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/alm-integration"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <ALMIntegration />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <Settings />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                
                {/* Catch all route */}
                <Route path="*" element={<Navigate to="/" />} />
              </Routes>
            </Router>
          </AppProvider>
        </AuthProvider>
      </SnackbarProvider>
    </ThemeProvider>
  );
};

export default App;