import React, { useState } from 'react';
import {
  Box, Card, CardContent, Typography, Button, Tabs, Tab, Grid,
  TextField, MenuItem, Alert, CircularProgress, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Paper, Chip
} from '@mui/material';
import {
  GetApp, Description, Assessment, Inventory, TrendingUp,
  People, LocalShipping, Category, DateRange
} from '@mui/icons-material';
import Layout from '../components/Layout';

const ReportsPage = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loadingReports, setLoadingReports] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [reportParams, setReportParams] = useState({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
    category: 'all',
    supplier: 'all',
    format: 'xlsx'
  });

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

  const exportReport = async (endpoint, filename) => {
    setLoadingReports(prev => ({ ...prev, [endpoint]: true }));
    setError('');
    setSuccess('');

    try {
      const queryParams = new URLSearchParams({
        start_date: reportParams.startDate,
        end_date: reportParams.endDate,
        category: reportParams.category,
        format: reportParams.format
      });

      const response = await fetch(`http://localhost:5000/api/analytics/export/${endpoint}?${queryParams}`, {
        method: 'GET'
      });

      if (!response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          setError(errorData.error || 'Failed to generate report');
        } else {
          setError(`Failed to generate report: ${response.statusText}`);
        }
        setLoadingReports(prev => ({ ...prev, [endpoint]: false }));
        return;
      }

      const blob = await response.blob();
      
      if (blob.size === 0) {
        setError('Report generated but file is empty');
        setLoadingReports(prev => ({ ...prev, [endpoint]: false }));
        return;
      }

      const extension = reportParams.format === 'csv' ? 'csv' : reportParams.format === 'pdf' ? 'pdf' : 'xlsx';
      downloadFile(blob, `${filename}_${reportParams.startDate}_to_${reportParams.endDate}.${extension}`);
      setSuccess(`${filename} downloaded successfully!`);
    } catch (err) {
      console.error('Export error:', err);
      setError(`Network error: ${err.message}`);
    } finally {
      setLoadingReports(prev => ({ ...prev, [endpoint]: false }));
    }
  };

  const reportTypes = [
    {
      title: 'Inventory Report',
      description: 'Complete inventory status with stock levels, values, and reorder points',
      icon: <Inventory />,
      endpoint: 'inventory-report',
      filename: 'inventory_report',
      color: '#1976d2'
    },
    {
      title: 'Sales Report',
      description: 'Detailed sales transactions with products, quantities, and revenue',
      icon: <TrendingUp />,
      endpoint: 'sales-report',
      filename: 'sales_report',
      color: '#2e7d32'
    },
    {
      title: 'Low Stock Report',
      description: 'Products below reorder point requiring immediate attention',
      icon: <Assessment />,
      endpoint: 'low-stock-report',
      filename: 'low_stock_report',
      color: '#d32f2f'
    },
    {
      title: 'Product Performance',
      description: 'Sales performance analysis by product with trends',
      icon: <Category />,
      endpoint: 'product-performance',
      filename: 'product_performance',
      color: '#ed6c02'
    },
    {
      title: 'Supplier Report',
      description: 'Supplier details with products supplied and performance',
      icon: <LocalShipping />,
      endpoint: 'supplier-report',
      filename: 'supplier_report',
      color: '#9c27b0'
    },
    {
      title: 'Customer Report',
      description: 'Customer database with purchase history and loyalty points',
      icon: <People />,
      endpoint: 'customer-report',
      filename: 'customer_report',
      color: '#0288d1'
    },
    {
      title: 'Batch Expiry Report',
      description: 'Product batches with expiry dates and valuation',
      icon: <DateRange />,
      endpoint: 'batch-expiry-report',
      filename: 'batch_expiry_report',
      color: '#f57c00'
    },
    {
      title: 'Profit & Loss Report',
      description: 'Revenue, costs, and profit analysis by period',
      icon: <Description />,
      endpoint: 'profit-loss-report',
      filename: 'profit_loss_report',
      color: '#388e3c'
    }
  ];

  return (
    <Layout>
      <Box>
        <Typography variant="h4" sx={{ mb: 3 }}>Reports & Exports</Typography>

        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}

        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Report Parameters</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Start Date"
                  type="date"
                  value={reportParams.startDate}
                  onChange={(e) => setReportParams({ ...reportParams, startDate: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="End Date"
                  type="date"
                  value={reportParams.endDate}
                  onChange={(e) => setReportParams({ ...reportParams, endDate: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  select
                  fullWidth
                  label="Category"
                  value={reportParams.category}
                  onChange={(e) => setReportParams({ ...reportParams, category: e.target.value })}
                >
                  <MenuItem value="all">All Categories</MenuItem>
                  <MenuItem value="Electronics">Electronics</MenuItem>
                  <MenuItem value="Food">Food</MenuItem>
                  <MenuItem value="Clothing">Clothing</MenuItem>
                  <MenuItem value="Home">Home</MenuItem>
                  <MenuItem value="Sports">Sports</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  select
                  fullWidth
                  label="Format"
                  value={reportParams.format}
                  onChange={(e) => setReportParams({ ...reportParams, format: e.target.value })}
                >
                  <MenuItem value="xlsx">Excel (.xlsx)</MenuItem>
                  <MenuItem value="csv">CSV (.csv)</MenuItem>
                  <MenuItem value="pdf">PDF (.pdf)</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        <Grid container spacing={3}>
          {reportTypes.map((report, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ 
                      bgcolor: report.color, 
                      color: 'white', 
                      p: 1, 
                      borderRadius: 1, 
                      mr: 2,
                      display: 'flex',
                      alignItems: 'center'
                    }}>
                      {report.icon}
                    </Box>
                    <Typography variant="h6">{report.title}</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {report.description}
                  </Typography>
                </CardContent>
                <Box sx={{ p: 2, pt: 0 }}>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={loadingReports[report.endpoint] ? <CircularProgress size={20} /> : <GetApp />}
                    onClick={() => exportReport(report.endpoint, report.filename)}
                    disabled={loadingReports[report.endpoint]}
                    sx={{ bgcolor: report.color, '&:hover': { bgcolor: report.color, opacity: 0.9 } }}
                  >
                    {loadingReports[report.endpoint] ? 'Generating...' : 'Download Report'}
                  </Button>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Report Information</Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Report Type</TableCell>
                    <TableCell>Contents</TableCell>
                    <TableCell>Best For</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Inventory Report</TableCell>
                    <TableCell>SKU, Product Name, Stock Levels, Values, Reorder Points</TableCell>
                    <TableCell>Stock audits, inventory planning</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Sales Report</TableCell>
                    <TableCell>Date, Product, Quantity, Price, Revenue, Customer</TableCell>
                    <TableCell>Revenue analysis, tax reporting</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Low Stock Report</TableCell>
                    <TableCell>Products below reorder point with supplier info</TableCell>
                    <TableCell>Purchase order planning</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Product Performance</TableCell>
                    <TableCell>Sales volume, revenue, trends by product</TableCell>
                    <TableCell>Product strategy, pricing decisions</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Supplier Report</TableCell>
                    <TableCell>Supplier details, products, contact info</TableCell>
                    <TableCell>Supplier management, sourcing</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Customer Report</TableCell>
                    <TableCell>Customer info, purchase history, loyalty points</TableCell>
                    <TableCell>Customer relationship management</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Batch Expiry Report</TableCell>
                    <TableCell>Batch numbers, expiry dates, quantities, values</TableCell>
                    <TableCell>Expiry management, FIFO/LIFO tracking</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Profit & Loss Report</TableCell>
                    <TableCell>Revenue, COGS, gross profit, margins</TableCell>
                    <TableCell>Financial analysis, business planning</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Box>
    </Layout>
  );
};

export default ReportsPage;
