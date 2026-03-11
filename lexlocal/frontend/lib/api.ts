const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Bylaw {
  id: string;
  municipality: string;
  category: string;
  title: string;
  text: string;
  constraints: Record<string, unknown>;
  tags: string[];
}

export interface QueryResponse {
  answer: string;
  matched_bylaws: Bylaw[];
  municipality_detected: string | null;
}

export interface GAGeneration {
  generation: number;
  best_fitness: number;
  avg_fitness: number;
  best_chromosome: number[];
  population_sample: number[][];
  violations: number;
  suggestion: Record<string, number>;
  done?: boolean;
  error?: string;
}

export async function queryBylaws(
  query: string,
  municipality?: string
): Promise<QueryResponse> {
  const res = await fetch(`${API}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, municipality: municipality || null }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export async function fetchBylaws(
  municipality?: string,
  category?: string
): Promise<{ bylaws: Bylaw[]; total: number }> {
  const params = new URLSearchParams();
  if (municipality) params.set("municipality", municipality);
  if (category) params.set("category", category);
  const res = await fetch(`${API}/api/bylaws?${params}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export async function fetchMunicipalities(): Promise<string[]> {
  const res = await fetch(`${API}/api/municipalities`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  const data = await res.json();
  return data.municipalities;
}

export function createGASocket(
  sessionId: string,
  payload: object,
  onMessage: (data: GAGeneration) => void,
  onDone: () => void,
  onError: (e: string) => void
): WebSocket {
  const wsBase = API.replace("http://", "ws://").replace("https://", "wss://");
  const ws = new WebSocket(`${wsBase}/ws/ga/${sessionId}`);
  ws.onopen = () => ws.send(JSON.stringify(payload));
  ws.onmessage = (e) => {
    const data: GAGeneration = JSON.parse(e.data);
    if (data.done) { onDone(); ws.close(); return; }
    if (data.error) { onError(data.error); ws.close(); return; }
    onMessage(data);
  };
  ws.onerror = () => onError("WebSocket connection failed");
  return ws;
}
