# Activity Feed System

Complete activity logging and feed system for tracking user actions within organizations.

## Overview

The Activity Feed system logs all significant user actions and displays them in a chronological feed. It provides transparency, audit trails, and helps teams stay informed about changes in the system.

## Features

- **Automatic Activity Logging**: Logs successful operations across the system
- **Organization Isolation**: Users only see activities from their organization
- **Real-time Updates**: Auto-refreshes every 30 seconds
- **Date Grouping**: Activities grouped by Today, Yesterday, and specific dates
- **Filtering**: Filter by resource type and user
- **Relative Timestamps**: Human-readable time indicators (e.g., "2 minutes ago")
- **User Avatars**: Color-coded avatars based on username
- **Dashboard Widget**: Quick view of recent activities on dashboard
- **Full Activity Page**: Detailed view with advanced filtering

## Backend Implementation

### Database Model

**Table**: `activity_logs`

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| organization_id | Integer | Foreign key to organizations |
| user_id | Integer | Foreign key to users |
| username | String(100) | Username (stored directly) |
| action | String(50) | Action performed (created, updated, deleted, etc.) |
| resource_type | String(50) | Type of resource (product, customer, supplier, etc.) |
| resource_name | String(200) | Name of the resource |
| description | String(500) | Full readable description |
| created_at | DateTime | Timestamp (UTC) |

### Activity Logger Utility

**File**: `app/utils/activity_logger.py`

```python
def log_activity(org_id, user_id, username, action, resource_type, resource_name):
    """
    Log user activity to the database.
    Silently fails to prevent breaking main operations.
    """
```

**Usage Example**:
```python
from app.utils.activity_logger import log_activity

# After successful product creation
log_activity(org_id, user_id, user.username, 'created', 'product', product.name)
```

### Logged Actions

#### Products
- Created product
- Updated product
- Deleted product

#### Customers
- Created customer
- Updated customer

#### Suppliers
- Created supplier
- Updated supplier

#### Inventory
- Adjusted stock for inventory

#### Invitations
- Sent invitation to user
- Accepted invitation and joined organization

#### Organization Management
- Updated organization settings
- Changed role to [role] for member
- Removed member

### API Endpoints

#### GET /api/activity

Get activity logs for the organization.

**Query Parameters**:
- `limit` (optional, default: 50, max: 100): Number of activities to return

**Headers**:
- `Authorization: Bearer <access_token>`

**Response**:
```json
[
  {
    "id": 1,
    "username": "admin",
    "action": "created",
    "resource_type": "product",
    "resource_name": "Coca Cola 500ml",
    "description": "admin created product Coca Cola 500ml",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

**Access Control**:
- All authenticated users can access
- Only sees activities from their organization
- Filtered by organization_id from JWT

## Frontend Implementation

### Components

#### ActivityFeed Component

**File**: `frontend/src/components/ActivityFeed.js`

**Props**:
- `limit` (number, default: 20): Number of activities to display
- `showViewAll` (boolean, default: false): Show "View All" button
- `onViewAll` (function): Callback when "View All" is clicked

**Features**:
- Auto-refresh every 30 seconds
- Date grouping (Today, Yesterday, specific dates)
- Relative timestamps
- Color-coded avatars
- Loading state
- Empty state

**Usage**:
```jsx
<ActivityFeed 
  limit={20} 
  showViewAll={true} 
  onViewAll={() => navigate('/activity')}
/>
```

#### ActivityPage Component

**File**: `frontend/src/pages/ActivityPage.js`

**Features**:
- Full-page activity feed
- Shows last 50 activities
- Filter by resource type (All, Products, Customers, Suppliers, Inventory, Users, Members, Organization)
- Filter by user (All, or specific users)
- Client-side filtering for performance
- Detailed activity cards with action badges
- Access control (manager+ only, viewers redirected)

### Dashboard Integration

The ActivityFeed component is integrated into the Dashboard as a card showing the last 20 activities with a "View All" button that navigates to the full Activity page.

### Navigation

**Menu Item**: "Activity"
**Icon**: History icon
**Path**: `/activity`
**Access**: Manager and Admin only
**Position**: Between "Reports" and "Organization" in sidebar

## Security & Privacy

### Access Control
- Viewers cannot access the Activity page (redirected to dashboard)
- Managers and Admins can view all activities in their organization
- Complete isolation between organizations

### Data Privacy
- Only successful operations are logged
- Failed operations are not logged
- Usernames are stored directly (no joins required)
- Timestamps stored in UTC, displayed in local time

### Error Handling
- Activity logging failures do not break main operations
- Wrapped in try/except blocks
- Silent failures with database rollback
- Main operation continues even if logging fails

## Setup Instructions

### 1. Run Migration

Add the activity_logs table to your database:

```bash
python scripts/add_activity_logs_table.py
```

### 2. Verify Backend

Start the backend server:

```bash
python run_sqlite.py
```

Test the endpoint:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/activity
```

### 3. Verify Frontend

Start the frontend:

```bash
cd frontend
npm start
```

Navigate to:
- Dashboard: http://localhost:3000/dashboard (see activity widget)
- Activity Page: http://localhost:3000/activity (full page)

## Usage Examples

### Viewing Recent Activity

1. **Dashboard Widget**:
   - Go to Dashboard
   - Scroll to "Recent Activity" card
   - See last 20 activities
   - Click "View All" to see more

2. **Full Activity Page**:
   - Click "Activity" in sidebar (manager/admin only)
   - See last 50 activities
   - Use filters to narrow down results

### Filtering Activities

1. **By Resource Type**:
   - Select resource type from dropdown
   - Options: All, Products, Customers, Suppliers, Inventory, Users, Members, Organization

2. **By User**:
   - Select user from dropdown
   - Options: All, or specific team members

3. **Combined Filters**:
   - Apply both filters simultaneously
   - Filters work client-side for instant results

### Understanding Activity Descriptions

Activities follow this format:
```
[username] [action] [resource_type] [resource_name]
```

Examples:
- "admin created product Coca Cola 500ml"
- "manager updated customer John Doe"
- "admin sent invitation to user jane@example.com"
- "manager adjusted stock for inventory Pepsi 1L"

## Troubleshooting

### Activities Not Showing

1. **Check Database**:
   ```bash
   python scripts/add_activity_logs_table.py
   ```

2. **Verify Backend**:
   - Check backend logs for errors
   - Test API endpoint directly
   - Verify JWT token includes organization_id

3. **Check Frontend**:
   - Open browser console for errors
   - Verify access_token in localStorage
   - Check network tab for API calls

### Auto-Refresh Not Working

- Check browser console for errors
- Verify component is mounted
- Check interval cleanup in useEffect

### Filters Not Working

- Filters are client-side
- Check browser console for errors
- Verify activities are loaded
- Check filter state values

## Performance Considerations

### Backend
- Indexed on organization_id for fast queries
- Indexed on created_at for sorting
- Limited to 100 activities per request
- Silent failures prevent performance impact

### Frontend
- Client-side filtering for instant results
- Auto-refresh every 30 seconds (configurable)
- Lazy loading on scroll (future enhancement)
- Efficient date grouping algorithm

## Future Enhancements

### Planned Features
- [ ] Export activity logs to CSV
- [ ] Advanced search with date range
- [ ] Activity notifications
- [ ] Detailed activity view (modal)
- [ ] Undo recent actions
- [ ] Activity analytics dashboard
- [ ] Real-time updates via WebSocket
- [ ] Infinite scroll for large datasets

### Potential Improvements
- Add more granular actions (e.g., "updated price" vs "updated product")
- Include before/after values for updates
- Add activity categories (critical, normal, informational)
- Implement activity retention policies
- Add activity export for compliance

## Testing

### Backend Tests

Test activity logging:
```python
# Create a product and verify activity is logged
response = client.post('/api/products', json={...})
activities = ActivityLog.query.filter_by(organization_id=org_id).all()
assert len(activities) > 0
assert activities[0].action == 'created'
```

### Frontend Tests

Test ActivityFeed component:
```javascript
// Mock API response
// Render component
// Verify activities are displayed
// Test filters
// Test auto-refresh
```

## Maintenance

### Database Cleanup

Consider implementing retention policies:
```sql
-- Delete activities older than 90 days
DELETE FROM activity_logs WHERE created_at < NOW() - INTERVAL '90 days';
```

### Monitoring

Monitor activity log growth:
```sql
-- Count activities per organization
SELECT organization_id, COUNT(*) FROM activity_logs GROUP BY organization_id;

-- Activities per day
SELECT DATE(created_at), COUNT(*) FROM activity_logs GROUP BY DATE(created_at);
```

## Support

For issues or questions:
1. Check this documentation
2. Review backend logs
3. Check browser console
4. Verify database migration ran successfully
5. Test API endpoints directly

## Summary

The Activity Feed system provides comprehensive activity tracking with:
- ✅ Automatic logging of all major operations
- ✅ Organization-based isolation
- ✅ Real-time updates
- ✅ Advanced filtering
- ✅ User-friendly interface
- ✅ Silent failure handling
- ✅ Performance optimized
- ✅ Security conscious

Built with modern technologies for efficient team collaboration and audit compliance.
