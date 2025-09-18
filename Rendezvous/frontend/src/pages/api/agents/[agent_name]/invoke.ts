import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { agent_name } = req.query;
  const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
  if (req.method === 'POST') {
    const r = await fetch(`${backendUrl}/agents/${agent_name}/invoke`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    });
    const data = await r.json();
    res.status(r.status).json(data);
  } else {
    res.status(405).end();
  }
}