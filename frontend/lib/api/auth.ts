import { User, LoginRequest, LoginResponse, RegisterRequest } from '@/types/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function getHeaders(): Promise<HeadersInit> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  const result = await res.json();
  if (result.access_token) localStorage.setItem('auth_token', result.access_token);
  return result;
}

export async function register(data: RegisterRequest) {
  const res = await fetch(`${API_URL}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json();
}

export async function getCurrentUser(): Promise<User> {
  const res = await fetch(`${API_URL}/api/auth/me`, { headers: await getHeaders() });
  if (!res.ok) throw new Error('Not authenticated');
  return res.json();
}

export function logout(): void {
  localStorage.removeItem('auth_token');
}
