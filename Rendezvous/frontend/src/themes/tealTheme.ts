import { createTheme } from '@mui/material/styles';

const tealTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#008080',
    },
    background: {
      default: '#E0F2F1',
      paper: '#B2DFDB',
    },
    text: {
      primary: '#004D40',
      secondary: '#00695C',
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

export default tealTheme;
