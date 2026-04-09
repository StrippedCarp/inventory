import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Button, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper, Chip, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, MenuItem, Grid, Alert, Tabs, Tab
} from '@mui/material';
import {
  Add as AddIcon, Warning as WarningIcon, Inventory as InventoryIcon
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { batchesAPI, productsAPI, suppliersAPI } from '../services/api';

const BatchesPage = () => {
  const [batches, setBatches] = useState([]);
  const [expiringBatches, setExpiringBatches] = useState([]);
  const [valuation, setValuation] = useState(null);
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [valuationMethod, setValuationMethod] = useState('fifo');
  const [formData, setFormData] = useState({
    product_id: '', batch_number: '', quantity: 0, cost_per_unit: 0,
    manufacture_date: '', expiry_date: '', supplier_id: ''
  });

  useEffect(() => {
    fetchBatches();
    fetchExpiringBatches();
    fetchProducts();
    fetchSuppliers();
    fetchValuation('fifo');
  }, []);

  const fetchBatches = async () => {
    try {
      const response = await batchesAPI.getAll();
      setBatches(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to fetch batches:', error);
      setBatches([]);
    }
  };

  const fetchExpiringBatches = async () => {
    try {
      const response = await batchesAPI.getExpiring({ days: 30 });
      setExpiringBatches(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to fetch expiring batches:', error);
      setExpiringBatches([]);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await productsAPI.getAll();
      setProducts(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to fetch products:', error);
      setProducts([]);
    }
  };

  const fetchSuppliers = async () => {
    try {
      const response = await suppliersAPI.getAll();
      setSuppliers(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to fetch suppliers:', error);
      setSuppliers([]);
    }
  };

  const fetchValuation = async (method) => {
    try {
      const response = await batchesAPI.getValuation({ method });
      setValuation(response.data);
    } catch (error) {
      console.error('Failed to fetch valuation:', error);
    }
  };

  const handleSubmit = async () => {
    try {
      await batchesAPI.create(formData);
      fetchBatches();
      fetchValuation(valuationMethod);
      setOpenDialog(false);
      resetForm();
    } catch (error) {
      console.error('Failed to create batch:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      product_id: '', batch_number: '', quantity: 0, cost_per_unit: 0,
      manufacture_date: '', expiry_date: '', supplier_id: ''
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency', currency: 'KES', minimumFractionDigits: 0
    }).format(amount);
  };

  const getStatusColor = (status) => {
    const colors = { active: 'success', expired: 'error', depleted: 'default' };
    return colors[status] || 'default';
  };

  const getDaysUntilExpiry = (expiryDate) => {
    if (!expiryDate) return null;
    const days = Math.ceil((new Date(expiryDate) - new Date()) / (1000 * 60 * 60 * 24));
    return days;
  };

  const getExpiryWarning = (days) => {
    if (days === null) return null;
    if (days < 0) return { color: 'error', text: 'EXPIRED' };
    if (days <= 7) return { color: 'error', text: `${days} days` };
    if (days <= 30) return { color: 'warning', text: `${days} days` };
    return { color: 'success', text: `${days} days` };
  };

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">Batch & Lot Tracking</Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpenDialog(true)}>
            Add Batch
          </Button>
        </Box>

        {expiringBatches.length > 0 && (
          <Alert severity="warning" icon={<WarningIcon />} sx={{ mb: 3 }}>
            {expiringBatches.length} batch(es) expiring within 30 days
          </Alert>
        )}

        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
          <Tab label="All Batches" />
          <Tab label="Expiring Soon" />
          <Tab label="Inventory Valuation" />
        </Tabs>

        {tabValue === 0 && (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Batch Number</TableCell>
                  <TableCell>Product</TableCell>
                  <TableCell>Supplier</TableCell>
                  <TableCell align="right">Quantity</TableCell>
                  <TableCell align="right">Cost/Unit</TableCell>
                  <TableCell align="right">Total Value</TableCell>
                  <TableCell>Expiry Date</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {batches.map((batch) => {
                  const days = getDaysUntilExpiry(batch.expiry_date);
                  const warning = getExpiryWarning(days);
                  return (
                    <TableRow key={batch.id} hover>
                      <TableCell>{batch.batch_number}</TableCell>
                      <TableCell>{batch.product_name}</TableCell>
                      <TableCell>{batch.supplier_name || '-'}</TableCell>
                      <TableCell align="right">{batch.quantity}</TableCell>
                      <TableCell align="right">{formatCurrency(batch.cost_per_unit)}</TableCell>
                      <TableCell align="right">{formatCurrency(batch.quantity * batch.cost_per_unit)}</TableCell>
                      <TableCell>
                        {batch.expiry_date ? (
                          <Box>
                            {new Date(batch.expiry_date).toLocaleDateString()}
                            {warning && (
                              <Chip label={warning.text} size="small" color={warning.color} sx={{ ml: 1 }} />
                            )}
                          </Box>
                        ) : '-'}
                      </TableCell>
                      <TableCell>
                        <Chip label={batch.status} size="small" color={getStatusColor(batch.status)} />
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {tabValue === 1 && (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Batch Number</TableCell>
                  <TableCell>Product</TableCell>
                  <TableCell align="right">Quantity</TableCell>
                  <TableCell>Expiry Date</TableCell>
                  <TableCell>Days Until Expiry</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {expiringBatches.map((batch) => {
                  const days = getDaysUntilExpiry(batch.expiry_date);
                  const warning = getExpiryWarning(days);
                  return (
                    <TableRow key={batch.id} hover>
                      <TableCell>{batch.batch_number}</TableCell>
                      <TableCell>{batch.product_name}</TableCell>
                      <TableCell align="right">{batch.quantity}</TableCell>
                      <TableCell>{new Date(batch.expiry_date).toLocaleDateString()}</TableCell>
                      <TableCell>
                        {warning && <Chip label={warning.text} size="small" color={warning.color} />}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {tabValue === 2 && (
          <Box>
            <Box sx={{ mb: 3 }}>
              <TextField
                select
                label="Valuation Method"
                value={valuationMethod}
                onChange={(e) => {
                  setValuationMethod(e.target.value);
                  fetchValuation(e.target.value);
                }}
                sx={{ width: 200 }}
              >
                <MenuItem value="fifo">FIFO (First In, First Out)</MenuItem>
                <MenuItem value="lifo">LIFO (Last In, First Out)</MenuItem>
              </TextField>
            </Box>

            {valuation && (
              <>
                <Grid container spacing={3} sx={{ mb: 3 }}>
                  <Grid item xs={12} md={4}>
                    <Card sx={{ bgcolor: '#e3f2fd' }}>
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">Total Inventory Value</Typography>
                        <Typography variant="h4">{formatCurrency(valuation.total_value)}</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Card sx={{ bgcolor: '#f3e5f5' }}>
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">Total Quantity</Typography>
                        <Typography variant="h4">{valuation.total_quantity}</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Card sx={{ bgcolor: '#e8f5e9' }}>
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">Average Cost</Typography>
                        <Typography variant="h4">{formatCurrency(valuation.average_cost)}</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Batch Number</TableCell>
                        <TableCell>Product</TableCell>
                        <TableCell align="right">Quantity</TableCell>
                        <TableCell align="right">Cost/Unit</TableCell>
                        <TableCell align="right">Total Value</TableCell>
                        <TableCell>Received Date</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {valuation.batches?.map((batch, index) => (
                        <TableRow key={index}>
                          <TableCell>{batch.batch_number}</TableCell>
                          <TableCell>{batch.product_name}</TableCell>
                          <TableCell align="right">{batch.quantity}</TableCell>
                          <TableCell align="right">{formatCurrency(batch.cost_per_unit)}</TableCell>
                          <TableCell align="right">{formatCurrency(batch.total_value)}</TableCell>
                          <TableCell>{new Date(batch.received_date).toLocaleDateString()}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            )}
          </Box>
        )}

        {/* Add Batch Dialog */}
        <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add New Batch</DialogTitle>
          <DialogContent>
            <TextField
              select
              fullWidth
              label="Product"
              value={formData.product_id}
              onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
              margin="normal"
              required
            >
              {products.map((product) => (
                <MenuItem key={product.id} value={product.id}>{product.name}</MenuItem>
              ))}
            </TextField>
            <TextField
              fullWidth
              label="Batch Number"
              value={formData.batch_number}
              onChange={(e) => setFormData({ ...formData, batch_number: e.target.value })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Quantity"
              type="number"
              value={formData.quantity}
              onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Cost Per Unit (KES)"
              type="number"
              value={formData.cost_per_unit}
              onChange={(e) => setFormData({ ...formData, cost_per_unit: parseFloat(e.target.value) })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Manufacture Date"
              type="date"
              value={formData.manufacture_date}
              onChange={(e) => setFormData({ ...formData, manufacture_date: e.target.value })}
              margin="normal"
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              fullWidth
              label="Expiry Date"
              type="date"
              value={formData.expiry_date}
              onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
              margin="normal"
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              select
              fullWidth
              label="Supplier"
              value={formData.supplier_id}
              onChange={(e) => setFormData({ ...formData, supplier_id: e.target.value })}
              margin="normal"
            >
              <MenuItem value="">None</MenuItem>
              {suppliers.map((supplier) => (
                <MenuItem key={supplier.id} value={supplier.id}>{supplier.name}</MenuItem>
              ))}
            </TextField>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => { setOpenDialog(false); resetForm(); }}>Cancel</Button>
            <Button onClick={handleSubmit} variant="contained">Add Batch</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
};

export default BatchesPage;
