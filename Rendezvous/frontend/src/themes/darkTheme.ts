import { createTheme } from '@mui/material/styles';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#000000',
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0B0B0',
    },
  },
  typography: {
    fontFamily: 'serif',
    h1: {
      fontFamily: 'serif',
    },
    h2: {
      fontFamily: 'serif',
    },
    h3: {
      fontFamily: 'serif',
    },
    h4: {
      fontFamily: 'serif',
    },
    h5: {
      fontFamily: 'serif',
    },
    h6: {
      fontFamily: 'serif',
    },
    body1: {
        fontFamily: 'serif',
      },
  },
});

export default darkTheme;
