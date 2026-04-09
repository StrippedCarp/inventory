import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  Assessment,
  GetApp,
  Refresh,
  PieChart,
  BarChart,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart as RechartsBar,
  Bar,
  PieChart as RechartsPie,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import Layout from '../components/Layout';
import { analyticsAPI } from '../services/api';

const AnalyticsPage = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [salesData, setSalesData] = useState(null);
  const [inventoryData, setInventoryData] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedPeriod]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    setError('');

    try {
      const [dashboardRes, salesRes, inventoryRes, forecastRes] = await Promise.all([
        analyticsAPI.getDashboard(),
        analyticsAPI.getSalesPerformance({ days: selectedPeriod }),
        analyticsAPI.getInventoryValuation(),
        analyticsAPI.getForecastAccuracy({ days: selectedPeriod })
      ]);

      setDashboardData(dashboardRes.data);
      setSalesData(salesRes.data);
      setInventoryData(inventoryRes.data);
      setForecastData(forecastRes.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to load analytics data');
      console.error('Analytics error:', err);
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const exportInventoryReport = async () => {
    try {
      setError('');
      const response = await analyticsAPI.exportFile('inventory-report', { format: 'xlsx' });
      const blob = response.data;  // axios with responseType: 'blob' returns data as blob
      const filename = `inventory_report_${new Date().toISOString().split('T')[0]}.xlsx`;
      downloadFile(blob, filename);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to export inventory report');
      console.error('Export error:', err);
    }
  };

  const exportSalesReport = async () => {
    try {
      setError('');
      const response = await analyticsAPI.exportFile('sales-report', { days: selectedPeriod, format: 'csv' });
      const blob = response.data;  // axios with responseType: 'blob' returns data as blob
      const filename = `sales_report_${new Date().toISOString().split('T')[0]}.csv`;
      downloadFile(blob, filename);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to export sales report');
      console.error('Export error:', err);
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
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
          Analytics & Reports
        </Typography>
        <Box>
          <FormControl sx={{ mr: 2, minWidth: 120 }}>
            <InputLabel>Period</InputLabel>
            <Select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              label="Period"
            >
              <MenuItem value={7}>7 Days</MenuItem>
              <MenuItem value={30}>30 Days</MenuItem>
              <MenuItem value={90}>90 Days</MenuItem>
              <MenuItem value={365}>1 Year</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadAnalyticsData}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<GetApp />}
            onClick={exportInventoryReport}
            sx={{ mr: 1 }}
          >
            Export Inventory
          </Button>
          <Button
            variant="outlined"
            startIcon={<GetApp />}
            onClick={exportSalesReport}
          >
            Export Sales
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* KPI Cards */}
      {dashboardData?.kpis && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Products
                </Typography>
                <Typography variant="h4">
                  {dashboardData.kpis.total_products || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Inventory Value
                </Typography>
                <Typography variant="h4" color="primary">
                  {(dashboardData.kpis.total_inventory_value || 0).toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Avg Turnover Ratio
                </Typography>
                <Typography variant="h4" color="success.main">
                  {(dashboardData.kpis.avg_inventory_turnover || 0).toFixed(1)}x
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Stockout Rate
                </Typography>
                <Typography variant="h4" color="error.main">
                  {(dashboardData.kpis.stockout_rate || 0).toFixed(1)}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}}

      <Grid container spacing={3}>
        {/* Sales Trends */}
        {dashboardData?.sales_trends && (
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sales Trends (Last 90 Days)
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={dashboardData.sales_trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Bar yAxisId="left" dataKey="quantity" fill="#8884d8" name="Quantity Sold" />
                    <Line yAxisId="right" type="monotone" dataKey="revenue" stroke="#82ca9d" name="Revenue ($)" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Stock Distribution */}
        {dashboardData?.stock_distribution && (
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Stock Status Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPie>
                    <Pie
                      data={dashboardData.stock_distribution}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                      label={({ status, count }) => `{status}: {count}`}
                    >
                      {dashboardData.stock_distribution.map((entry, index) => (
                        <Cell key={`cell-{index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </RechartsPie>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Category Performance */}
        {dashboardData?.category_performance && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Category Performance
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsBar data={dashboardData.category_performance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="revenue" fill="#8884d8" name="Revenue ($)" />
                  </RechartsBar>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Top Products */}
        {dashboardData?.top_products && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Top 10 Products by Sales
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsBar data={dashboardData.top_products}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="total_sold" fill="#82ca9d" name="Units Sold" />
                  </RechartsBar>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Sales Performance Metrics */}
        {salesData?.performance_metrics && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sales Performance Metrics
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body1" gutterBottom>
                    Current Month Sales: {(salesData.performance_metrics.current_month_sales || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    Previous Month Sales: {(salesData.performance_metrics.previous_month_sales || 0).toLocaleString()}
                  </Typography>
                  <Box display="flex" alignItems="center" sx={{ mt: 1 }}>
                    <Typography variant="body1" sx={{ mr: 1 }}>
                      Growth Rate:
                    </Typography>
                    <Chip
                      label={`{(salesData.performance_metrics.growth_rate || 0).toFixed(1)}%`}
                      color={(salesData.performance_metrics.growth_rate || 0) >= 0 ? 'success' : 'error'}
                      icon={<TrendingUp />}
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Forecast Accuracy */}
        {forecastData?.accuracy_trends && forecastData.accuracy_trends.length > 0 && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Forecast Accuracy Trends
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={forecastData.accuracy_trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip formatter={(value) => [`{(value * 100).toFixed(1)}%`, 'Confidence']} />
                    <Line type="monotone" dataKey="confidence" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Inventory Valuation Summary */}
        {inventoryData?.category_summary && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Inventory Valuation by Category
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsBar data={inventoryData.category_summary}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip formatter={(value, name) => [
                      name === 'total_value' ? `${value.toLocaleString()}` : value,
                      name === 'total_value' ? 'Total Value' : 'Items'
                    ]} />
                    <Bar dataKey="total_value" fill="#8884d8" name="Total Value ($)" />
                    <Bar dataKey="item_count" fill="#82ca9d" name="Item Count" />
                  </RechartsBar>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Layout>
  );
};

export default AnalyticsPage;
