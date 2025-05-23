import axios from 'axios';

// Backend URLs based on environment
const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://cores-ai.vercel.app/api'
  : 'http://localhost:8082';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types based on your schemas
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatRequest {
  messages: Message[];
}

export interface ChatResponse {
  messages: Message[];
}

export interface SearchResult {
  title: string;
  snippet: string;
  url: string;
  relevance_score: number;
}

export interface WebSearchResponse {
  query: string;
  results: SearchResult[];
  summary: string;
}

export interface StreamingRequest {
  messages: Message[];
  output_mode?: 'object' | 'array' | 'no-schema';
  schema_type?: 'general' | 'search' | 'notifications' | 'tasks' | 'analysis' | 'creative_software';
  context?: string;
}

export interface HealthResponse {
  status: string;
  message: string;
  version?: string;
  features?: string[];
}

// Health check functions
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const response = await api.get('/health');
    return response.status === 200 && response.data.status === 'healthy';
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
};

export const getHealthDetails = async (): Promise<HealthResponse | null> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Failed to get health details:', error);
    return null;
  }
};

// Chat functions
export const sendChatMessage = async (messages: Message[]): Promise<ChatResponse> => {
  const response = await api.post('/api/v1/chat', { messages });
  return response.data;
};

// Web search functions
export const performWebSearch = async (query: string): Promise<WebSearchResponse> => {
  const response = await api.post('/api/v1/search', { query });
  return response.data;
};

// Streaming functions
export const detectSchema = async (message: string): Promise<any> => {
  const response = await streamingApi.post('/api/v1/detect-schema', { message });
  return response.data;
};

export const streamObject = async (
  request: StreamingRequest,
  onChunk: (chunk: any) => void,
  onComplete: () => void,
  onError: (error: any) => void
): Promise<void> => {
  try {
    const response = await streamingApi.post('/api/v1/stream-object', request, {
      responseType: 'stream',
      headers: {
        'Accept': 'text/event-stream',
      },
    });

    // Handle server-sent events
    const reader = response.data.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.trim() !== '');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            onChunk(data);
            
            if (data.is_final) {
              onComplete();
              return;
            }
          } catch (e) {
            console.error('Error parsing streaming data:', e);
          }
        }
      }
    }
  } catch (error) {
    onError(error);
  }
};

// Creative software knowledge
export const getCreativeSoftwareKnowledge = async (query: string): Promise<any> => {
  const request: StreamingRequest = {
    messages: [{ role: 'user', content: query }],
    output_mode: 'object',
    schema_type: 'creative_software',
  };
  
  return new Promise((resolve, reject) => {
    let result: any = null;
    
    streamObject(
      request,
      (chunk) => {
        if (chunk.data) {
          result = chunk.data;
        }
      },
      () => resolve(result),
      (error) => reject(error)
    );
  });
};

// Server status
export const getServerStatus = async (game?: string) => {
  try {
    const response = await api.get('/api/v1/server-status', {
      params: { game }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get server status:', error);
    throw error;
  }
};

export default {
  checkBackendHealth,
  getHealthDetails,
  sendChatMessage,
  performWebSearch,
  detectSchema,
  streamObject,
  getCreativeSoftwareKnowledge,
  getServerStatus,
}; 