import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Tabs, Tab, TextField, Button,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Chip, IconButton, MenuItem, Select, Alert, CircularProgress, Grid,
  Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import { Save, Delete, Send, Block, Business } from '@mui/icons-material';
import Layout from '../components/Layout';
import InviteUserDialog from '../components/InviteUserDialog';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import handleApiError from '../utils/errorHandler';

const API_URL = 'http://localhost:5000/api';

const OrganizationPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saveLoading, setSaveLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Settings state
  const [orgSettings, setOrgSettings] = useState(null);
  const [orgName, setOrgName] = useState('');

  // Members state
  const [members, setMembers] = useState([]);
  const [confirmDialog, setConfirmDialog] = useState({ open: false, action: null, member: null });

  // Invitations state
  const [invitations, setInvitations] = useState([]);
  const [openInviteDialog, setOpenInviteDialog] = useState(false);

  useEffect(() => {
    // Check if user has access
    if (user && user.role === 'viewer') {
      setError('Access denied');
      setTimeout(() => navigate('/dashboard'), 2000);
      return;
    }
    fetchData();
  }, [tabValue, user, navigate]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(''), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const fetchData = async () => {
    try {
      setLoading(true);
      if (tabValue === 0) {
        await fetchSettings();
      } else if (tabValue === 1) {
        await fetchMembers();
      } else if (tabValue === 2) {
        await fetchInvitations();
      }
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const fetchSettings = async () => {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(`${API_URL}/organizations/settings`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setOrgSettings(response.data);
    setOrgName(response.data.name);
  };

  const fetchMembers = async () => {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(`${API_URL}/organizations/members`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setMembers(response.data);
  };

  const fetchInvitations = async () => {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(`${API_URL}/organizations/invitations`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    setInvitations(response.data);
  };

  const handleSaveSettings = async () => {
    try {
      setSaveLoading(true);
      setError('');
      const token = localStorage.getItem('access_token');
      await axios.put(`${API_URL}/organizations/settings`, { name: orgName }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuccess('Organization settings updated successfully');
      await fetchSettings();
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setSaveLoading(false);
    }
  };

  const handleChangeRole = async (memberId, newRole) => {
    try {
      setError('');
      const token = localStorage.getItem('access_token');
      await axios.put(`${API_URL}/organizations/members/${memberId}/role`, { role: newRole }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuccess('Member role updated successfully');
      await fetchMembers();
    } catch (err) {
      setError(handleApiError(err));
    }
  };

  const handleRemoveMember = async (member) => {
    setConfirmDialog({
      open: true,
      action: 'remove',
      member,
      title: 'Remove Member',
      message: `Are you sure you want to remove ${member.username} from the organization?`
    });
  };

  const handleRevokeInvitation = async (invitation) => {
    setConfirmDialog({
      open: true,
      action: 'revoke',
      member: invitation,
      title: 'Revoke Invitation',
      message: `Are you sure you want to revoke the invitation for ${invitation.email}?`
    });
  };

  const handleConfirmAction = async () => {
    const { action, member } = confirmDialog;
    
    try {
      setError('');
      const token = localStorage.getItem('access_token');
      if (action === 'remove') {
        await axios.delete(`${API_URL}/organizations/members/${member.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSuccess('Member removed successfully');
        await fetchMembers();
      } else if (action === 'revoke') {
        await axios.delete(`${API_URL}/organizations/invitations/${member.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSuccess('Invitation revoked successfully');
        await fetchInvitations();
      }
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setConfirmDialog({ open: false, action: null, member: null });
    }
  };

  const handleResendInvitation = async (invitationId) => {
    try {
      setError('');
      const token = localStorage.getItem('access_token');
      await axios.post(`${API_URL}/organizations/invitations/${invitationId}/resend`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuccess('Invitation resent successfully');
      await fetchInvitations();
    } catch (err) {
      setError(handleApiError(err));
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'primary';
      case 'manager': return 'warning';
      default: return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'accepted': return 'success';
      case 'pending': return 'warning';
      case 'expired': return 'error';
      default: return 'default';
    }
  };

  if (user && user.role === 'viewer') {
    return null;
  }

  return (
    <Layout>
      <Box>
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Business fontSize="large" color="primary" />
            <Typography variant="h4">
              Organization: {orgSettings?.name || 'Loading...'}
            </Typography>
          </Box>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        <Card>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab label="Settings" />
            <Tab label="Members" />
            <Tab label="Invitations" />
          </Tabs>

          <CardContent>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                {/* Tab 1 - Settings */}
                {tabValue === 0 && orgSettings && (
                  <Box>
                    <Grid container spacing={3} sx={{ mb: 3 }}>
                      <Grid item xs={12} md={6}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography color="text.secondary" gutterBottom>
                              Created
                            </Typography>
                            <Typography variant="h6">
                              {new Date(orgSettings.created_at).toLocaleDateString()}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography color="text.secondary" gutterBottom>
                              Total Members
                            </Typography>
                            <Typography variant="h6">
                              {orgSettings.member_count}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>

                    <TextField
                      label="Organization Name"
                      fullWidth
                      value={orgName}
                      onChange={(e) => setOrgName(e.target.value)}
                      disabled={user?.role !== 'admin'}
                      sx={{ mb: 2 }}
                    />

                    {user?.role === 'admin' && (
                      <Button
                        variant="contained"
                        startIcon={<Save />}
                        onClick={handleSaveSettings}
                        disabled={saveLoading || orgName === orgSettings.name}
                      >
                        {saveLoading ? <CircularProgress size={24} color="inherit" /> : 'Save Changes'}
                      </Button>
                    )}
                  </Box>
                )}

                {/* Tab 2 - Members */}
                {tabValue === 1 && (
                  <Box>
                    {members.length === 0 ? (
                      <Box sx={{ textAlign: 'center', py: 4 }}>
                        <Typography variant="h6" color="text.secondary">
                          No members found.
                        </Typography>
                      </Box>
                    ) : (
                      <TableContainer component={Paper}>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Username</TableCell>
                              <TableCell>Email</TableCell>
                              <TableCell>Role</TableCell>
                              <TableCell>Joined</TableCell>
                              {user?.role === 'admin' && <TableCell align="right">Actions</TableCell>}
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {members.map((member) => (
                              <TableRow 
                                key={member.id}
                                sx={{ 
                                  backgroundColor: member.is_current_user ? 'action.hover' : 'inherit'
                                }}
                              >
                                <TableCell>{member.username}</TableCell>
                                <TableCell>{member.email}</TableCell>
                                <TableCell>
                                  <Chip label={member.role} color={getRoleColor(member.role)} size="small" />
                                </TableCell>
                                <TableCell>{new Date(member.created_at).toLocaleDateString()}</TableCell>
                                {user?.role === 'admin' && (
                                  <TableCell align="right">
                                    {!member.is_current_user && member.role !== 'admin' && (
                                      <>
                                        <Select
                                          value={member.role}
                                          onChange={(e) => handleChangeRole(member.id, e.target.value)}
                                          size="small"
                                          sx={{ mr: 1, minWidth: 100 }}
                                        >
                                          <MenuItem value="manager">Manager</MenuItem>
                                          <MenuItem value="viewer">Viewer</MenuItem>
                                        </Select>
                                        <IconButton
                                          onClick={() => handleRemoveMember(member)}
                                          color="error"
                                          size="small"
                                        >
                                          <Delete />
                                        </IconButton>
                                      </>
                                    )}
                                  </TableCell>
                                )}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </Box>
                )}

                {/* Tab 3 - Invitations */}
                {tabValue === 2 && (
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
                      <Button
                        variant="contained"
                        onClick={() => setOpenInviteDialog(true)}
                      >
                        Invite User
                      </Button>
                    </Box>

                    {invitations.length === 0 ? (
                      <Box sx={{ textAlign: 'center', py: 4 }}>
                        <Typography variant="h6" color="text.secondary">
                          No pending invitations.
                        </Typography>
                      </Box>
                    ) : (
                      <TableContainer component={Paper}>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Email</TableCell>
                              <TableCell>Role</TableCell>
                              <TableCell>Status</TableCell>
                              <TableCell>Sent</TableCell>
                              <TableCell>Expires</TableCell>
                              <TableCell align="right">Actions</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {invitations.map((invitation) => (
                              <TableRow key={invitation.id}>
                                <TableCell>{invitation.email}</TableCell>
                                <TableCell>
                                  <Chip label={invitation.role} color={getRoleColor(invitation.role)} size="small" />
                                </TableCell>
                                <TableCell>
                                  <Chip label={invitation.status} color={getStatusColor(invitation.status)} size="small" />
                                </TableCell>
                                <TableCell>{new Date(invitation.created_at).toLocaleDateString()}</TableCell>
                                <TableCell>{new Date(invitation.expires_at).toLocaleDateString()}</TableCell>
                                <TableCell align="right">
                                  {(invitation.status === 'pending' || invitation.status === 'expired') && (
                                    <IconButton
                                      onClick={() => handleResendInvitation(invitation.id)}
                                      color="primary"
                                      size="small"
                                      title="Resend"
                                    >
                                      <Send />
                                    </IconButton>
                                  )}
                                  {invitation.status === 'pending' && (
                                    <IconButton
                                      onClick={() => handleRevokeInvitation(invitation)}
                                      color="error"
                                      size="small"
                                      title="Revoke"
                                    >
                                      <Block />
                                    </IconButton>
                                  )}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </Box>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {/* Confirmation Dialog */}
        <Dialog open={confirmDialog.open} onClose={() => setConfirmDialog({ open: false, action: null, member: null })}>
          <DialogTitle>{confirmDialog.title}</DialogTitle>
          <DialogContent>
            <Typography>{confirmDialog.message}</Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setConfirmDialog({ open: false, action: null, member: null })}>
              Cancel
            </Button>
            <Button onClick={handleConfirmAction} color="error" variant="contained">
              Confirm
            </Button>
          </DialogActions>
        </Dialog>

        {/* Invite User Dialog */}
        <InviteUserDialog
          open={openInviteDialog}
          onClose={() => setOpenInviteDialog(false)}
          onSuccess={(msg) => {
            setSuccess(msg);
            fetchInvitations();
          }}
        />
      </Box>
    </Layout>
  );
};

export default OrganizationPage;
