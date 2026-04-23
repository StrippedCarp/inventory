import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Divider
} from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const ActivityPage = () => {
  const [activities, setActivities] = useState([]);
  const [filteredActivities, setFilteredActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [resourceTypeFilter, setResourceTypeFilter] = useState('All');
  const [userFilter, setUserFilter] = useState('All');
  const [users, setUsers] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const role = localStorage.getItem('role');
    if (role === 'viewer') {
      navigate('/dashboard');
      return;
    }
    
    fetchActivities();
  }, [navigate]);

  const fetchActivities = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:5000/api/activity?limit=50', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setActivities(response.data);
      setFilteredActivities(response.data);
      
      // Extract unique users
      const uniqueUsers = [...new Set(response.data.map(a => a.username))];
      setUsers(uniqueUsers);
    } catch (error) {
      console.error('Error fetching activities:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let filtered = activities;
    
    if (resourceTypeFilter !== 'All') {
      filtered = filtered.filter(a => a.resource_type === resourceTypeFilter);
    }
    
    if (userFilter !== 'All') {
      filtered = filtered.filter(a => a.username === userFilter);
    }
    
    setFilteredActivities(filtered);
  }, [resourceTypeFilter, userFilter, activities]);

  const getRelativeTime = (timestamp) => {
    const now = new Date();
    const date = new Date(timestamp);
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString();
  };

  const getDateGroup = (timestamp) => {
    const now = new Date();
    const date = new Date(timestamp);
    const diffDays = Math.floor((now - date) / 86400000);

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
  };

  const groupActivitiesByDate = () => {
    const groups = {};
    filteredActivities.forEach(activity => {
      const group = getDateGroup(activity.created_at);
      if (!groups[group]) groups[group] = [];
      groups[group].push(activity);
    });
    return groups;
  };

  const getAvatarColor = (username) => {
    const colors = ['#1976d2', '#388e3c', '#d32f2f', '#f57c00', '#7b1fa2', '#0097a7'];
    const index = username.charCodeAt(0) % colors.length;
    return colors[index];
  };

  const getActionColor = (action) => {
    if (action === 'created') return '#388e3c';
    if (action === 'updated') return '#1976d2';
    if (action === 'deleted') return '#d32f2f';
    return '#757575';
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  const groupedActivities = groupActivitiesByDate();

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Activity Feed
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Resource Type</InputLabel>
              <Select
                value={resourceTypeFilter}
                label="Resource Type"
                onChange={(e) => setResourceTypeFilter(e.target.value)}
              >
                <MenuItem value="All">All</MenuItem>
                <MenuItem value="product">Products</MenuItem>
                <MenuItem value="customer">Customers</MenuItem>
                <MenuItem value="supplier">Suppliers</MenuItem>
                <MenuItem value="inventory">Inventory</MenuItem>
                <MenuItem value="user">Users</MenuItem>
                <MenuItem value="member">Members</MenuItem>
                <MenuItem value="organization settings">Organization</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>User</InputLabel>
              <Select
                value={userFilter}
                label="User"
                onChange={(e) => setUserFilter(e.target.value)}
              >
                <MenuItem value="All">All</MenuItem>
                {users.map(user => (
                  <MenuItem key={user} value={user}>{user}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 2 }}>
        {filteredActivities.length === 0 ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
            <Typography color="textSecondary">No activity found</Typography>
          </Box>
        ) : (
          Object.entries(groupedActivities).map(([dateGroup, items]) => (
            <Box key={dateGroup} sx={{ mb: 3 }}>
              <Typography variant="subtitle2" color="textSecondary" sx={{ px: 2, py: 1, fontWeight: 600 }}>
                {dateGroup}
              </Typography>
              <List sx={{ py: 0 }}>
                {items.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem alignItems="flex-start" sx={{ py: 2 }}>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: getAvatarColor(activity.username), width: 40, height: 40 }}>
                          {activity.username.charAt(0).toUpperCase()}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box>
                            <Typography variant="body1" component="span">
                              {activity.description}
                            </Typography>
                            <Typography
                              variant="caption"
                              component="span"
                              sx={{
                                ml: 1,
                                px: 1,
                                py: 0.5,
                                borderRadius: 1,
                                bgcolor: getActionColor(activity.action) + '20',
                                color: getActionColor(activity.action)
                              }}
                            >
                              {activity.action}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Box sx={{ mt: 0.5 }}>
                            <Typography variant="caption" color="textSecondary">
                              {getRelativeTime(activity.created_at)} • {activity.resource_type}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < items.length - 1 && <Divider variant="inset" component="li" />}
                  </React.Fragment>
                ))}
              </List>
            </Box>
          ))
        )}
      </Paper>
    </Container>
  );
};

export default ActivityPage;
