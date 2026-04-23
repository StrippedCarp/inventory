import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Tabs, Tab, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper, Chip, Alert, Grid, Button,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem,
  IconButton, Divider
} from '@mui/material';
import { Edit, Delete, PersonAdd, Refresh, Email, Sms, Visibility, Business } from '@mui/icons-material';
import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const AdminPortal = () => {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [users, setUsers] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [competitors, setCompetitors] = useState([]);
  const [supplierContacts, setSupplierContacts] = useState([]);
  const [customerContacts, setCustomerContacts] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  // User management state
  const [openUserDialog, setOpenUserDialog] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [userFormData, setUserFormData] = useState({ username: '', email: '', password: '', role: 'viewer' });

  // Contact detail dialog
  const [openContactDialog, setOpenContactDialog] = useState(false);
  const [selectedContact, setSelectedContact] = useState(null);

  useEffect(() => {
    fetchData();
  }, [tabValue]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (tabValue === 0) {
        await fetchUsers();
      } else if (tabValue === 1) {
        await fetchSuppliers();
      } else if (tabValue === 2) {
        await fetchCompetitors();
      } else if (tabValue === 3) {
        await fetchContacts();
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  const fetchUsers = async () => {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(`${API_URL}/users`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setUsers(response.data);
  };

  const fetchSuppliers = async () => {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(`${API_URL}/suppliers`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setSuppliers(response.data);
  };

  const fetchCompetitors = async () => {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(`${API_URL}/competitors`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setCompetitors(response.data.competitors || []);
  };

  const fetchContacts = async () => {
    const token = localStorage.getItem('access_token');
    const [supplierRes, customerRes] = await Promise.all([
      axios.get(`${API_URL}/admin/supplier-contacts`, {
        headers: { Authorization: `Bearer ${token}` }
      }),
      axios.get(`${API_URL}/admin/customer-contacts`, {
        headers: { Authorization: `Bearer ${token}` }
      })
    ]);
    setSupplierContacts(supplierRes.data);
    setCustomerContacts(customerRes.data);
  };

  // User Management Functions
  const handleOpenUserDialog = (user = null) => {
    if (user) {
      setEditingUser(user);
      setUserFormData({ username: user.username, email: user.email, password: '', role: user.role });
    } else {
      setEditingUser(null);
      setUserFormData({ username: '', email: '', password: '', role: 'viewer' });
    }
    setOpenUserDialog(true);
    setError('');
  };

  const handleCloseUserDialog = () => {
    setOpenUserDialog(false);
    setEditingUser(null);
    setUserFormData({ username: '', email: '', password: '', role: 'viewer' });
    setError('');
  };

  const handleSubmitUser = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (editingUser) {
        await axios.put(`${API_URL}/users/${editingUser.id}`, userFormData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSuccess('User updated successfully');
      } else {
        await axios.post(`${API_URL}/users`, userFormData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSuccess('User created successfully');
      }
      fetchUsers();
      handleCloseUserDialog();
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError(error.response?.data?.message || 'Error saving user');
    }
  };

  const handleDeleteUser = async (id) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        const token = localStorage.getItem('access_token');
        await axios.delete(`${API_URL}/users/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSuccess('User deleted successfully');
        fetchUsers();
        setTimeout(() => setSuccess(''), 3000);
      } catch (error) {
        setError('Error deleting user');
      }
    }
  };

  const handleViewContact = (contact) => {
    setSelectedContact(contact);
    setOpenContactDialog(true);
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'error';
      case 'manager': return 'warning';
      default: return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'sent': return 'success';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4">Admin Portal</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
              <Business fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                Managing {user?.organization_name || 'Default Organization'}
              </Typography>
            </Box>
          </Box>
          <Button variant="outlined" startIcon={<Refresh />} onClick={fetchData}>
            Refresh
          </Button>
        </Box>

        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Card>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab label="Users" />
            <Tab label="Suppliers" />
            <Tab label="Competitors" />
            <Tab label="Communications" />
          </Tabs>

          <CardContent>
            {/* Users Tab */}
            {tabValue === 0 && (
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6">System Users</Typography>
                  <Button variant="contained" startIcon={<PersonAdd />} onClick={() => handleOpenUserDialog()}>
                    Add User
                  </Button>
                </Box>
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>ID</TableCell>
                        <TableCell>Username</TableCell>
                        <TableCell>Email</TableCell>
                        <TableCell>Role</TableCell>
                        <TableCell>Created At</TableCell>
                        <TableCell align="right">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {users.map((user) => (
                        <TableRow key={user.id}>
                          <TableCell>{user.id}</TableCell>
                          <TableCell>{user.username}</TableCell>
                          <TableCell>{user.email}</TableCell>
                          <TableCell>
                            <Chip label={user.role} color={getRoleColor(user.role)} size="small" />
                          </TableCell>
                          <TableCell>{new Date(user.created_at).toLocaleDateString()}</TableCell>
                          <TableCell align="right">
                            <IconButton onClick={() => handleOpenUserDialog(user)} color="primary" size="small">
                              <Edit />
                            </IconButton>
                            <IconButton onClick={() => handleDeleteUser(user.id)} color="error" size="small">
                              <Delete />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}

            {/* Suppliers Tab */}
            {tabValue === 1 && (
              <Box>
                <Typography variant="h6" sx={{ mb: 2 }}>All Suppliers</Typography>
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>ID</TableCell>
                        <TableCell>Name</TableCell>
                        <TableCell>Contact Person</TableCell>
                        <TableCell>Email</TableCell>
                        <TableCell>Phone</TableCell>
                        <TableCell>Lead Time</TableCell>
                        <TableCell>Rating</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {suppliers.map((supplier) => (
                        <TableRow key={supplier.id}>
                          <TableCell>{supplier.id}</TableCell>
                          <TableCell>{supplier.name}</TableCell>
                          <TableCell>{supplier.contact_person || '-'}</TableCell>
                          <TableCell>{supplier.email}</TableCell>
                          <TableCell>{supplier.phone || '-'}</TableCell>
                          <TableCell>{supplier.lead_time_days} days</TableCell>
                          <TableCell>
                            <Chip label={supplier.rating.toFixed(1)} color="primary" size="small" />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}

            {/* Competitors Tab */}
            {tabValue === 2 && (
              <Box>
                <Typography variant="h6" sx={{ mb: 2 }}>All Competitors</Typography>
                {competitors.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body1" color="text.secondary">
                      No competitors found. Add products to see relevant competitors.
                    </Typography>
                  </Box>
                ) : (
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>ID</TableCell>
                          <TableCell>Business Name</TableCell>
                          <TableCell>Owner</TableCell>
                          <TableCell>Category</TableCell>
                          <TableCell>Location</TableCell>
                          <TableCell>Email</TableCell>
                          <TableCell>Phone</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {competitors.map((competitor) => (
                          <TableRow key={competitor.id}>
                            <TableCell>{competitor.id}</TableCell>
                            <TableCell>{competitor.business_name}</TableCell>
                            <TableCell>{competitor.owner_name || '-'}</TableCell>
                            <TableCell>{competitor.category}</TableCell>
                            <TableCell>{competitor.location || '-'}</TableCell>
                            <TableCell>{competitor.email || '-'}</TableCell>
                            <TableCell>{competitor.phone || '-'}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </Box>
            )}

            {/* Communications Tab */}
            {tabValue === 3 && (
              <Box>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Typography variant="h6" sx={{ mb: 2 }}>Supplier Communications</Typography>
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Date</TableCell>
                            <TableCell>User</TableCell>
                            <TableCell>Supplier</TableCell>
                            <TableCell>Method</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Message Preview</TableCell>
                            <TableCell align="right">Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {supplierContacts.map((contact) => (
                            <TableRow key={contact.id}>
                              <TableCell>{new Date(contact.created_at).toLocaleString()}</TableCell>
                              <TableCell>{contact.user_name}</TableCell>
                              <TableCell>{contact.supplier_name}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={contact.contact_method === 'email' ? <Email /> : <Sms />}
                                  label={contact.contact_method} 
                                  size="small" 
                                />
                              </TableCell>
                              <TableCell>
                                <Chip label={contact.status} color={getStatusColor(contact.status)} size="small" />
                              </TableCell>
                              <TableCell>{contact.message.substring(0, 50)}...</TableCell>
                              <TableCell align="right">
                                <IconButton onClick={() => handleViewContact(contact)} size="small">
                                  <Visibility />
                                </IconButton>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>

                  <Grid item xs={12}>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="h6" sx={{ mb: 2 }}>Customer Communications</Typography>
                    <TableContainer component={Paper}>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Date</TableCell>
                            <TableCell>User</TableCell>
                            <TableCell>Customer</TableCell>
                            <TableCell>Method</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Message Preview</TableCell>
                            <TableCell align="right">Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {customerContacts.map((contact) => (
                            <TableRow key={contact.id}>
                              <TableCell>{new Date(contact.created_at).toLocaleString()}</TableCell>
                              <TableCell>{contact.user_name}</TableCell>
                              <TableCell>{contact.customer_name}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={contact.contact_method === 'email' ? <Email /> : <Sms />}
                                  label={contact.contact_method} 
                                  size="small" 
                                />
                              </TableCell>
                              <TableCell>
                                <Chip label={contact.status} color={getStatusColor(contact.status)} size="small" />
                              </TableCell>
                              <TableCell>{contact.message.substring(0, 50)}...</TableCell>
                              <TableCell align="right">
                                <IconButton onClick={() => handleViewContact(contact)} size="small">
                                  <Visibility />
                                </IconButton>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>
                </Grid>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* User Dialog */}
        <Dialog open={openUserDialog} onClose={handleCloseUserDialog} maxWidth="sm" fullWidth>
          <DialogTitle>{editingUser ? 'Edit User' : 'Add New User'}</DialogTitle>
          <DialogContent>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            <TextField
              fullWidth
              label="Username"
              value={userFormData.username}
              onChange={(e) => setUserFormData({ ...userFormData, username: e.target.value })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={userFormData.email}
              onChange={(e) => setUserFormData({ ...userFormData, email: e.target.value })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label={editingUser ? 'Password (leave blank to keep current)' : 'Password'}
              type="password"
              value={userFormData.password}
              onChange={(e) => setUserFormData({ ...userFormData, password: e.target.value })}
              margin="normal"
              required={!editingUser}
            />
            <TextField
              fullWidth
              select
              label="Role"
              value={userFormData.role}
              onChange={(e) => setUserFormData({ ...userFormData, role: e.target.value })}
              margin="normal"
            >
              <MenuItem value="viewer">Viewer</MenuItem>
              <MenuItem value="manager">Manager</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
            </TextField>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseUserDialog}>Cancel</Button>
            <Button onClick={handleSubmitUser} variant="contained">
              {editingUser ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Contact Detail Dialog */}
        <Dialog open={openContactDialog} onClose={() => setOpenContactDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Communication Details</DialogTitle>
          <DialogContent>
            {selectedContact && (
              <Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Date: {new Date(selectedContact.created_at).toLocaleString()}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>From:</strong> {selectedContact.user_name}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>To:</strong> {selectedContact.supplier_name || selectedContact.customer_name}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>Method:</strong> {selectedContact.contact_method}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>Status:</strong> <Chip label={selectedContact.status} color={getStatusColor(selectedContact.status)} size="small" />
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Typography variant="body2" gutterBottom>
                  <strong>Message:</strong>
                </Typography>
                <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                  <Typography variant="body2" style={{ whiteSpace: 'pre-wrap' }}>
                    {selectedContact.message}
                  </Typography>
                </Paper>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenContactDialog(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
};

export default AdminPortal;
