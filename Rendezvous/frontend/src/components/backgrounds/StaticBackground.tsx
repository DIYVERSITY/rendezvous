import { Box } from '@mui/material';

const StaticBackground = () => {
  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: -1,
        backgroundImage: 'radial-gradient(circle at top center, #6495ED, #008080, #4a0072, #000000)',
      }}
    />
  );
};

export default StaticBackground;
