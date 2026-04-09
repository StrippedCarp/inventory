import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Button, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper, Chip, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, MenuItem, IconButton, Tabs, Tab,
  Grid, Alert
} from '@mui/material';
import {
  Add as AddIcon, Edit as EditIcon, Star as StarIcon,
  LocalOffer as OfferIcon, History as HistoryIcon
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { customersAPI } from '../services/api';

const CustomersPage = () => {
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [openDetailsDialog, setOpenDetailsDialog] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [formData, setFormData] = useState({
    name: '', email: '', phone: '', address: '', customer_type: 'regular',
    discount_percentage: 0, credit_limit: 0, notes: ''
  });

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await customersAPI.getAll();
      setCustomers(response.data);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    }
  };

  const handleSubmit = async () => {
    try {
      if (formData.id) {
        await customersAPI.update(formData.id, formData);
      } else {
        await customersAPI.create(formData);
      }
      fetchCustomers();
      setOpenDialog(false);
      resetForm();
    } catch (error) {
      console.error('Failed to save customer:', error);
    }
  };

  const handleViewDetails = async (customer) => {
    try {
      const response = await customersAPI.getById(customer.id);
      setSelectedCustomer(response.data);
      setOpenDetailsDialog(true);
    } catch (error) {
      console.error('Failed to fetch customer details:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '', email: '', phone: '', address: '', customer_type: 'regular',
      discount_percentage: 0, credit_limit: 0, notes: ''
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency', currency: 'KES', minimumFractionDigits: 0
    }).format(amount);
  };

  const getCustomerTypeColor = (type) => {
    const colors = { regular: 'default', vip: 'secondary', wholesale: 'primary' };
    return colors[type] || 'default';
  };

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">Customer Management</Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpenDialog(true)}>
            Add Customer
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Contact</TableCell>
                <TableCell>Type</TableCell>
                <TableCell align="right">Loyalty Points</TableCell>
                <TableCell align="right">Total Purchases</TableCell>
                <TableCell align="right">Discount</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {customers.map((customer) => (
                <TableRow key={customer.id} hover>
                  <TableCell>{customer.name}</TableCell>
                  <TableCell>
                    {customer.phone}<br />
                    <Typography variant="caption" color="text.secondary">{customer.email}</Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={customer.customer_type} size="small" color={getCustomerTypeColor(customer.customer_type)} />
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                      <StarIcon sx={{ fontSize: 16, color: 'gold', mr: 0.5 }} />
                      {customer.loyalty_points}
                    </Box>
                  </TableCell>
                  <TableCell align="right">{formatCurrency(customer.total_purchases)}</TableCell>
                  <TableCell align="right">{customer.discount_percentage}%</TableCell>
                  <TableCell>
                    <Chip label={customer.status} size="small" color={customer.status === 'active' ? 'success' : 'default'} />
                  </TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleViewDetails(customer)}>
                      <HistoryIcon />
                    </IconButton>
                    <IconButton size="small" onClick={() => { setFormData(customer); setOpenDialog(true); }}>
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Add/Edit Dialog */}
        <Dialog open={openDialog} onClose={() => { setOpenDialog(false); resetForm(); }} maxWidth="sm" fullWidth>
          <DialogTitle>{formData.id ? 'Edit Customer' : 'Add Customer'}</DialogTitle>
          <DialogContent>
            <TextField 
              fullWidth 
              label="Name" 
              value={formData.name || ''} 
              onChange={(e) => setFormData({ ...formData, name: e.target.value })} 
              margin="normal" 
              required 
            />
            <TextField 
              fullWidth 
              label="Email" 
              type="email" 
              value={formData.email || ''} 
              onChange={(e) => setFormData({ ...formData, email: e.target.value })} 
              margin="normal" 
            />
            <TextField 
              fullWidth 
              label="Phone" 
              value={formData.phone || ''} 
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })} 
              margin="normal" 
            />
            <TextField 
              fullWidth 
              label="Address" 
              multiline 
              rows={2} 
              value={formData.address || ''} 
              onChange={(e) => setFormData({ ...formData, address: e.target.value })} 
              margin="normal" 
            />
            <TextField 
              select 
              fullWidth 
              label="Customer Type" 
              value={formData.customer_type || 'regular'} 
              onChange={(e) => setFormData({ ...formData, customer_type: e.target.value })} 
              margin="normal"
            >
              <MenuItem value="regular">Regular</MenuItem>
              <MenuItem value="vip">VIP</MenuItem>
              <MenuItem value="wholesale">Wholesale</MenuItem>
            </TextField>
            <TextField 
              fullWidth 
              label="Discount %" 
              type="number" 
              value={formData.discount_percentage || 0} 
              onChange={(e) => setFormData({ ...formData, discount_percentage: parseFloat(e.target.value) || 0 })} 
              margin="normal" 
            />
            <TextField 
              fullWidth 
              label="Credit Limit (KES)" 
              type="number" 
              value={formData.credit_limit || 0} 
              onChange={(e) => setFormData({ ...formData, credit_limit: parseFloat(e.target.value) || 0 })} 
              margin="normal" 
            />
            <TextField 
              fullWidth 
              label="Notes" 
              multiline 
              rows={2} 
              value={formData.notes || ''} 
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })} 
              margin="normal" 
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => { setOpenDialog(false); resetForm(); }}>Cancel</Button>
            <Button onClick={handleSubmit} variant="contained" disabled={!formData.name}>Save</Button>
          </DialogActions>
        </Dialog>

        {/* Customer Details Dialog */}
        <Dialog open={openDetailsDialog} onClose={() => setOpenDetailsDialog(false)} maxWidth="md" fullWidth>
          <DialogTitle>{selectedCustomer?.name}</DialogTitle>
          <DialogContent>
            {selectedCustomer && (
              <>
                <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 2 }}>
                  <Tab label="Purchase History" />
                  <Tab label="Loyalty History" />
                  <Tab label="Special Prices" />
                </Tabs>

                {tabValue === 0 && (
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Date</TableCell>
                          <TableCell>Product</TableCell>
                          <TableCell align="right">Quantity</TableCell>
                          <TableCell align="right">Amount</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedCustomer.recent_purchases?.map((purchase) => (
                          <TableRow key={purchase.id}>
                            <TableCell>{new Date(purchase.sale_date).toLocaleDateString()}</TableCell>
                            <TableCell>{purchase.product_name}</TableCell>
                            <TableCell align="right">{purchase.quantity_sold}</TableCell>
                            <TableCell align="right">{formatCurrency(purchase.total_amount)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}

                {tabValue === 1 && (
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Date</TableCell>
                          <TableCell>Type</TableCell>
                          <TableCell align="right">Points</TableCell>
                          <TableCell>Description</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedCustomer.loyalty_history?.map((transaction) => (
                          <TableRow key={transaction.id}>
                            <TableCell>{new Date(transaction.created_at).toLocaleDateString()}</TableCell>
                            <TableCell>{transaction.transaction_type}</TableCell>
                            <TableCell align="right" sx={{ color: transaction.points > 0 ? 'green' : 'red' }}>
                              {transaction.points > 0 ? '+' : ''}{transaction.points}
                            </TableCell>
                            <TableCell>{transaction.description}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}

                {tabValue === 2 && (
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Product</TableCell>
                          <TableCell align="right">Special Price</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedCustomer.special_prices?.map((price) => (
                          <TableRow key={price.id}>
                            <TableCell>{price.product_name}</TableCell>
                            <TableCell align="right">{formatCurrency(price.special_price)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDetailsDialog(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
};

export default CustomersPage;
