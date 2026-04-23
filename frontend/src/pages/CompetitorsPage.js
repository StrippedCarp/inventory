import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Chip, Alert, Button,
  Dialog, DialogTitle, DialogContent, DialogActions, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Paper, Tabs, Tab,
  Divider, IconButton
} from '@mui/material';
import {
  TrendingUp, TrendingDown, Store, AttachMoney, Inventory,
  Close, CalendarToday, ShowChart
} from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import Layout from '../components/Layout';
import { competitorsAPI } from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const CompetitorsPage = () => {
  const [competitors, setCompetitors] = useState([]);
  const [userCategories, setUserCategories] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedCompetitor, setSelectedCompetitor] = useState(null);
  const [detailsDialog, setDetailsDialog] = useState(false);
  const [competitorDetails, setCompetitorDetails] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    fetchCompetitors();
  }, []);

  const fetchCompetitors = async () => {
    setLoading(true);
    try {
      const response = await competitorsAPI.getAll();
      setCompetitors(response.data.competitors || []);
      setUserCategories(response.data.user_categories || []);
      setMessage(response.data.message || '');
    } catch (error) {
      console.error('Error fetching competitors:', error);
      setError('Failed to load competitors');
    }
    setLoading(false);
  };

  const handleViewDetails = async (competitor) => {
    try {
      const response = await competitorsAPI.getDetails(competitor.id);
      setCompetitorDetails(response.data);
      setSelectedCompetitor(competitor);
      setDetailsDialog(true);
    } catch (error) {
      setError('Failed to load competitor details');
    }
  };

  const formatCurrency = (amount) => {
    return `KES ${parseFloat(amount || 0).toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const getSalesChartData = () => {
    if (!competitorDetails?.sales_history) return null;

    const history = competitorDetails.sales_history.slice(0, 30).reverse();
    
    return {
      labels: history.map(s => new Date(s.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
      datasets: [
        {
          label: 'Daily Sales',
          data: history.map(s => s.daily_sales),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1
        }
      ]
    };
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Sales Performance (Last 30 Days)'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return 'KES ' + value.toLocaleString();
          }
        }
      }
    }
  };

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Competitor Intelligence</Typography>
          <Button variant="outlined" onClick={fetchCompetitors}>
            Refresh
          </Button>
        </Box>

        {message && (
          <Alert severity="info" sx={{ mb: 2 }}>
            {message}
          </Alert>
        )}

        {userCategories.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Your Business Categories:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {userCategories.map((category, index) => (
                <Chip key={index} label={category} color="primary" size="small" />
              ))}
            </Box>
          </Box>
        )}

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {competitors.length === 0 && !loading && (
          <Alert severity="info">
            No competitors found in your business categories. Add products to your inventory to see relevant competitors.
          </Alert>
        )}

        <Grid container spacing={3}>
          {competitors.map((competitor) => (
            <Grid item xs={12} md={6} lg={4} key={competitor.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box>
                      <Typography variant="h6" component="div">
                        {competitor.business_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {competitor.owner_name}
                      </Typography>
                    </Box>
                    <Chip label={competitor.category} color="secondary" size="small" />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Store sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {competitor.location || 'Location not specified'}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Inventory sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {competitor.product_count || 0} Products
                      </Typography>
                    </Box>
                  </Box>

                  {competitor.sales_data && (
                    <Box sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="body2" fontWeight="bold" gutterBottom>
                        Latest Sales Data
                      </Typography>
                      <Grid container spacing={1}>
                        <Grid item xs={12}>
                          <Typography variant="caption" color="text.secondary">Daily Sales</Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {formatCurrency(competitor.sales_data.daily_sales)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Monthly</Typography>
                          <Typography variant="body2">
                            {formatCurrency(competitor.sales_data.monthly_sales)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Yearly</Typography>
                          <Typography variant="body2">
                            {formatCurrency(competitor.sales_data.yearly_sales)}
                          </Typography>
                        </Grid>
                      </Grid>
                    </Box>
                  )}

                  <Button
                    variant="contained"
                    size="small"
                    fullWidth
                    onClick={() => handleViewDetails(competitor)}
                  >
                    View Details
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Competitor Details Dialog */}
        <Dialog 
          open={detailsDialog} 
          onClose={() => setDetailsDialog(false)} 
          maxWidth="md" 
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="h6">{competitorDetails?.business_name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {competitorDetails?.category} • {competitorDetails?.location}
                </Typography>
              </Box>
              <IconButton onClick={() => setDetailsDialog(false)}>
                <Close />
              </IconButton>
            </Box>
          </DialogTitle>
          <DialogContent>
            <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ mb: 2 }}>
              <Tab label="Sales Performance" />
              <Tab label="Products & Pricing" />
            </Tabs>

            {/* Sales Performance Tab */}
            {tabValue === 0 && competitorDetails && (
              <Box>
                {competitorDetails.sales_data && (
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="caption" color="text.secondary">Daily Sales</Typography>
                          <Typography variant="h6">
                            {formatCurrency(competitorDetails.sales_data.daily_sales)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="caption" color="text.secondary">Monthly Sales</Typography>
                          <Typography variant="h6">
                            {formatCurrency(competitorDetails.sales_data.monthly_sales)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={4}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="caption" color="text.secondary">Yearly Sales</Typography>
                          <Typography variant="h6">
                            {formatCurrency(competitorDetails.sales_data.yearly_sales)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                )}

                {competitorDetails.sales_history && competitorDetails.sales_history.length > 0 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>Sales Trend</Typography>
                    <Line data={getSalesChartData()} options={chartOptions} />
                  </Box>
                )}

                {(!competitorDetails.sales_history || competitorDetails.sales_history.length === 0) && (
                  <Alert severity="info">No sales history available for this competitor</Alert>
                )}
              </Box>
            )}

            {/* Products & Pricing Tab */}
            {tabValue === 1 && competitorDetails && (
              <Box>
                {competitorDetails.products && competitorDetails.products.length > 0 ? (
                  <TableContainer component={Paper} variant="outlined">
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Product Name</TableCell>
                          <TableCell>Category</TableCell>
                          <TableCell align="right">Price</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {competitorDetails.products.map((product) => (
                          <TableRow key={product.id}>
                            <TableCell>{product.product_name}</TableCell>
                            <TableCell>
                              <Chip label={product.category} size="small" />
                            </TableCell>
                            <TableCell align="right">
                              <Typography variant="body2" fontWeight="bold">
                                {formatCurrency(product.price)}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Alert severity="info">No product pricing information available</Alert>
                )}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDetailsDialog(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
};

export default CompetitorsPage;
