import React from 'react';
import { Navigate } from 'react-router-dom';
import { CircularProgress, Box, Alert } from '@mui/material';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, requiredRole }) => {
  const { isAuthenticated, loading, hasRole } = useAuth();

  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
        p={3}
      >
        <Alert severity="error">
          Access denied. You need {requiredRole} role or higher to access this page.
        </Alert>
      </Box>
    );
  }

  return children;
};

export default ProtectedRoute;