import type { FactoryBrief, FactoryResult } from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export const api = {
  get: async (endpoint: string) => {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  post: async (endpoint: string, data: any) => {
    // Check if it's FormData (for file uploads)
    const isFormData = data instanceof FormData;
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: isFormData ? {} : { 'Content-Type': 'application/json' },
      body: isFormData ? data : JSON.stringify(data),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  put: async (endpoint: string, data: any) => {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  delete: async (endpoint: string) => {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  generateFactoryPack: async (brief: FactoryBrief): Promise<FactoryResult> => {
    const res = await fetch(`${BASE_URL}/factory/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(brief),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  getFactoryTrace: async () => {
    const res = await fetch(`${BASE_URL}/factory/trace`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  getLastFactoryPack: async () => {
    const res = await fetch(`${BASE_URL}/factory/last-pack`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  getFactorySamples: async () => {
    const res = await fetch(`${BASE_URL}/factory/samples`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  runOneInputChangeDemo: async (brief?: FactoryBrief) => {
    const res = await fetch(`${BASE_URL}/factory/demo-one-input-change`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: brief ? JSON.stringify(brief) : JSON.stringify({}),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  scheduleFactoryHandoff: async (payload: {
    variant_id: string;
    platform: 'tiktok' | 'reels' | 'shorts';
    scheduled_at: string;
    caption?: string;
  }) => {
    const res = await fetch(`${BASE_URL}/factory/schedule-handoff`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }
};
