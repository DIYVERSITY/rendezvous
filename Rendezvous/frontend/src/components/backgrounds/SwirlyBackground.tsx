import { Box } from '@mui/material';

const SwirlyBackground = () => {
  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: -1,
        backgroundImage: 
          'radial-gradient(at 0% 0%, #008080 0%, transparent 50%), radial-gradient(at 95% 95%, #6495ED 0%, transparent 50%), radial-gradient(at 20% 70%, #4a0072 0%, transparent 40%)',
        backgroundSize: '200% 200%',
        animation: 'gradient 20s ease infinite',
      }}
    />
  );
};

export default SwirlyBackground;
