import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import AcceptInvite from './pages/AcceptInvite';
import NotFound from './pages/NotFound';
import Dashboard from './pages/Dashboard';
import InventoryPage from './pages/InventoryPage';
import ForecastPage from './pages/ForecastPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ProductsPage from './pages/ProductsPage';
import SuppliersPage from './pages/SuppliersPage';
import CompetitorsPage from './pages/CompetitorsPage';
import CustomersPage from './pages/CustomersPage';
import BatchesPage from './pages/BatchesPage';
import ReportsPage from './pages/ReportsPage';
import SalesPage from './pages/SalesPage';
import AlertsPage from './pages/AlertsPage';
import UsersPage from './pages/UsersPage';
import AdminPortal from './pages/AdminPortal';
import AdminCompetitorsPage from './pages/AdminCompetitorsPage';
import OrganizationPage from './pages/OrganizationPage';
import ActivityPage from './pages/ActivityPage';
import ProtectedRoute from './components/ProtectedRoute';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
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
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          borderRadius: 8,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 6,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/invite" element={<AcceptInvite />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/inventory" element={
              <ProtectedRoute>
                <InventoryPage />
              </ProtectedRoute>
            } />
            <Route path="/forecast" element={
              <ProtectedRoute requiredRole="manager">
                <ForecastPage />
              </ProtectedRoute>
            } />
            <Route path="/analytics" element={
              <ProtectedRoute>
                <AnalyticsPage />
              </ProtectedRoute>
            } />
            <Route path="/products" element={
              <ProtectedRoute requiredRole="manager">
                <ProductsPage />
              </ProtectedRoute>
            } />
            <Route path="/sales" element={
              <ProtectedRoute>
                <SalesPage />
              </ProtectedRoute>
            } />
            <Route path="/alerts" element={
              <ProtectedRoute requiredRole="manager">
                <AlertsPage />
              </ProtectedRoute>
            } />
            <Route path="/suppliers" element={
              <ProtectedRoute>
                <SuppliersPage />
              </ProtectedRoute>
            } />
            <Route path="/competitors" element={
              <ProtectedRoute>
                <CompetitorsPage />
              </ProtectedRoute>
            } />
            <Route path="/customers" element={
              <ProtectedRoute>
                <CustomersPage />
              </ProtectedRoute>
            } />
            <Route path="/batches" element={
              <ProtectedRoute requiredRole="manager">
                <BatchesPage />
              </ProtectedRoute>
            } />
            <Route path="/reports" element={
              <ProtectedRoute>
                <ReportsPage />
              </ProtectedRoute>
            } />
            <Route path="/users" element={
              <ProtectedRoute requiredRole="admin">
                <UsersPage />
              </ProtectedRoute>
            } />
            <Route path="/admin" element={
              <ProtectedRoute requiredRole="admin">
                <AdminPortal />
              </ProtectedRoute>
            } />
            <Route path="/admin/competitors" element={
              <ProtectedRoute requiredRole="admin">
                <AdminCompetitorsPage />
              </ProtectedRoute>
            } />
            <Route path="/organization" element={
              <ProtectedRoute requiredRole="manager">
                <OrganizationPage />
              </ProtectedRoute>
            } />
            <Route path="/activity" element={
              <ProtectedRoute requiredRole="manager">
                <ActivityPage />
              </ProtectedRoute>
            } />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;