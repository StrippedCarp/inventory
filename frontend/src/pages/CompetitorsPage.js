import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tabs,
  Tab,
  Alert,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Store as StoreIcon,
  AttachMoney as MoneyIcon,
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { competitorsAPI } from '../services/api';

const CompetitorsPage = () => {
  const [competitors, setCompetitors] = useState([]);
  const [selectedCompetitor, setSelectedCompetitor] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCompetitors();
  }, []);

  const fetchCompetitors = async () => {
    try {
      const response = await competitorsAPI.getAll();
      setCompetitors(response.data || []);
      if (response.data && response.data.length > 0) {
        setSelectedCompetitor(response.data[0]);
      }
    } catch (err) {
      setError('Failed to load competitors data');
      // Demo data
      const demoData = [
        {
          id: 1,
          business_name: 'Fresh Groceries Ltd',
          owner_name: 'Jane Doe',
          category: 'grocery',
          location: 'Nairobi CBD',
          product_count: 45,
          sales_data: {
            daily_sales: 15000,
            monthly_sales: 450000,
            yearly_sales: 5400000
          }
        },
        {
          id: 2,
          business_name: 'Green Market',
          owner_name: 'John Smith',
          category: 'grocery',
          location: 'Westlands',
          product_count: 38,
          sales_data: {
            daily_sales: 12000,
            monthly_sales: 360000,
            yearly_sales: 4320000
          }
        }
      ];
      setCompetitors(demoData);
      setSelectedCompetitor(demoData[0]);
    } finally {
      setLoading(false);
    }
  };

  const fetchCompetitorDetails = async (competitorId) => {
    try {
      const response = await competitorsAPI.getDetails(competitorId);
      setSelectedCompetitor(response.data);
    } catch (err) {
      console.error('Failed to load competitor details:', err);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 0
    }).format(amount);
  };

  return (
    <Layout>
      <Box>
        <Typography variant="h4" sx={{ mb: 3 }}>Market Competitors</Typography>
        
        {error && <Alert severity="info" sx={{ mb: 2 }}>{error}</Alert>}

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Typography variant="h6" sx={{ mb: 2 }}>Competitors in Your Category</Typography>
            {competitors.map((comp) => (
              <Card 
                key={comp.id} 
                sx={{ 
                  mb: 2, 
                  cursor: 'pointer',
                  border: selectedCompetitor?.id === comp.id ? '2px solid #1976d2' : 'none'
                }}
                onClick={() => {
                  setSelectedCompetitor(comp);
                  fetchCompetitorDetails(comp.id);
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box>
                      <Typography variant="h6">{comp.business_name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {comp.owner_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {comp.location}
                      </Typography>
                    </Box>
                    <Chip label={comp.category} size="small" color="primary" />
                  </Box>
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      Products: {comp.product_count}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Grid>

          <Grid item xs={12} md={8}>
            {selectedCompetitor && (
              <Card>
                <CardContent>
                  <Typography variant="h5" sx={{ mb: 3 }}>
                    {selectedCompetitor.business_name}
                  </Typography>

                  <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
                    <Tab label="Sales Performance" />
                    <Tab label="Product Pricing" />
                  </Tabs>

                  {tabValue === 0 && (
                    <Box>
                      <Grid container spacing={3}>
                        <Grid item xs={12} md={4}>
                          <Card sx={{ bgcolor: '#e3f2fd' }}>
                            <CardContent>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <MoneyIcon sx={{ mr: 1 }} />
                                <Typography variant="body2" color="text.secondary">
                                  Daily Sales
                                </Typography>
                              </Box>
                              <Typography variant="h5">
                                {formatCurrency(selectedCompetitor.sales_data?.daily_sales || 0)}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                        <Grid item xs={12} md={4}>
                          <Card sx={{ bgcolor: '#f3e5f5' }}>
                            <CardContent>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <TrendingUpIcon sx={{ mr: 1 }} />
                                <Typography variant="body2" color="text.secondary">
                                  Monthly Sales
                                </Typography>
                              </Box>
                              <Typography variant="h5">
                                {formatCurrency(selectedCompetitor.sales_data?.monthly_sales || 0)}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                        <Grid item xs={12} md={4}>
                          <Card sx={{ bgcolor: '#e8f5e9' }}>
                            <CardContent>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <StoreIcon sx={{ mr: 1 }} />
                                <Typography variant="body2" color="text.secondary">
                                  Yearly Sales
                                </Typography>
                              </Box>
                              <Typography variant="h5">
                                {formatCurrency(selectedCompetitor.sales_data?.yearly_sales || 0)}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                      </Grid>
                    </Box>
                  )}

                  {tabValue === 1 && (
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Product Name</TableCell>
                            <TableCell>Category</TableCell>
                            <TableCell align="right">Price (KES)</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {selectedCompetitor.products?.map((product) => (
                            <TableRow key={product.id}>
                              <TableCell>{product.product_name}</TableCell>
                              <TableCell>{product.category}</TableCell>
                              <TableCell align="right">{formatCurrency(product.price)}</TableCell>
                            </TableRow>
                          )) || (
                            <TableRow>
                              <TableCell colSpan={3} align="center">
                                No product data available
                              </TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </Box>
    </Layout>
  );
};

export default CompetitorsPage;
