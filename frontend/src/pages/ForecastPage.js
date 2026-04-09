import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
} from '@mui/material';
import {
  TrendingUp,
  Psychology,
  Refresh,
  Download,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import Layout from '../components/Layout';
import { productsAPI } from '../services/api';

const ForecastPage = () => {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [daysAhead, setDaysAhead] = useState(7);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    loadProducts();
    loadModelInfo();
  }, []);

  const loadProducts = async () => {
    try {
      const response = await productsAPI.getAll();
      setProducts(response.data.products || []);
    } catch (err) {
      setError('Failed to load products');
    }
  };

  const loadModelInfo = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/forecast/model-info', {
        headers: {
          'Authorization': `Bearer KES {localStorage.getItem('access_token')}`
        }
      });
      const data = await response.json();
      setModelInfo(data);
    } catch (err) {
      console.error('Failed to load model info:', err);
    }
  };

  const generateForecast = async () => {
    if (!selectedProduct) {
      setError('Please select a product');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`http://localhost:5000/api/forecast/predict/${selectedProduct}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer KES {localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ days_ahead: daysAhead })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setForecast(data);
      } else {
        setError(data.message || 'Failed to generate forecast');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getForecastChartData = () => {
    if (!forecast) return [];

    return forecast.forecast.dates.map((date, index) => ({
      date: new Date(date).toLocaleDateString(),
      demand: forecast.forecast.values[index],
      confidence: forecast.forecast.confidence_score
    }));
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.7) return 'success';
    if (confidence >= 0.5) return 'warning';
    return 'error';
  };

  const getConfidenceText = (confidence) => {
    if (confidence >= 0.7) return 'High';
    if (confidence >= 0.5) return 'Medium';
    return 'Low';
  };

  const exportForecast = () => {
    if (!forecast) return;

    const csvContent = [
      ['Date', 'Predicted Demand'],
      ...forecast.forecast.dates.map((date, index) => [
        date,
        forecast.forecast.values[index]
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forecast_KES {forecast.product_name}_KES {new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <Layout>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Demand Forecasting
        </Typography>
        {modelInfo && (
          <Chip
            icon={<Psychology />}
            label={`Model: KES {modelInfo.model_type}`}
            color={modelInfo.model_loaded ? 'success' : 'warning'}
            variant="outlined"
          />
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Forecast Generation Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Generate Forecast
          </Typography>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Select Product</InputLabel>
                <Select
                  value={selectedProduct}
                  onChange={(e) => setSelectedProduct(e.target.value)}
                  label="Select Product"
                >
                  {products.map((product) => (
                    <MenuItem key={product.id} value={product.id}>
                      {product.name} ({product.sku})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                fullWidth
                label="Days Ahead"
                type="number"
                value={daysAhead}
                onChange={(e) => setDaysAhead(Math.max(1, Math.min(30, parseInt(e.target.value) || 7)))}
                inputProps={{ min: 1, max: 30 }}
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <TrendingUp />}
                onClick={generateForecast}
                disabled={loading || !selectedProduct}
                fullWidth
              >
                {loading ? 'Generating...' : 'Generate Forecast'}
              </Button>
            </Grid>
            <Grid item xs={12} sm={2}>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadProducts}
                fullWidth
              >
                Refresh
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Forecast Results */}
      {forecast && (
        <Grid container spacing={3}>
          {/* Summary Cards */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Product
                </Typography>
                <Typography variant="h6">
                  {forecast.product_name}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  ID: {forecast.product_id}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Predicted Demand
                </Typography>
                <Typography variant="h4" color="primary">
                  {forecast.forecast.total_demand}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Next {daysAhead} days
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Confidence Score
                </Typography>
                <Box display="flex" alignItems="center">
                  <Typography variant="h4" sx={{ mr: 2 }}>
                    {(forecast.forecast.confidence_score * 100).toFixed(1)}%
                  </Typography>
                  <Chip
                    label={getConfidenceText(forecast.forecast.confidence_score)}
                    color={getConfidenceColor(forecast.forecast.confidence_score)}
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="textSecondary">
                  Model: {forecast.model_type}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Forecast Chart */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    Demand Forecast Visualization
                  </Typography>
                  <Button
                    startIcon={<Download />}
                    onClick={exportForecast}
                    size="small"
                  >
                    Export CSV
                  </Button>
                </Box>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={getForecastChartData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="demand"
                      stroke="#1976d2"
                      strokeWidth={3}
                      dot={{ fill: '#1976d2', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Forecast Table */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Daily Breakdown
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell align="right">Demand</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {forecast.forecast.dates.map((date, index) => (
                        <TableRow key={date}>
                          <TableCell>
                            {new Date(date).toLocaleDateString()}
                          </TableCell>
                          <TableCell align="right">
                            {forecast.forecast.values[index].toFixed(1)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Forecast Metadata */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Forecast Details
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="textSecondary">
                      Generated At
                    </Typography>
                    <Typography variant="body1">
                      {new Date(forecast.generated_at).toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="textSecondary">
                      Forecast Period
                    </Typography>
                    <Typography variant="body1">
                      {daysAhead} days
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="textSecondary">
                      Average Daily Demand
                    </Typography>
                    <Typography variant="body1">
                      {(forecast.forecast.total_demand / daysAhead).toFixed(2)}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2" color="textSecondary">
                      Model Type
                    </Typography>
                    <Typography variant="body1">
                      {forecast.model_type}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Help Text */}
      {!forecast && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              How to Use Demand Forecasting
            </Typography>
            <Typography variant="body1" paragraph>
              1. Select a product from the dropdown menu
            </Typography>
            <Typography variant="body1" paragraph>
              2. Choose the number of days ahead to forecast (1-30 days)
            </Typography>
            <Typography variant="body1" paragraph>
              3. Click "Generate Forecast" to create predictions
            </Typography>
            <Typography variant="body2" color="textSecondary">
              The system uses machine learning models trained on historical sales data to predict future demand.
              Confidence scores indicate the reliability of predictions.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Layout>
  );
};

export default ForecastPage;
