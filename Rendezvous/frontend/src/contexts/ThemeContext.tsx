import React, { createContext, useState, useMemo, useContext } from 'react';
import { ThemeProvider as MuiThemeProvider, CssBaseline } from '@mui/material';
import darkTheme from '../themes/darkTheme';
import tealTheme from '../themes/tealTheme';

const ThemeContext = createContext({
  toggleTheme: () => {},
  mode: 'dark',
});

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }) => {
  const [mode, setMode] = useState('dark');

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'dark' ? 'teal' : 'dark'));
  };

  const theme = useMemo(() => (mode === 'dark' ? darkTheme : tealTheme), [mode]);

  return (
    <ThemeContext.Provider value={{ toggleTheme, mode }}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};
