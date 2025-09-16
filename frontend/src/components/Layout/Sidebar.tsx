import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  Divider,
  Collapse,
  IconButton,
} from '@mui/material';
import {
  Dashboard,
  Description,
  Assignment,
  Security,
  Integration,
  Settings,
  ExpandLess,
  ExpandMore,
  ChevronLeft,
  ChevronRight,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

interface SidebarProps {
  open: boolean;
  onToggle: () => void;
}

interface MenuItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path?: string;
  children?: MenuItem[];
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: <Dashboard />,
    path: '/dashboard',
  },
  {
    id: 'requirements',
    label: 'Requirements',
    icon: <Description />,
    path: '/requirements',
  },
  {
    id: 'test-cases',
    label: 'Test Cases',
    icon: <Assignment />,
    path: '/test-cases',
  },
  {
    id: 'compliance',
    label: 'Compliance',
    icon: <Security />,
    path: '/compliance',
  },
  {
    id: 'alm-integration',
    label: 'ALM Integration',
    icon: <Integration />,
    path: '/alm-integration',
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: <Settings />,
    path: '/settings',
  },
];

const Sidebar: React.FC<SidebarProps> = ({ open, onToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [expandedItems, setExpandedItems] = React.useState<string[]>([]);

  const handleItemClick = (item: MenuItem) => {
    if (item.children) {
      const newExpanded = expandedItems.includes(item.id)
        ? expandedItems.filter(id => id !== item.id)
        : [...expandedItems, item.id];
      setExpandedItems(newExpanded);
    } else if (item.path) {
      navigate(item.path);
    }
  };

  const isSelected = (path: string) => {
    return location.pathname === path;
  };

  const renderMenuItem = (item: MenuItem, level = 0) => (
    <React.Fragment key={item.id}>
      <ListItem
        button
        onClick={() => handleItemClick(item)}
        selected={item.path ? isSelected(item.path) : false}
        sx={{
          pl: level * 2 + 2,
          '&.Mui-selected': {
            backgroundColor: 'primary.main',
            color: 'primary.contrastText',
            '&:hover': {
              backgroundColor: 'primary.dark',
            },
            '& .MuiListItemIcon-root': {
              color: 'primary.contrastText',
            },
          },
        }}
      >
        <ListItemIcon
          sx={{
            minWidth: open ? 56 : 'auto',
            justifyContent: 'center',
          }}
        >
          {item.icon}
        </ListItemIcon>
        {open && (
          <>
            <ListItemText primary={item.label} />
            {item.children && (
              expandedItems.includes(item.id) ? <ExpandLess /> : <ExpandMore />
            )}
          </>
        )}
      </ListItem>
      {item.children && (
        <Collapse in={expandedItems.includes(item.id) && open} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {item.children.map(child => renderMenuItem(child, level + 1))}
          </List>
        </Collapse>
      )}
    </React.Fragment>
  );

  return (
    <Drawer
      variant="permanent"
      open={open}
      sx={{
        width: open ? 240 : 60,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: open ? 240 : 60,
          boxSizing: 'border-box',
          overflowX: 'hidden',
          transition: 'width 0.3s',
          backgroundColor: '#1e1e1e',
          color: 'white',
          marginTop: '64px', // Account for navbar height
        },
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          padding: '0 8px',
          minHeight: '48px',
        }}
      >
        <IconButton onClick={onToggle} sx={{ color: 'white' }}>
          {open ? <ChevronLeft /> : <ChevronRight />}
        </IconButton>
      </Box>
      <Divider sx={{ backgroundColor: 'rgba(255, 255, 255, 0.12)' }} />
      <List>
        {menuItems.map(item => renderMenuItem(item))}
      </List>
    </Drawer>
  );
};

export default Sidebar;