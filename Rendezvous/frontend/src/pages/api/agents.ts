import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
  if (req.method === 'GET') {
    const r = await fetch(`${backendUrl}/agents`);
    const data = await r.json();
    res.status(200).json(data);
  } else {
    res.status(405).end();
  }
}