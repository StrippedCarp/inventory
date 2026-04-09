import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  Grid,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Badge,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as ResolveIcon,
  CheckCircle,
  Refresh as RefreshIcon,
  Notifications as NotificationIcon,
  TrendingDown as LowStockIcon,
  Schedule as ExpiryIcon,
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { alertsAPI } from '../services/api';

const AlertsPage = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [resolveDialog, setResolveDialog] = useState(null);
  const [resolveNote, setResolveNote] = useState('');

  const [alertStats, setAlertStats] = useState({
    critical: 0,
    warning: 0,
    info: 0,
    resolved: 0,
  });

  // Mock data for demonstration
  const mockAlerts = [
      {
        id: 1,
        type: 'low_stock',
        severity: 'critical',
        title: 'Critical Low Stock',
        message: 'Laptop inventory is critically low (2 units remaining)',
        product_name: 'Laptop',
        product_id: 1,
        current_stock: 2,
        min_threshold: 10,
        status: 'active',
        created_at: '2024-01-21T08:00:00Z',
        resolved_at: null,
        resolved_by: null,
        resolution_note: null,
      },
      {
        id: 2,
        type: 'low_stock',
        severity: 'warning',
        title: 'Low Stock Warning',
        message: 'Mouse inventory is running low (8 units remaining)',
        product_name: 'Mouse',
        product_id: 2,
        current_stock: 8,
        min_threshold: 15,
        status: 'active',
        created_at: '2024-01-21T10:30:00Z',
        resolved_at: null,
        resolved_by: null,
        resolution_note: null,
      },
      {
        id: 3,
        type: 'expiry',
        severity: 'warning',
        title: 'Product Expiry Warning',
        message: 'Batteries will expire in 7 days',
        product_name: 'Batteries',
        product_id: 3,
        expiry_date: '2024-01-28',
        status: 'active',
        created_at: '2024-01-21T12:00:00Z',
        resolved_at: null,
        resolved_by: null,
        resolution_note: null,
      },
      {
        id: 4,
        type: 'reorder',
        severity: 'info',
        title: 'Reorder Suggestion',
        message: 'Consider reordering Keyboards based on sales trend',
        product_name: 'Keyboard',
        product_id: 4,
        suggested_quantity: 50,
        status: 'resolved',
        created_at: '2024-01-20T14:00:00Z',
        resolved_at: '2024-01-21T09:00:00Z',
        resolved_by: 'admin',
        resolution_note: 'Order placed with supplier',
      },
      {
        id: 5,
        type: 'system',
        severity: 'info',
        title: 'System Notification',
        message: 'Weekly inventory report is ready for review',
        status: 'active',
        created_at: '2024-01-21T06:00:00Z',
        resolved_at: null,
        resolved_by: null,
        resolution_note: null,
      },
    ];

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await alertsAPI.getAll();
      setAlerts(response.data.alerts || response.data || []);
      calculateStats(response.data.alerts || response.data || []);
    } catch (err) {
      console.error('Alerts fetch error:', err);
      setAlerts(mockAlerts);
      calculateStats(mockAlerts);
      setError('Using demo data - backend not connected');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (alertsData) => {
    const stats = alertsData.reduce((acc, alert) => {
      if (alert.status === 'resolved') {
        acc.resolved++;
      } else {
        acc[alert.severity]++;
      }
      return acc;
    }, { critical: 0, warning: 0, info: 0, resolved: 0 });

    setAlertStats(stats);
  };

  const handleResolveAlert = (alert) => {
    setResolveDialog(alert);
    setResolveNote('');
  };

  const confirmResolve = () => {
    if (resolveDialog) {
      setAlerts(alerts.map(alert => 
        alert.id === resolveDialog.id 
          ? {
              ...alert,
              status: 'resolved',
              resolved_at: new Date().toISOString(),
              resolved_by: 'current_user',
              resolution_note: resolveNote || 'Resolved manually'
            }
          : alert
      ));
      
      // Update stats
      setAlertStats(prev => ({
        ...prev,
        [resolveDialog.severity]: prev[resolveDialog.severity] - 1,
        resolved: prev.resolved + 1,
      }));
    }
    setResolveDialog(null);
    setResolveNote('');
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <ErrorIcon color="error" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'info': return <InfoIcon color="info" />;
      default: return <NotificationIcon />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'low_stock': return <LowStockIcon />;
      case 'expiry': return <ExpiryIcon />;
      default: return <NotificationIcon />;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredAlerts = alerts.filter(alert => {
    if (tabValue === 0) return alert.status === 'active';
    if (tabValue === 1) return alert.status === 'resolved';
    return true;
  });

  const checkStockLevels = async () => {
    setLoading(true);
    try {
      const response = await alertsAPI.checkStockLevels();
      // Refresh alerts after checking
      await fetchAlerts();
      setError('');
    } catch (err) {
      console.error('Stock check error:', err);
      // Simulate creating new alerts for demo
      const newAlert = {
        id: Date.now(),
        type: 'low_stock',
        severity: 'warning',
        title: 'Stock Check Alert',
        message: 'Stock levels checked - new low stock items detected',
        product_name: 'Demo Product',
        status: 'active',
        created_at: new Date().toISOString(),
      };
      setAlerts(prev => [newAlert, ...prev]);
      setError('Stock check completed (demo mode)');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">Alerts & Notifications</Typography>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={checkStockLevels}
            disabled={loading}
          >
            Check Stock Levels
          </Button>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {/* Alert Banner for Critical/Warning Alerts */}
        {alertStats.critical > 0 && (
          <Alert severity="error" sx={{ mb: 2 }} icon={<ErrorIcon />}>
            <strong>Critical Alert!</strong> You have {alertStats.critical} critical alert{alertStats.critical > 1 ? 's' : ''} requiring immediate attention.
          </Alert>
        )}
        {alertStats.warning > 0 && alertStats.critical === 0 && (
          <Alert severity="warning" sx={{ mb: 2 }} icon={<WarningIcon />}>
            <strong>Warning!</strong> You have {alertStats.warning} warning alert{alertStats.warning > 1 ? 's' : ''} that need attention.
          </Alert>
        )}
        {alertStats.critical === 0 && alertStats.warning === 0 && alertStats.info === 0 && (
          <Alert severity="success" sx={{ mb: 2 }} icon={<CheckCircle />}>
            <strong>All Clear!</strong> No active alerts at this time.
          </Alert>
        )}

        {/* Alert Stats */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Badge badgeContent={alertStats.critical} color="error">
                    <ErrorIcon sx={{ mr: 2, color: 'error.main' }} />
                  </Badge>
                  <Box sx={{ ml: 2 }}>
                    <Typography color="textSecondary" gutterBottom>
                      Critical Alerts
                    </Typography>
                    <Typography variant="h5">
                      {alertStats.critical}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Badge badgeContent={alertStats.warning} color="warning">
                    <WarningIcon sx={{ mr: 2, color: 'warning.main' }} />
                  </Badge>
                  <Box sx={{ ml: 2 }}>
                    <Typography color="textSecondary" gutterBottom>
                      Warning Alerts
                    </Typography>
                    <Typography variant="h5">
                      {alertStats.warning}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Badge badgeContent={alertStats.info} color="info">
                    <InfoIcon sx={{ mr: 2, color: 'info.main' }} />
                  </Badge>
                  <Box sx={{ ml: 2 }}>
                    <Typography color="textSecondary" gutterBottom>
                      Info Alerts
                    </Typography>
                    <Typography variant="h5">
                      {alertStats.info}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CheckCircle sx={{ mr: 2, color: 'success.main' }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Resolved
                    </Typography>
                    <Typography variant="h5">
                      {alertStats.resolved}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Alerts Table */}
        <Card>
          <CardContent>
            <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ mb: 2 }}>
              <Tab label={`Active (${alerts.filter(a => a.status === 'active').length})`} />
              <Tab label={`Resolved (${alerts.filter(a => a.status === 'resolved').length})`} />
            </Tabs>

            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Type</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Product</TableCell>
                    <TableCell>Created</TableCell>
                    {tabValue === 1 && <TableCell>Resolved</TableCell>}
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredAlerts.map((alert) => (
                    <TableRow key={alert.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getTypeIcon(alert.type)}
                          <Typography variant="body2" sx={{ ml: 1 }}>
                            {alert.type ? alert.type.replace('_', ' ') : 'notification'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          icon={getSeverityIcon(alert.severity)}
                          label={alert.severity} 
                          color={getSeverityColor(alert.severity)} 
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {alert.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {alert.message}
                        </Typography>
                      </TableCell>
                      <TableCell>{alert.product_name || '-'}</TableCell>
                      <TableCell>{formatDate(alert.created_at)}</TableCell>
                      {tabValue === 1 && (
                        <TableCell>
                          {alert.resolved_at ? formatDate(alert.resolved_at) : '-'}
                        </TableCell>
                      )}
                      <TableCell>
                        {alert.status === 'active' ? (
                          <IconButton 
                            onClick={() => handleResolveAlert(alert)} 
                            size="small"
                            color="success"
                          >
                            <ResolveIcon />
                          </IconButton>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            Resolved by {alert.resolved_by}
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        {/* Resolve Alert Dialog */}
        <Dialog open={!!resolveDialog} onClose={() => setResolveDialog(null)} maxWidth="sm" fullWidth>
          <DialogTitle>Resolve Alert</DialogTitle>
          <DialogContent>
            {resolveDialog && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="h6" gutterBottom>
                  {resolveDialog.title}
                </Typography>
                <Typography color="text.secondary" gutterBottom>
                  {resolveDialog.message}
                </Typography>
                <TextField
                  label="Resolution Note"
                  multiline
                  rows={3}
                  value={resolveNote}
                  onChange={(e) => setResolveNote(e.target.value)}
                  fullWidth
                  sx={{ mt: 2 }}
                  placeholder="Describe how this alert was resolved..."
                />
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setResolveDialog(null)}>Cancel</Button>
            <Button onClick={confirmResolve} variant="contained" color="success">
              Mark as Resolved
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
};

export default AlertsPage;