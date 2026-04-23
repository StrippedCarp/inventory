import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Chip,
  Alert,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormLabel,
} from '@mui/material';
import {
  Phone as PhoneIcon,
  Email as EmailIcon,
  Business as BusinessIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { suppliersAPI } from '../services/api';

const SuppliersPage = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [contactDialog, setContactDialog] = useState(false);
  const [addDialog, setAddDialog] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState(null);
  const [contactForm, setContactForm] = useState({
    message: '',
    contact_method: 'email'
  });
  const [supplierForm, setSupplierForm] = useState({
    name: '',
    contact_person: '',
    email: '',
    phone: '',
    lead_time_days: 7,
    rating: 5.0
  });

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const fetchSuppliers = async () => {
    try {
      const response = await suppliersAPI.getAll();
      setSuppliers(response.data || []);
    } catch (err) {
      console.error('Suppliers fetch error:', err);
      setSuppliers([
        {
          id: 1,
          name: 'TechCorp Solutions',
          contact_person: 'John Smith',
          email: 'john@techcorp.com',
          phone: '+254-712-345678',
          lead_time_days: 7,
          rating: 4.5
        }
      ]);
      setError('Using demo data - backend not connected');
    } finally {
      setLoading(false);
    }
  };

  const handleContactSupplier = (supplier) => {
    setSelectedSupplier(supplier);
    setContactDialog(true);
  };

  const handleSendContact = async () => {
    try {
      await suppliersAPI.contact(selectedSupplier.id, contactForm);
      setSuccess(`Contact request sent to ${selectedSupplier.name}`);
      setContactDialog(false);
      setContactForm({ message: '', contact_method: 'email' });
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to send contact request');
    }
  };

  const handleAddSupplier = async () => {
    try {
      await suppliersAPI.create(supplierForm);
      setSuccess('Supplier added successfully');
      setAddDialog(false);
      setSupplierForm({
        name: '',
        contact_person: '',
        email: '',
        phone: '',
        lead_time_days: 7,
        rating: 5.0
      });
      fetchSuppliers();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to add supplier');
    }
  };

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Suppliers</Typography>
          <Button variant="contained" onClick={() => setAddDialog(true)}>
            Add Supplier
          </Button>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        <Grid container spacing={3}>
          {suppliers.map((supplier) => (
            <Grid item xs={12} md={6} lg={4} key={supplier.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="div">
                      {supplier.name}
                    </Typography>
                    <Chip label={`Rating: ${supplier.rating || 5.0}`} color="primary" size="small" />
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <BusinessIcon sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {supplier.contact_person}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <EmailIcon sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {supplier.email}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <PhoneIcon sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {supplier.phone}
                      </Typography>
                    </Box>
                  </Box>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Lead Time: {supplier.lead_time_days || 7} days
                  </Typography>

                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<SendIcon />}
                      onClick={() => handleContactSupplier(supplier)}
                    >
                      Contact
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Dialog open={contactDialog} onClose={() => setContactDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Contact {selectedSupplier?.name}</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'grid', gap: 2, mt: 1 }}>
              <FormLabel>Contact Method</FormLabel>
              <RadioGroup
                value={contactForm.contact_method}
                onChange={(e) => setContactForm({ ...contactForm, contact_method: e.target.value })}
              >
                <FormControlLabel value="email" control={<Radio />} label="Email" />
                <FormControlLabel value="sms" control={<Radio />} label="SMS" />
              </RadioGroup>
              <TextField
                label="Message"
                multiline
                rows={4}
                value={contactForm.message}
                onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                fullWidth
                required
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setContactDialog(false)}>Cancel</Button>
            <Button onClick={handleSendContact} variant="contained" startIcon={<SendIcon />}>
              Send
            </Button>
          </DialogActions>
        </Dialog>

        <Dialog open={addDialog} onClose={() => setAddDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add New Supplier</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'grid', gap: 2, mt: 1 }}>
              <TextField
                label="Supplier Name"
                value={supplierForm.name}
                onChange={(e) => setSupplierForm({ ...supplierForm, name: e.target.value })}
                fullWidth
                required
              />
              <TextField
                label="Contact Person"
                value={supplierForm.contact_person}
                onChange={(e) => setSupplierForm({ ...supplierForm, contact_person: e.target.value })}
                fullWidth
              />
              <TextField
                label="Email"
                type="email"
                value={supplierForm.email}
                onChange={(e) => setSupplierForm({ ...supplierForm, email: e.target.value })}
                fullWidth
                required
              />
              <TextField
                label="Phone"
                value={supplierForm.phone}
                onChange={(e) => setSupplierForm({ ...supplierForm, phone: e.target.value })}
                fullWidth
              />
              <TextField
                label="Lead Time (Days)"
                type="number"
                value={supplierForm.lead_time_days}
                onChange={(e) => setSupplierForm({ ...supplierForm, lead_time_days: parseInt(e.target.value) })}
                fullWidth
              />
              <TextField
                label="Rating (1-5)"
                type="number"
                inputProps={{ min: 1, max: 5, step: 0.1 }}
                value={supplierForm.rating}
                onChange={(e) => setSupplierForm({ ...supplierForm, rating: parseFloat(e.target.value) })}
                fullWidth
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAddDialog(false)}>Cancel</Button>
            <Button onClick={handleAddSupplier} variant="contained">
              Add Supplier
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
};

export default SuppliersPage;