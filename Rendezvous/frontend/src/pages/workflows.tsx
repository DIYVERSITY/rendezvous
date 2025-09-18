import { Typography, Box } from '@mui/material';
import React, { useCallback } from 'react';
import ReactFlow, {
  useNodesState,
  useEdgesState,
  addEdge,
  MiniMap,
  Controls,
  Background,
  Node,
  Edge
} from 'reactflow';
import 'reactflow/dist/style.css';
import StaticBackground from '@/components/backgrounds/StaticBackground';

const initialNodes: Node[] = [
  { id: '1', position: { x: 0, y: 0 }, data: { label: 'Start' }, type: 'input' },
  { id: '2', position: { x: 0, y: 100 }, data: { label: 'Search Web' } },
  { id: '3', position: { x: 200, y: 200 }, data: { label: 'Summarize Results' } },
  { id: '4', position: { x: 0, y: 300 }, data: { label: 'Output' }, type: 'output' },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e2-3', source: '2', target: '3' },
  { id: 'e3-4', source: '3', target: '4' },
];

export default function WorkflowsPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  return (
    <Box sx={{ height: '80vh' }}>
      <StaticBackground />
      <Typography variant="h4" gutterBottom>
        Workflow Editor
      </Typography>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background />
      </ReactFlow>
    </Box>
  );
}