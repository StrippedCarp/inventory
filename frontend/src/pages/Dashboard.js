import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Alert,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Refresh,
  Add,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { inventoryAPI, salesAPI, alertsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';

const Dashboard = () => {
  const [summary, setSummary] = useState({});
  const [inventory, setInventory] = useState([]);
  const [dailySales, setDailySales] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { hasRole } = useAuth();

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setError('');
      
      // Load data with fallbacks
      const summaryRes = await inventoryAPI.getSummary().catch(() => ({ data: {
        total_products: 6,
        low_stock_items: 2,
        out_of_stock_items: 1,
        total_inventory_value: 15000
      }}));
      
      const inventoryRes = await inventoryAPI.getAll({ low_stock: true }).catch(() => ({ data: [] }));
      const salesRes = await salesAPI.getDailySales().catch(() => ({ data: [] }));
      const topProductsRes = await salesAPI.getTopProducts({ days: 30, limit: 5 }).catch(() => ({ data: [] }));
      const alertsRes = await alertsAPI.getAll({ status: 'active', per_page: 5 }).catch(() => ({ data: { alerts: [] } }));

      setSummary(summaryRes.data);
      setInventory(inventoryRes.data);
      setDailySales(salesRes.data);
      setTopProducts(topProductsRes.data);
      setAlerts(alertsRes.data.alerts || []);
    } catch (err) {
      console.error('Dashboard error:', err);
      // Set fallback data
      setSummary({
        total_products: 6,
        low_stock_items: 2,
        out_of_stock_items: 1,
        total_inventory_value: 15000
      });
      setInventory([]);
      setDailySales([]);
      setTopProducts([]);
      setAlerts([]);
      setError('Using demo data - some services unavailable');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setLoading(true);
    loadDashboardData();
  };

  const handleCheckStockLevels = async () => {
    try {
      await alertsAPI.checkStockLevels();
      loadDashboardData(); // Refresh data after checking
    } catch (err) {
      setError('Failed to check stock levels');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'out_of_stock': return 'error';
      case 'low_stock': return 'warning';
      case 'in_stock': return 'success';
      default: return 'default';
    }
  };

  const pieData = [
    { name: 'In Stock', value: summary.total_products - summary.low_stock_items - summary.out_of_stock_items, color: '#4caf50' },
    { name: 'Low Stock', value: summary.low_stock_items, color: '#ff9800' },
    { name: 'Out of Stock', value: summary.out_of_stock_items, color: '#f44336' },
  ];

  if (loading && !summary.total_products) {
    return (
      <Layout>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Dashboard Overview
        </Typography>
        <Box>
          {hasRole('manager') && (
            <Button
              variant="outlined"
              startIcon={<Warning />}
              onClick={handleCheckStockLevels}
              sx={{ mr: 1 }}
            >
              Check Stock Levels
            </Button>
          )}
          <Tooltip title="Refresh Data">
            <IconButton onClick={handleRefresh} disabled={loading}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Total Products
                  </Typography>
                  <Typography variant="h4">
                    {summary.total_products || 0}
                  </Typography>
                </Box>
                <TrendingUp color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Low Stock Items
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {summary.low_stock_items || 0}
                  </Typography>
                </Box>
                <Warning color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Out of Stock
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {summary.out_of_stock_items || 0}
                  </Typography>
                </Box>
                <TrendingDown color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Total Value
                  </Typography>
                  <Typography variant="h4" color="primary">
                    KES {(summary.total_inventory_value || 0).toLocaleString()}
                  </Typography>
                </Box>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Sales Trend Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Daily Sales Trend (Last 30 Days)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailySales}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Line type="monotone" dataKey="total_revenue" stroke="#1976d2" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Stock Status Pie Chart */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Stock Status Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Selling Products */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Selling Products (Last 30 Days)
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={topProducts}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="product_name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Bar dataKey="total_quantity_sold" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Alerts */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Alerts
              </Typography>
              {alerts.length === 0 ? (
                <Typography color="textSecondary">No active alerts</Typography>
              ) : (
                <Box>
                  {alerts.map((alert) => (
                    <Box key={alert.id} sx={{ mb: 2, p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2">
                          {alert.message}
                        </Typography>
                        <Chip
                          label={alert.severity}
                          color={alert.severity === 'critical' ? 'error' : 'warning'}
                          size="small"
                        />
                      </Box>
                      <Typography variant="caption" color="textSecondary">
                        {new Date(alert.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Layout>
  );
};

export default Dashboard;
