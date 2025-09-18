import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Paper,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  InputBase,
} from '@mui/material';
import {
  Add,
  AutoGraphRounded,
  TravelExplore,
  Article,
  Search,
} from '@mui/icons-material';

const menuItems = [
  { text: 'Deep Research', icon: <TravelExplore sx={{ color: 'white' }} /> },
  { text: 'Create Report', icon: <Article sx={{ color: 'white' }} /> },
  { text: 'Search', icon: <Search sx={{ color: 'white' }} /> },
];

const ChatComponent = () => {
  const [actionsOpen, setActionsOpen] = useState(false);
  const [value, setValue] = useState('');

  const handleToggleActions = () => {
    setActionsOpen(!actionsOpen);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      // Handle submission logic here
      console.log('Submitting:', value);
      setValue('');
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
      }}
    >
      <Typography variant="h2" gutterBottom sx={{ color: 'white' }}>
        How may I help?
      </Typography>
      <Box sx={{ width: 600 }}>
        <Paper
          sx={{
            p: '2px 4px',
            display: 'flex',
            alignItems: 'center',
            borderRadius: '50px',
            backgroundColor: 'rgba(42, 42, 42, 0.8)',
            transition: 'all 0.3s ease-in-out',
            '&:hover': {
              backgroundColor: 'rgba(52, 52, 52, 1)',
              boxShadow: '0 0 20px rgba(0, 188, 212, 0.5)',
            },
          }}
        >
          <IconButton sx={{ p: '10px' }} aria-label="actions" onClick={handleToggleActions}>
            <Add sx={{ color: 'white', transform: actionsOpen ? 'rotate(45deg)' : 'rotate(0)', transition: 'transform 0.3s' }} />
          </IconButton>
          <InputBase
            sx={{
              ml: 1,
              flex: 1,
              color: 'white',
              fontFamily: 'var(--font-dm-mono)',
              fontSize: '1rem',
              lineHeight: '24px',
            }}
            placeholder="e.g. Build me a Nike Marketing Campaign"
            multiline
            maxRows={4}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <IconButton type="submit" sx={{ p: '10px' }} aria-label="send">
            <AutoGraphRounded sx={{ color: 'white' }} />
          </IconButton>
        </Paper>
        <Collapse in={actionsOpen}>
          <Paper sx={{ mt: 1, borderRadius: '20px', backgroundColor: 'rgba(42, 42, 42, 0.8)' }}>
            <List>
              {menuItems.map((item) => (
                <ListItem button key={item.text}>
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} sx={{ fontFamily: 'var(--font-dm-mono)' }} />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Collapse>
      </Box>
    </Box>
  );
};

export default ChatComponent;