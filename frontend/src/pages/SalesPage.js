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
  Grid,
  Autocomplete,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  ShoppingCart as CartIcon,
  AttachMoney as MoneyIcon,
  Receipt as ReceiptIcon,
} from '@mui/icons-material';
import Layout from '../components/Layout';
import { salesAPI, inventoryAPI, productsAPI } from '../services/api';

const SalesPage = () => {
  const [sales, setSales] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [products, setProducts] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [cart, setCart] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [paymentMethod, setPaymentMethod] = useState('cash');

  const [stats, setStats] = useState({
    totalSales: 0,
    totalRevenue: 0,
    todayRevenue: 0,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [salesRes, productsRes, transactionsRes, inventoryRes] = await Promise.all([
        salesAPI.getDailySales().catch(() => ({ data: [] })),
        productsAPI.getAll().catch(() => ({ data: { products: [] } })),
        salesAPI.getAll().catch(() => ({ data: { sales: [] } })),
        inventoryAPI.getAll().catch(() => ({ data: [] }))
      ]);
      
      setSales(salesRes.data || []);
      setProducts(productsRes.data.products || productsRes.data || []);
      setTransactions(transactionsRes.data.sales || transactionsRes.data || []);
      setInventory(inventoryRes.data || []);
      calculateStats(salesRes.data || []);
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Failed to load data');
    }
  };

  const calculateStats = (salesData) => {
    const totalRevenue = salesData.reduce((sum, day) => sum + (day.total_revenue || 0), 0);
    const today = new Date().toISOString().split('T')[0];
    const todayData = salesData.find(d => d.date === today);
    
    setStats({
      totalSales: salesData.reduce((sum, day) => sum + (day.transaction_count || 0), 0),
      totalRevenue: totalRevenue,
      todayRevenue: todayData?.total_revenue || 0,
    });
  };

  const addToCart = () => {
    if (!selectedProduct || quantity <= 0) {
      setError('Please select a product and quantity');
      return;
    }

    // Check stock availability
    const inventoryItem = inventory.find(item => item.item_id === selectedProduct.id);
    if (!inventoryItem) {
      setError(`${selectedProduct.name} has no inventory record`);
      return;
    }

    const currentStock = inventoryItem.current_stock || 0;
    const cartQuantity = cart.find(item => item.product_id === selectedProduct.id)?.quantity || 0;
    const totalRequested = cartQuantity + quantity;

    if (currentStock === 0) {
      setError(`${selectedProduct.name} is out of stock`);
      return;
    }

    if (totalRequested > currentStock) {
      setError(`Insufficient stock for ${selectedProduct.name}. Available: ${currentStock}, In cart: ${cartQuantity}`);
      return;
    }

    const existingItem = cart.find(item => item.product_id === selectedProduct.id);
    
    if (existingItem) {
      setCart(cart.map(item =>
        item.product_id === selectedProduct.id
          ? { ...item, quantity: item.quantity + quantity }
          : item
      ));
    } else {
      setCart([...cart, {
        product_id: selectedProduct.id,
        name: selectedProduct.name,
        sku: selectedProduct.sku,
        unit_price: selectedProduct.unit_price,
        quantity: quantity,
        subtotal: selectedProduct.unit_price * quantity,
        available_stock: currentStock
      }]);
    }

    setSelectedProduct(null);
    setQuantity(1);
    setError('');
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.product_id !== productId));
  };

  const updateCartQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }

    // Check stock availability
    const cartItem = cart.find(item => item.product_id === productId);
    if (cartItem && newQuantity > cartItem.available_stock) {
      setError(`Cannot exceed available stock (${cartItem.available_stock}) for ${cartItem.name}`);
      return;
    }
    
    setCart(cart.map(item =>
      item.product_id === productId
        ? { ...item, quantity: newQuantity, subtotal: item.unit_price * newQuantity }
        : item
    ));
    setError('');
  };

  const calculateTotal = () => {
    return cart.reduce((sum, item) => sum + item.subtotal, 0);
  };

  const handleCheckout = async () => {
    if (cart.length === 0) {
      setError('Cart is empty');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Record each sale and update inventory
      for (const item of cart) {
        await inventoryAPI.recordSale(item.product_id, {
          quantity_sold: item.quantity,
          unit_price: item.unit_price
        });
      }

      setSuccess(`Sale completed! Total: KES ${calculateTotal().toFixed(2)}`);
      setCart([]);
      setOpen(false);
      fetchData(); // Refresh data
      
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      console.error('Checkout error:', err);
      setError(err.response?.data?.message || 'Failed to complete sale. Check stock availability.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setOpen(false);
    setCart([]);
    setSelectedProduct(null);
    setQuantity(1);
    setError('');
  };

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">Sales</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpen(true)}
          >
            New Sale
          </Button>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <ReceiptIcon sx={{ mr: 2, color: 'primary.main', fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Transactions
                    </Typography>
                    <Typography variant="h5">
                      {stats.totalSales}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <MoneyIcon sx={{ mr: 2, color: 'success.main', fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Revenue (30 days)
                    </Typography>
                    <Typography variant="h5">
                      KES {stats.totalRevenue.toFixed(2)}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CartIcon sx={{ mr: 2, color: 'info.main', fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Today's Revenue
                    </Typography>
                    <Typography variant="h5">
                      KES {stats.todayRevenue.toFixed(2)}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Sales History */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Transactions
                </Typography>
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Product</TableCell>
                        <TableCell align="right">Qty</TableCell>
                        <TableCell align="right">Amount</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {transactions.slice(0, 10).map((txn) => (
                        <TableRow key={txn.id}>
                          <TableCell>{new Date(txn.sale_date).toLocaleDateString()}</TableCell>
                          <TableCell>{txn.product_name || `Product ${txn.product_id}`}</TableCell>
                          <TableCell align="right">{txn.quantity_sold}</TableCell>
                          <TableCell align="right">KES {(txn.total_amount || 0).toFixed(2)}</TableCell>
                        </TableRow>
                      ))}
                      {transactions.length === 0 && (
                        <TableRow>
                          <TableCell colSpan={4} align="center">
                            No transactions yet
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Daily Sales Summary
                </Typography>
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell align="right">Transactions</TableCell>
                        <TableCell align="right">Revenue</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {sales.slice(0, 10).map((day, index) => (
                        <TableRow key={index}>
                          <TableCell>{new Date(day.date).toLocaleDateString()}</TableCell>
                          <TableCell align="right">{day.transaction_count || 0}</TableCell>
                          <TableCell align="right">KES {(day.total_revenue || 0).toFixed(2)}</TableCell>
                        </TableRow>
                      ))}
                      {sales.length === 0 && (
                        <TableRow>
                          <TableCell colSpan={3} align="center">
                            No sales data available
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* New Sale Dialog */}
        <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
          <DialogTitle>New Sale</DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
              
              {/* Product Selection */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6}>
                  <Autocomplete
                    options={products}
                    getOptionLabel={(option) => `${option.name} (${option.sku})`}
                    value={selectedProduct}
                    onChange={(e, newValue) => setSelectedProduct(newValue)}
                    renderInput={(params) => (
                      <TextField {...params} label="Select Product" />
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={3}>
                  <TextField
                    label="Quantity"
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                    fullWidth
                    inputProps={{ min: 1 }}
                  />
                </Grid>
                <Grid item xs={12} sm={3}>
                  <Button
                    variant="contained"
                    onClick={addToCart}
                    fullWidth
                    sx={{ height: '56px' }}
                  >
                    Add to Cart
                  </Button>
                </Grid>
              </Grid>

              {/* Cart */}
              <Typography variant="h6" gutterBottom>
                Cart Items
              </Typography>
              <TableContainer component={Paper} sx={{ mb: 2 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Product</TableCell>
                      <TableCell>SKU</TableCell>
                      <TableCell align="right">Price</TableCell>
                      <TableCell align="right">Quantity</TableCell>
                      <TableCell align="right">Subtotal</TableCell>
                      <TableCell align="center">Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {cart.map((item) => (
                      <TableRow key={item.product_id}>
                        <TableCell>{item.name}</TableCell>
                        <TableCell>{item.sku}</TableCell>
                        <TableCell align="right">KES {item.unit_price}</TableCell>
                        <TableCell align="right">
                          <TextField
                            type="number"
                            value={item.quantity}
                            onChange={(e) => updateCartQuantity(item.product_id, parseInt(e.target.value) || 0)}
                            size="small"
                            sx={{ width: 80 }}
                            inputProps={{ min: 0 }}
                          />
                        </TableCell>
                        <TableCell align="right">KES {item.subtotal.toFixed(2)}</TableCell>
                        <TableCell align="center">
                          <IconButton
                            size="small"
                            onClick={() => removeFromCart(item.product_id)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                    {cart.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={6} align="center">
                          Cart is empty
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Payment Method */}
              <TextField
                select
                label="Payment Method"
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                fullWidth
                sx={{ mb: 2 }}
              >
                <MenuItem value="cash">Cash</MenuItem>
                <MenuItem value="mpesa">M-Pesa</MenuItem>
                <MenuItem value="card">Card</MenuItem>
                <MenuItem value="bank_transfer">Bank Transfer</MenuItem>
              </TextField>

              {/* Total */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="h6">Total:</Typography>
                <Typography variant="h6" color="primary">
                  KES {calculateTotal().toFixed(2)}
                </Typography>
              </Box>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button
              onClick={handleCheckout}
              variant="contained"
              disabled={cart.length === 0 || loading}
            >
              {loading ? 'Processing...' : 'Complete Sale'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
};

export default SalesPage;
