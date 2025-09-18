import { createTheme } from '@mui/material/styles';

const modernTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#9c27b0', // A purple accent
    },
    secondary: {
      main: '#00bcd4', // A cyan accent
    },
    background: {
      default: '#1a1a1a',
      paper: '#2a2a2a',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b3b3b3',
    },
  },
  typography: {
    fontFamily: 'var(--font-lora)',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 700,
    },
    body1: {
      fontSize: '1rem',
    },
    mono: {
      fontFamily: '"DM Mono", monospace',
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1a1a1a',
          boxShadow: 'none',
          borderBottom: '1px solid #3a3a3a',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1a1a1a',
          borderRight: '1px solid #3a3a3a',
        },
      },
    },
  },
});

declare module '@mui/material/styles' {
  interface TypographyVariants {
    mono: React.CSSProperties;
  }

  // allow configuration using `createTheme`
  interface TypographyVariantsOptions {
    mono?: React.CSSProperties;
  }
}

declare module '@mui/material/Typography' {
  interface TypographyPropsVariantOverrides {
    mono: true;
  }
}

export default modernTheme;