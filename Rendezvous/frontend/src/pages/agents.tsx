import { Typography, Grid, Box, Card, CardContent, Button } from '@mui/material';
import StaticBackground from '@/components/backgrounds/StaticBackground';
import { useEffect, useState } from 'react';

export default function AgentsPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [invokeResult, setInvokeResult] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/agents')
      .then((res) => res.json())
      .then(setAgents);
  }, []);

  const handleInvoke = async (name: string) => {
    setInvokeResult('Invoking...');
    const res = await fetch(`/api/agents/${name}/invoke`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: { test: 'hello' } }),
    });
    const data = await res.json();
    setInvokeResult(JSON.stringify(data));
  };

  return (
    <Box>
      <StaticBackground />
      <Typography variant="h4" gutterBottom>
        Agent Registry
      </Typography>
      <Grid container spacing={3}>
        {agents.map((agent) => (
          <Grid item xs={12} sm={6} md={4} key={agent.name}>
            <Card sx={{ height: '100%', backgroundColor: 'rgba(42, 42, 42, 0.5)' }}>
              <CardContent>
                <Typography variant="h6">{agent.name}</Typography>
                <Typography variant="body2" color="text.secondary">v{agent.version}</Typography>
                <Typography variant="body1" sx={{ my: 2 }}>{agent.capabilities?.join(', ')}</Typography>
                <Button variant="contained" size="small" onClick={() => handleInvoke(agent.name)}>
                  Test Invoke
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      {invokeResult && (
        <Box mt={4}>
          <Typography variant="subtitle1">Invoke Result:</Typography>
          <pre style={{ color: 'lime', background: '#222', padding: 12 }}>{invokeResult}</pre>
        </Box>
      )}
    </Box>
  );
}