import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Button, Grid, Dialog,
  DialogTitle, DialogContent, DialogActions, TextField, Alert,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, IconButton, Chip, Tabs, Tab
} from '@mui/material';
import { Add, Edit, Delete, Inventory } from '@mui/icons-material';
import Layout from '../components/Layout';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const AdminCompetitorsPage = () => {
  const [competitors, setCompetitors] = useState([]);
  const [addDialog, setAddDialog] = useState(false);
  const [detailsDialog, setDetailsDialog] = useState(false);
  const [productDialog, setProductDialog] = useState(false);
  const [salesDialog, setSalesDialog] = useState(false);
  const [selectedCompetitor, setSelectedCompetitor] = useState(null);
  const [competitorProducts, setCompetitorProducts] = useState([]);
  const [editingProduct, setEditingProduct] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [form, setForm] = useState({
    business_name: '',
    owner_name: '',
    category: '',
    location: '',
    phone: '',
    email: ''
  });
  const [productForm, setProductForm] = useState({
    product_name: '',
    category: '',
    price: ''
  });
  const [salesForm, setSalesForm] = useState({
    date: new Date().toISOString().split('T')[0],
    daily_sales: '',
    monthly_sales: '',
    yearly_sales: ''
  });

  useEffect(() => {
    fetchCompetitors();
  }, []);

  const fetchCompetitors = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_URL}/admin/competitors/all`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCompetitors(response.data || []);
    } catch (err) {
      setError('Failed to load competitors');
    }
  };

  const handleAddCompetitor = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(`${API_URL}/admin/competitors`, form, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuccess('Competitor added successfully');
      setAddDialog(false);
      setForm({
        business_name: '',
        owner_name: '',
        category: '',
        location: '',
        phone: '',
        email: ''
      });
      fetchCompetitors();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to add competitor');
    }
  };

  const handleViewDetails = async (competitor) => {
    setSelectedCompetitor(competitor);
    setDetailsDialog(true);
    setTabValue(0);
    await fetchCompetitorProducts(competitor.id);
  };

  const fetchCompetitorProducts = async (competitorId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_URL}/competitors/${competitorId}/products`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCompetitorProducts(response.data || []);
    } catch (err) {
      console.error('Failed to load products:', err);
    }
  };

  const handleAddProduct = () => {
    setEditingProduct(null);
    setProductForm({ product_name: '', category: '', price: '' });
    setProductDialog(true);
  };

  const handleEditProduct = (product) => {
    setEditingProduct(product);
    setProductForm({
      product_name: product.product_name,
      category: product.category,
      price: product.price
    });
    setProductDialog(true);
  };

  const handleSaveProduct = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (editingProduct) {
        await axios.put(
          `${API_URL}/admin/competitors/${selectedCompetitor.id}/products/${editingProduct.id}`,
          productForm,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setSuccess('Product updated successfully');
      } else {
        await axios.post(
          `${API_URL}/admin/competitors/${selectedCompetitor.id}/products`,
          productForm,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setSuccess('Product added successfully');
      }
      setProductDialog(false);
      fetchCompetitorProducts(selectedCompetitor.id);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to save product');
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('Delete this product?')) return;
    try {
      const token = localStorage.getItem('access_token');
      await axios.delete(
        `${API_URL}/admin/competitors/${selectedCompetitor.id}/products/${productId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSuccess('Product deleted successfully');
      fetchCompetitorProducts(selectedCompetitor.id);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to delete product');
    }
  };

  const handleAddSales = () => {
    setSalesForm({
      date: new Date().toISOString().split('T')[0],
      daily_sales: '',
      monthly_sales: '',
      yearly_sales: ''
    });
    setSalesDialog(true);
  };

  const handleSaveSales = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_URL}/admin/competitors/${selectedCompetitor.id}/sales`,
        salesForm,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSuccess('Sales data added successfully');
      setSalesDialog(false);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to add sales data');
    }
  };

  const formatCurrency = (amount) => {
    return `KES ${parseFloat(amount || 0).toLocaleString('en-KE', { minimumFractionDigits: 2 })}`;
  };

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Manage Competitors (Admin)</Typography>
          <Button variant="contained" onClick={() => setAddDialog(true)}>
            Add Competitor
          </Button>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        <Grid container spacing={3}>
          {competitors.map((comp) => (
            <Grid item xs={12} md={6} lg={4} key={comp.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box>
                      <Typography variant="h6">{comp.business_name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {comp.owner_name || 'N/A'}
                      </Typography>
                    </Box>
                    <Chip label={comp.category} color="secondary" size="small" />
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      📍 {comp.location || 'N/A'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      📦 {comp.product_count || 0} Products
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      📊 {comp.sales_records || 0} Sales Records
                    </Typography>
                  </Box>
                  <Button
                    variant="contained"
                    size="small"
                    fullWidth
                    onClick={() => handleViewDetails(comp)}
                  >
                    Manage
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Add Competitor Dialog */}
        <Dialog open={addDialog} onClose={() => setAddDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add New Competitor</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'grid', gap: 2, mt: 1 }}>
              <TextField
                label="Business Name"
                value={form.business_name}
                onChange={(e) => setForm({ ...form, business_name: e.target.value })}
                fullWidth
                required
              />
              <TextField
                label="Owner Name"
                value={form.owner_name}
                onChange={(e) => setForm({ ...form, owner_name: e.target.value })}
                fullWidth
              />
              <TextField
                label="Category"
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                fullWidth
                required
                helperText="e.g., Electronics, Clothing, Food, Hardware"
              />
              <TextField
                label="Location"
                value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
                fullWidth
              />
              <TextField
                label="Phone"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                fullWidth
              />
              <TextField
                label="Email"
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                fullWidth
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAddDialog(false)}>Cancel</Button>
            <Button onClick={handleAddCompetitor} variant="contained">
              Add Competitor
            </Button>
          </DialogActions>
        </Dialog>

        {/* Competitor Details Dialog */}
        <Dialog open={detailsDialog} onClose={() => setDetailsDialog(false)} maxWidth="md" fullWidth>
          <DialogTitle>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="h6">{selectedCompetitor?.business_name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedCompetitor?.category} • {selectedCompetitor?.location}
                </Typography>
              </Box>
            </Box>
          </DialogTitle>
          <DialogContent>
            <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ mb: 2 }}>
              <Tab label="Products" />
              <Tab label="Sales Data" />
            </Tabs>

            {/* Products Tab */}
            {tabValue === 0 && (
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6">Products & Pricing</Typography>
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<Add />}
                    onClick={handleAddProduct}
                  >
                    Add Product
                  </Button>
                </Box>

                {competitorProducts.length > 0 ? (
                  <TableContainer component={Paper} variant="outlined">
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Product Name</TableCell>
                          <TableCell>Category</TableCell>
                          <TableCell align="right">Price</TableCell>
                          <TableCell align="center">Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {competitorProducts.map((product) => (
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
                            <TableCell align="center">
                              <IconButton
                                size="small"
                                color="primary"
                                onClick={() => handleEditProduct(product)}
                              >
                                <Edit fontSize="small" />
                              </IconButton>
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleDeleteProduct(product.id)}
                              >
                                <Delete fontSize="small" />
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Alert severity="info">No products added yet. Click "Add Product" to start.</Alert>
                )}
              </Box>
            )}

            {/* Sales Data Tab */}
            {tabValue === 1 && (
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6">Sales Data</Typography>
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<Add />}
                    onClick={handleAddSales}
                  >
                    Add Sales Data
                  </Button>
                </Box>
                <Alert severity="info">
                  Sales data helps track competitor performance over time. Add daily, monthly, or yearly sales figures.
                </Alert>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDetailsDialog(false)}>Close</Button>
          </DialogActions>
        </Dialog>

        {/* Add/Edit Product Dialog */}
        <Dialog open={productDialog} onClose={() => setProductDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>{editingProduct ? 'Edit Product' : 'Add Product'}</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'grid', gap: 2, mt: 1 }}>
              <TextField
                label="Product Name"
                value={productForm.product_name}
                onChange={(e) => setProductForm({ ...productForm, product_name: e.target.value })}
                fullWidth
                required
              />
              <TextField
                label="Category"
                value={productForm.category}
                onChange={(e) => setProductForm({ ...productForm, category: e.target.value })}
                fullWidth
                required
                helperText="e.g., Electronics, Clothing, Food"
              />
              <TextField
                label="Price (KES)"
                type="number"
                value={productForm.price}
                onChange={(e) => setProductForm({ ...productForm, price: e.target.value })}
                fullWidth
                required
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setProductDialog(false)}>Cancel</Button>
            <Button onClick={handleSaveProduct} variant="contained">
              {editingProduct ? 'Update' : 'Add'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Add Sales Data Dialog */}
        <Dialog open={salesDialog} onClose={() => setSalesDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add Sales Data</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'grid', gap: 2, mt: 1 }}>
              <TextField
                label="Date"
                type="date"
                value={salesForm.date}
                onChange={(e) => setSalesForm({ ...salesForm, date: e.target.value })}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
              <TextField
                label="Daily Sales (KES)"
                type="number"
                value={salesForm.daily_sales}
                onChange={(e) => setSalesForm({ ...salesForm, daily_sales: e.target.value })}
                fullWidth
              />
              <TextField
                label="Monthly Sales (KES)"
                type="number"
                value={salesForm.monthly_sales}
                onChange={(e) => setSalesForm({ ...salesForm, monthly_sales: e.target.value })}
                fullWidth
              />
              <TextField
                label="Yearly Sales (KES)"
                type="number"
                value={salesForm.yearly_sales}
                onChange={(e) => setSalesForm({ ...salesForm, yearly_sales: e.target.value })}
                fullWidth
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSalesDialog(false)}>Cancel</Button>
            <Button onClick={handleSaveSales} variant="contained">
              Add Sales Data
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
};

export default AdminCompetitorsPage;
