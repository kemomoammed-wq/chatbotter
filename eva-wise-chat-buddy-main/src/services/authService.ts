// Auth Service for Authentication
const API_BASE_URL =
  import.meta.env.VITE_FASTAPI_URL ||
  import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD ? '' : 'http://localhost:8000');

export interface User {
  id: number;
  username: string;
  email?: string;
  full_name?: string;
  language?: string;
  created_at?: string;
  last_login?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  email?: string;
  full_name?: string;
}

export interface AuthResponse {
  success: boolean;
  user?: User;
  message?: string;
  error?: string;
}

class AuthService {
  private baseUrl: string;
  private currentUser: User | null = null;

  constructor() {
    this.baseUrl = API_BASE_URL;
    // Load user from localStorage on init
    this.loadUserFromStorage();
  }

  private loadUserFromStorage() {
    try {
      const stored = localStorage.getItem('eva_user');
      if (stored) {
        this.currentUser = JSON.parse(stored);
      }
    } catch (e) {
      console.error('Error loading user from storage:', e);
    }
  }

  async login(request: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data: AuthResponse = await response.json();
      
      if (data.success && data.user) {
        this.currentUser = data.user;
        localStorage.setItem('eva_user', JSON.stringify(data.user));
        localStorage.setItem('eva_username', data.user.username);
      }
      
      return data;
    } catch (error) {
      console.error('Error logging in:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'حدث خطأ في تسجيل الدخول',
      };
    }
  }

  async register(request: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data: AuthResponse = await response.json();
      
      if (data.success && data.user) {
        this.currentUser = data.user;
        localStorage.setItem('eva_user', JSON.stringify(data.user));
        localStorage.setItem('eva_username', data.user.username);
      }
      
      return data;
    } catch (error) {
      console.error('Error registering:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'حدث خطأ في التسجيل',
      };
    }
  }

  logout() {
    this.currentUser = null;
    localStorage.removeItem('eva_user');
    localStorage.removeItem('eva_username');
  }

  getCurrentUser(): User | null {
    return this.currentUser;
  }

  isAuthenticated(): boolean {
    return this.currentUser !== null;
  }

  getUsername(): string | null {
    return this.currentUser?.username || localStorage.getItem('eva_username');
  }

  getUserFullName(): string | null {
    return this.currentUser?.full_name || this.currentUser?.username || null;
  }
}

export const authService = new AuthService();
export default authService;

