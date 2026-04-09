import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  IconButton,
  Chip,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { productsAPI } from '../services/api';
import api from '../services/api';

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [open, setOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    category: '',
    unit_price: '',
    description: '',
    supplier_id: '',
    reorder_point: '',
    safety_stock: '',
  });

  const categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Home', 'Sports'];

  useEffect(() => {
    // Test backend connection first
    const testConnection = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/health');
        if (response.ok) {
          console.log('✅ Backend connected');
          fetchProducts();
        } else {
          throw new Error('Backend not responding');
        }
      } catch (err) {
        console.error('❌ Backend connection failed:', err);
        setError('Backend not connected - using demo mode');
        // Load demo data
        setProducts([
          {
            id: 1,
            sku: 'LAPTOP-001',
            name: 'Business Laptop',
            category: 'Electronics',
            unit_price: 899.99,
            current_stock: 15,
            reorder_level: 10
          }
        ]);
        setLoading(false);
      }
    };
    
    testConnection();
  }, []);

  const fetchProducts = async () => {
    try {
      // Try the correct API first
      const response = await productsAPI.getAll();
      setProducts(response.data.products || response.data || []);
    } catch (err) {
      console.error('Fetch error:', err);
      // Fallback to mock data if API fails
      setProducts([
        {
          id: 1,
          sku: 'LAPTOP-001',
          name: 'Business Laptop',
          category: 'Electronics',
          unit_price: 899.99,
          current_stock: 15,
          reorder_level: 10
        },
        {
          id: 2,
          sku: 'MOUSE-001',
          name: 'Wireless Mouse',
          category: 'Electronics',
          unit_price: 29.99,
          current_stock: 25,
          reorder_level: 15
        }
      ]);
      setError('Using demo data - backend not connected');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Basic validation
      if (!formData.name || !formData.sku || !formData.category || !formData.unit_price) {
        setError('Please fill in all required fields (Name, SKU, Category, Price)');
        return;
      }

      const submitData = {
        name: formData.name.trim(),
        sku: formData.sku.trim(),
        category: formData.category,
        unit_price: parseFloat(formData.unit_price),
        description: formData.description || '',
        reorder_point: parseInt(formData.reorder_point) || 10,
        safety_stock: parseInt(formData.safety_stock) || 5,
      };
      
      // Only include supplier_id if it's provided
      if (formData.supplier_id) {
        submitData.supplier_id = parseInt(formData.supplier_id);
      }

      console.log('Submitting product data:', submitData);

      if (editingProduct) {
        await productsAPI.update(editingProduct.id, submitData);
      } else {
        await productsAPI.create(submitData);
      }
      
      await fetchProducts();
      handleClose();
      setError(''); // Clear any previous errors
    } catch (err) {
      console.error('Product save error:', err);
      const errorMsg = err.response?.data?.message || err.message || 'Failed to save product';
      setError(errorMsg);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await productsAPI.delete(id);
        fetchProducts();
      } catch (err) {
        setError('Failed to delete product');
      }
    }
  };

  const handleEdit = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      sku: product.sku,
      category: product.category,
      unit_price: product.unit_price,
      description: product.description || '',
      supplier_id: product.supplier_id || '',
      reorder_point: product.reorder_point || '',
      safety_stock: product.safety_stock || '',
    });
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingProduct(null);
    setFormData({
      name: '',
      sku: '',
      category: '',
      unit_price: '',
      description: '',
      supplier_id: '',
      reorder_point: '',
      safety_stock: '',
    });
  };

  const getStockStatus = (quantity, minLevel) => {
    if (quantity <= minLevel) return { label: 'Low Stock', color: 'error' };
    if (quantity <= minLevel * 1.5) return { label: 'Medium', color: 'warning' };
    return { label: 'Good', color: 'success' };
  };

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">Products</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpen(true)}
          >
            Add Product
          </Button>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Card>
          <CardContent>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>SKU</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Price</TableCell>
                    <TableCell>Reorder Level</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {products.map((product) => (
                      <TableRow key={product.id}>
                        <TableCell>{product.sku}</TableCell>
                        <TableCell>{product.name}</TableCell>
                        <TableCell>{product.category}</TableCell>
                        <TableCell>KES {product.unit_price}</TableCell>
                        <TableCell>{product.reorder_point || 10}</TableCell>
                        <TableCell>
                          <IconButton onClick={() => handleEdit(product)} size="small">
                            <EditIcon />
                          </IconButton>
                          <IconButton onClick={() => handleDelete(product.id)} size="small">
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
          <DialogTitle>
            {editingProduct ? 'Edit Product' : 'Add New Product'}
          </DialogTitle>
          <DialogContent>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            <Box component="form" onSubmit={handleSubmit} sx={{ display: 'grid', gap: 2, mt: 1 }}>
              <TextField
                label="Product Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                fullWidth
                required
              />
              <TextField
                label="SKU"
                value={formData.sku}
                onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                fullWidth
                required
              />
              <TextField
                select
                label="Category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                fullWidth
                required
              >
                {categories.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </TextField>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                <TextField
                  label="Price"
                  type="number"
                  value={formData.unit_price}
                  onChange={(e) => setFormData({ ...formData, unit_price: e.target.value })}
                  required
                />
                <TextField
                  label="Supplier ID (Optional)"
                  type="number"
                  value={formData.supplier_id}
                  onChange={(e) => setFormData({ ...formData, supplier_id: e.target.value })}
                  placeholder="Leave empty for default supplier"
                />
              </Box>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                <TextField
                  label="Reorder Point"
                  type="number"
                  value={formData.reorder_point}
                  onChange={(e) => setFormData({ ...formData, reorder_point: e.target.value })}
                />
                <TextField
                  label="Safety Stock"
                  type="number"
                  value={formData.safety_stock}
                  onChange={(e) => setFormData({ ...formData, safety_stock: e.target.value })}
                />
              </Box>
              <TextField
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                fullWidth
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button type="submit" onClick={handleSubmit} variant="contained">
              {editingProduct ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
};

export default ProductsPage;