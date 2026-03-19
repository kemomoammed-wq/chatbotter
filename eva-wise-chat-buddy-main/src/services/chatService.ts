// Chat Service for Backend API Integration
// يدعم FastAPI أو Flask، مع تفضيل FastAPI إن تم ضبط متغير VITE_FASTAPI_URL
const API_BASE_URL =
  import.meta.env.VITE_FASTAPI_URL ||
  import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? '' : 'http://localhost:8000');

export interface ChatRequest {
  message: string;
  user_id?: string;
  language?: 'ar' | 'en';
  conversation_mode?: 'smart' | 'eva-only' | 'ai-only';
}

export interface YoutubeVideo {
  title: string;
  description: string;
  thumbnail_url: string;
  video_url: string;
  channel_title?: string;
  published_at?: string;
}

export interface WebResult {
  title?: string;
  url?: string;
  snippet?: string;
  description?: string;
  content?: string;
  source?: string;
}

export interface ChatResponse {
  success: boolean;
  response: string;
  detected_lang?: string;
  intent?: string;
  sentiment?: string;
  source?: string;
  web_results?: WebResult[];
  training_saved?: boolean;
  youtube_video?: YoutubeVideo;
  error?: string;
}

export interface Link {
  id: number;
  url: string;
  title?: string;
  description?: string;
  content?: string;
  source?: string;
  timestamp?: string;
}

export interface LinksResponse {
  success: boolean;
  count: number;
  links: Link[];
  error?: string;
}

export interface SearchResponse {
  success: boolean;
  count: number;
  results: Link[];
  error?: string;
}

class ChatService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: request.message,
          user_id: request.user_id || 'anonymous',
          language: request.language,
          conversation_mode: request.conversation_mode || 'smart',
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      return {
        success: false,
        response: error instanceof Error ? error.message : 'حدث خطأ في الاتصال بالخادم',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async getLinks(source?: string, limit: number = 50): Promise<LinksResponse> {
    try {
      const params = new URLSearchParams();
      if (source) params.append('source', source);
      params.append('limit', limit.toString());

      const response = await fetch(`${this.baseUrl}/api/links?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: LinksResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting links:', error);
      return {
        success: false,
        count: 0,
        links: [],
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async addLink(url: string, priority: number = 5, forceRefresh: boolean = false): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/links`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url,
          priority,
          force_refresh: forceRefresh,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error adding link:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async searchLinks(query: string, limit: number = 10): Promise<SearchResponse> {
    try {
      const params = new URLSearchParams();
      params.append('query', query);
      params.append('limit', limit.toString());

      const response = await fetch(`${this.baseUrl}/api/links/search?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: SearchResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Error searching links:', error);
      return {
        success: false,
        count: 0,
        results: [],
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async healthCheck(): Promise<{ status: string; chatbot_loaded: boolean }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking health:', error);
      return {
        status: 'unhealthy',
        chatbot_loaded: false,
      };
    }
  }

  // ==================== Streaming Chat ====================
  
  async sendMessageStream(
    request: ChatRequest,
    onChunk: (chunk: string) => void,
    onDone: () => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: request.message,
          user_id: request.user_id || 'anonymous',
          language: request.language,
          conversation_mode: request.conversation_mode || 'smart',
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.done) {
                onDone();
              } else if (data.chunk) {
                onChunk(data.chunk);
              } else if (data.error) {
                onError(data.error);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error in streaming:', error);
      onError(error instanceof Error ? error.message : 'Unknown error');
    }
  }

  // ==================== Multimedia Upload ====================

  async uploadImage(file: File): Promise<{ success: boolean; data?: any; error?: string }> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${this.baseUrl}/api/upload/image`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error uploading image:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async uploadAudio(file: File): Promise<{ success: boolean; data?: any; error?: string }> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${this.baseUrl}/api/upload/audio`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error uploading audio:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // ==================== Voice Processing ====================

  async speechToText(audioBlob: Blob, language: 'ar' | 'en' = 'en'): Promise<{ success: boolean; text?: string; error?: string }> {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');
      formData.append('language', language);

      const response = await fetch(`${this.baseUrl}/api/voice/speech-to-text`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error in speech-to-text:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async textToSpeech(text: string, language: 'ar' | 'en' = 'en'): Promise<{ success: boolean; audioUrl?: string; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/voice/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          language,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      // Get audio blob
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      return {
        success: true,
        audioUrl,
      };
    } catch (error) {
      console.error('Error in text-to-speech:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // ==================== Conversation Management ====================

  async getConversations(userId: string = 'anonymous', limit: number = 20): Promise<{
    success: boolean;
    conversations?: any[];
    error?: string;
  }> {
    try {
      const params = new URLSearchParams();
      params.append('user_id', userId);
      params.append('limit', limit.toString());

      const response = await fetch(`${this.baseUrl}/api/conversations?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting conversations:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async getConversationHistory(conversationId: string, limit: number = 50): Promise<{
    success: boolean;
    history?: any[];
    error?: string;
  }> {
    try {
      const params = new URLSearchParams();
      params.append('limit', limit.toString());

      const response = await fetch(
        `${this.baseUrl}/api/conversations/${conversationId}?${params.toString()}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting conversation history:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async createConversation(userId: string = 'anonymous', title?: string): Promise<{
    success: boolean;
    conversation_id?: string;
    error?: string;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          title,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating conversation:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // ==================== Memory Management ====================

  async getMemory(userId: string = 'anonymous', key?: string): Promise<{
    success: boolean;
    memories?: any[];
    error?: string;
  }> {
    try {
      const params = new URLSearchParams();
      params.append('user_id', userId);
      if (key) params.append('key', key);

      const response = await fetch(`${this.baseUrl}/api/memory?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting memory:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // ==================== Tools ====================

  async executeTool(tool: string, params: any): Promise<{ success: boolean; [key: string]: any }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/tools/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tool,
          params,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error executing tool:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async listTools(): Promise<{ success: boolean; tools?: string[]; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/tools/list`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error listing tools:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }
}

export const chatService = new ChatService();
export default chatService;

