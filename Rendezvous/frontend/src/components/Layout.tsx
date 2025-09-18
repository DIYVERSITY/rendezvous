import React from 'react';
import { Box, Drawer, List, ListItem, ListItemIcon, ListItemText, Toolbar, Typography, CssBaseline, AppBar } from '@mui/material';
import { Home, Memory, Hub, Settings } from '@mui/icons-material';
import Link from 'next/link';

const drawerWidth = 240;

const navItems = [
  { text: 'Dashboard', icon: <Home />, href: '/' },
  { text: 'Workflows', icon: <Hub />, href: '/workflows' },
  { text: 'Agents', icon: <Memory />, href: '/agents' },
  { text: 'Settings', icon: <Settings />, href: '/settings' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ fontFamily: 'var(--font-merriweather)', fontWeight: 900 }}>
            RendEZvouS
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {navItems.map((item) => (
              <Link href={item.href} passHref key={item.text} legacyBehavior>
                <ListItem button component="a">
                  <ListItemIcon sx={{ color: 'white' }}>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItem>
              </Link>
            ))}
          </List>
        </Box>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3, backgroundColor: 'transparent' }}>
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
}
