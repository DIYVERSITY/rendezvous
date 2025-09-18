import { Box } from '@mui/material';
import { useState, useRef, useEffect } from 'react';
import LoadingSphere from '@/components/LoadingSphere';
import ChatComponent from '@/components/ChatComponent';
import { gsap } from 'gsap';
import SwirlyBackground from '@/components/backgrounds/SwirlyBackground';

export default function HomePage() {
  const [showChat, setShowChat] = useState(false);
  const chatRef = useRef(null);

  const handleAnimationComplete = () => {
    setShowChat(true);
  };

  useEffect(() => {
    if (showChat) {
      gsap.to(chatRef.current, { 
        opacity: 1, 
        duration: 1, 
        ease: 'power3.out' 
      });
    }
  }, [showChat]);

  return (
    <Box sx={{ height: '80vh', width: '100%', position: 'relative' }}>
      <SwirlyBackground />
      <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, opacity: showChat ? 0 : 1, transition: 'opacity 1s ease-in-out' }}>
        <LoadingSphere onAnimationComplete={handleAnimationComplete} />
      </Box>
      {showChat && (
        <Box ref={chatRef} sx={{ opacity: 0 }}>
          <ChatComponent />
        </Box>
      )}
    </Box>
  );
}