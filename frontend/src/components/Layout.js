import React, { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Badge,
  Avatar,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Inventory as InventoryIcon,
  ShoppingCart as SalesIcon,
  Warning as AlertsIcon,
  People as SuppliersIcon,
  Assessment as AnalyticsIcon,
  TrendingUp as ForecastIcon,
  TrendingUp,
  AccountCircle,
  Logout,
  Settings,
  ManageAccounts,
  PersonOutline as CustomersIcon,
  Inventory2 as BatchesIcon,
  Description as ReportsIcon,
  AdminPanelSettings,
  History as ActivityIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const drawerWidth = 240;

const Layout = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, hasRole } = useAuth();

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard', roles: ['viewer', 'manager', 'admin'] },
    { text: 'Inventory', icon: <InventoryIcon />, path: '/inventory', roles: ['viewer', 'manager', 'admin'] },
    { text: 'Batches', icon: <BatchesIcon />, path: '/batches', roles: ['manager', 'admin'] },
    { text: 'Forecast', icon: <ForecastIcon />, path: '/forecast', roles: ['manager', 'admin'] },
    { text: 'Products', icon: <InventoryIcon />, path: '/products', roles: ['manager', 'admin'] },
    { text: 'Sales', icon: <SalesIcon />, path: '/sales', roles: ['viewer', 'manager', 'admin'] },
    { text: 'Customers', icon: <CustomersIcon />, path: '/customers', roles: ['viewer', 'manager', 'admin'] },
    { text: 'Alerts', icon: <AlertsIcon />, path: '/alerts', roles: ['manager', 'admin'] },
    { text: 'Suppliers', icon: <SuppliersIcon />, path: '/suppliers', roles: ['viewer', 'manager', 'admin'] },
    { text: 'Competitors', icon: <TrendingUp />, path: '/competitors', roles: ['viewer', 'manager', 'admin'] },
    { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics', roles: ['viewer', 'manager', 'admin'] },
    { text: 'Reports', icon: <ReportsIcon />, path: '/reports', roles: ['viewer', 'manager', 'admin'] },
    { text: 'Activity', icon: <ActivityIcon />, path: '/activity', roles: ['manager', 'admin'] },
    { text: 'Organization', icon: <Settings />, path: '/organization', roles: ['manager', 'admin'] },
    { text: 'Admin Portal', icon: <AdminPanelSettings />, path: '/admin', roles: ['admin', 'manager'] },
    { text: 'Manage Competitors', icon: <TrendingUp />, path: '/admin/competitors', roles: ['admin'] },
    { text: 'Users', icon: <ManageAccounts />, path: '/users', roles: ['admin'] },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleMenuClose();
    navigate('/login');
  };

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Inventory Pro
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems
          .filter(item => item.roles.includes(user?.role))
          .map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => navigate(item.path)}
              >
                <ListItemIcon>
                  {item.text === 'Alerts' ? (
                    <Badge badgeContent={0} color="error">
                      {item.icon}
                    </Badge>
                  ) : (
                    item.icon
                  )}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {menuItems.find(item => item.path === location.pathname)?.text || 'Dashboard'}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {user?.organization_name || 'Default Organization'}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                {user?.username} • {user?.role}
              </Typography>
            </Box>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenuClick}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                {user?.username?.charAt(0).toUpperCase()}
              </Avatar>
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
            >
              <MenuItem onClick={handleMenuClose}>
                <ListItemIcon>
                  <AccountCircle fontSize="small" />
                </ListItemIcon>
                Profile
              </MenuItem>
              <MenuItem onClick={handleMenuClose}>
                <ListItemIcon>
                  <Settings fontSize="small" />
                </ListItemIcon>
                Settings
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout}>
                <ListItemIcon>
                  <Logout fontSize="small" />
                </ListItemIcon>
                Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default Layout;