import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Tooltip,
  Grid,
} from '@mui/material';
import {
  Edit,
  Add,
  Remove,
  Refresh,
  Search,
  FilterList,
  GetApp,
} from '@mui/icons-material';
import { inventoryAPI, productsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';

const InventoryPage = () => {
  const [inventory, setInventory] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [adjustDialog, setAdjustDialog] = useState({ open: false, item: null });
  const [saleDialog, setSaleDialog] = useState({ open: false, item: null });
  const { hasRole } = useAuth();

  useEffect(() => {
    loadData();
  }, [search, categoryFilter, lowStockOnly]);

  const loadData = async () => {
    try {
      setError('');
      const params = {};
      if (search) params.search = search;
      if (categoryFilter) params.category = categoryFilter;
      if (lowStockOnly) params.low_stock = true;

      const [inventoryRes, categoriesRes] = await Promise.all([
        inventoryAPI.getAll(params),
        productsAPI.getCategories()
      ]);

      setInventory(inventoryRes.data);
      setCategories(categoriesRes.data.categories || []);
    } catch (err) {
      setError('Failed to load inventory data');
    } finally {
      setLoading(false);
    }
  };

  const handleAdjustStock = async (adjustment) => {
    try {
      await inventoryAPI.adjustStock(adjustDialog.item.item_id, adjustment);
      setAdjustDialog({ open: false, item: null });
      loadData();
    } catch (err) {
      setError('Failed to adjust stock');
    }
  };

  const handleRecordSale = async (saleData) => {
    try {
      await inventoryAPI.recordSale(saleDialog.item.item_id, saleData);
      setSaleDialog({ open: false, item: null });
      loadData();
    } catch (err) {
      setError('Failed to record sale');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'out_of_stock': return 'error';
      case 'low_stock': return 'warning';
      case 'in_stock': return 'success';
      default: return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'out_of_stock': return 'Out of Stock';
      case 'low_stock': return 'Low Stock';
      case 'in_stock': return 'In Stock';
      default: return 'Unknown';
    }
  };

  const exportToCSV = () => {
    const headers = ['SKU', 'Name', 'Category', 'Current Stock', 'Reorder Level', 'Unit Price', 'Total Value', 'Status'];
    const csvContent = [
      headers.join(','),
      ...inventory.map(item => [
        item.sku,
        `"${item.name}"`,
        item.category,
        item.current_stock,
        item.reorder_level,
        item.unit_price,
        item.total_value,
        getStatusText(item.status)
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'inventory_report.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <Layout>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Inventory Management
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<GetApp />}
            onClick={exportToCSV}
            sx={{ mr: 1 }}
          >
            Export CSV
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadData}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Search products"
                variant="outlined"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  label="Category"
                >
                  <MenuItem value="">All Categories</MenuItem>
                  {categories.map((category) => (
                    <MenuItem key={category} value={category}>
                      {category}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Button
                variant={lowStockOnly ? 'contained' : 'outlined'}
                startIcon={<FilterList />}
                onClick={() => setLowStockOnly(!lowStockOnly)}
                fullWidth
              >
                {lowStockOnly ? 'Show All' : 'Low Stock Only'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Inventory Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>SKU</TableCell>
                <TableCell>Product Name</TableCell>
                <TableCell>Category</TableCell>
                <TableCell align="right">Current Stock</TableCell>
                <TableCell align="right">Reorder Level</TableCell>
                <TableCell align="right">Unit Price</TableCell>
                <TableCell align="right">Total Value</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Location</TableCell>
                {hasRole('manager') && <TableCell>Actions</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {inventory
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((item) => (
                  <TableRow key={item.item_id}>
                    <TableCell>{item.sku}</TableCell>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>{item.category}</TableCell>
                    <TableCell align="right">{item.current_stock}</TableCell>
                    <TableCell align="right">{item.reorder_level}</TableCell>
                    <TableCell align="right">KES {item.unit_price}</TableCell>
                    <TableCell align="right">KES {item.total_value?.toFixed(2)}</TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusText(item.status)}
                        color={getStatusColor(item.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{item.location}</TableCell>
                    {hasRole('manager') && (
                      <TableCell>
                        <Tooltip title="Adjust Stock">
                          <IconButton
                            size="small"
                            onClick={() => setAdjustDialog({ open: true, item })}
                          >
                            <Edit />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Record Sale">
                          <IconButton
                            size="small"
                            onClick={() => setSaleDialog({ open: true, item })}
                            disabled={item.current_stock === 0}
                          >
                            <Remove />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    )}
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={inventory.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(event, newPage) => setPage(newPage)}
          onRowsPerPageChange={(event) => {
            setRowsPerPage(parseInt(event.target.value, 10));
            setPage(0);
          }}
        />
      </Card>

      {/* Stock Adjustment Dialog */}
      <StockAdjustmentDialog
        open={adjustDialog.open}
        item={adjustDialog.item}
        onClose={() => setAdjustDialog({ open: false, item: null })}
        onSubmit={handleAdjustStock}
      />

      {/* Sale Recording Dialog */}
      <SaleRecordDialog
        open={saleDialog.open}
        item={saleDialog.item}
        onClose={() => setSaleDialog({ open: false, item: null })}
        onSubmit={handleRecordSale}
      />
    </Layout>
  );
};

// Stock Adjustment Dialog Component
const StockAdjustmentDialog = ({ open, item, onClose, onSubmit }) => {
  const [type, setType] = useState('add');
  const [quantity, setQuantity] = useState('');
  const [reason, setReason] = useState('');

  const handleSubmit = () => {
    onSubmit({
      type,
      quantity: parseInt(quantity),
      reason: reason || 'Manual adjustment'
    });
    setQuantity('');
    setReason('');
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Adjust Stock - {item?.name}</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Current Stock: {item?.current_stock}
          </Typography>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Adjustment Type</InputLabel>
            <Select value={type} onChange={(e) => setType(e.target.value)} label="Adjustment Type">
              <MenuItem value="add">Add Stock</MenuItem>
              <MenuItem value="remove">Remove Stock</MenuItem>
              <MenuItem value="set">Set Stock Level</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Quantity"
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Reason"
            multiline
            rows={2}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={!quantity}>
          Adjust Stock
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Sale Recording Dialog Component
const SaleRecordDialog = ({ open, item, onClose, onSubmit }) => {
  const [quantity, setQuantity] = useState('');
  const [unitPrice, setUnitPrice] = useState('');

  useEffect(() => {
    if (item) {
      setUnitPrice(item.unit_price.toString());
    }
  }, [item]);

  const handleSubmit = () => {
    onSubmit({
      quantity_sold: parseInt(quantity),
      unit_price: parseFloat(unitPrice)
    });
    setQuantity('');
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Record Sale - {item?.name}</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Available Stock: {item?.current_stock}
          </Typography>
          <TextField
            fullWidth
            label="Quantity Sold"
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            inputProps={{ max: item?.current_stock }}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Unit Price"
            type="number"
            step="0.01"
            value={unitPrice}
            onChange={(e) => setUnitPrice(e.target.value)}
          />
          {quantity && unitPrice && (
            <Typography variant="h6" sx={{ mt: 2 }}>
              Total: ${(parseInt(quantity || 0) * parseFloat(unitPrice || 0)).toFixed(2)}
            </Typography>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          disabled={!quantity || !unitPrice || parseInt(quantity) > item?.current_stock}
        >
          Record Sale
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default InventoryPage;
