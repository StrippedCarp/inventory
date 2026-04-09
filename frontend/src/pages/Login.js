import React, { useState } from 'react';
import { Navigate, Link } from 'react-router-dom';
import { 
  Container, 
  Paper, 
  TextField, 
  Button, 
  Typography, 
  Alert, 
  Box,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [registerData, setRegisterData] = useState({ 
    username: '', 
    email: '', 
    password: '', 
    confirmPassword: '',
    role: 'viewer'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(loginData);
    if (result.success) {
      // Navigation handled by AuthContext
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    if (registerData.password !== registerData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: registerData.username,
          email: registerData.email,
          password: registerData.password,
          role: registerData.role
        })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Registration successful! You can now login.');
        setTabValue(0); // Switch to login tab
        setRegisterData({ username: '', email: '', password: '', confirmPassword: '', role: 'viewer' });
      } else {
        setError(data.message || 'Registration failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
    setLoading(false);
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" align="center" gutterBottom>
            Inventory Management
          </Typography>
          
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} centered>
            <Tab label="Login" />
            <Tab label="Register" />
          </Tabs>

          {error && <Alert severity="error" sx={{ mt: 2, mb: 2 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mt: 2, mb: 2 }}>{success}</Alert>}
          
          {tabValue === 0 && (
            <Box component="form" onSubmit={handleLogin} sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Username"
                margin="normal"
                value={loginData.username}
                onChange={(e) => setLoginData({...loginData, username: e.target.value})}
                required
              />
              <TextField
                fullWidth
                label="Password"
                type="password"
                margin="normal"
                value={loginData.password}
                onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                required
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
              
              <Typography variant="body2" color="textSecondary" align="center">
                Demo accounts: admin/password123, manager/password123, viewer/password123
              </Typography>
            </Box>
          )}

          {tabValue === 1 && (
            <Box component="form" onSubmit={handleRegister} sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Username"
                margin="normal"
                value={registerData.username}
                onChange={(e) => setRegisterData({...registerData, username: e.target.value})}
                required
              />
              <TextField
                fullWidth
                label="Email"
                type="email"
                margin="normal"
                value={registerData.email}
                onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                required
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Role</InputLabel>
                <Select
                  value={registerData.role}
                  onChange={(e) => setRegisterData({...registerData, role: e.target.value})}
                  label="Role"
                >
                  <MenuItem value="viewer">Viewer</MenuItem>
                  <MenuItem value="manager">Manager</MenuItem>
                  <MenuItem value="admin">Admin</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Password"
                type="password"
                margin="normal"
                value={registerData.password}
                onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                required
              />
              <TextField
                fullWidth
                label="Confirm Password"
                type="password"
                margin="normal"
                value={registerData.confirmPassword}
                onChange={(e) => setRegisterData({...registerData, confirmPassword: e.target.value})}
                required
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? 'Registering...' : 'Register'}
              </Button>
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;