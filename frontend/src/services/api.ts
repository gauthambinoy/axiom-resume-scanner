import axios from 'axios';
import type {
  ScanResponse,
  QuickScanResponse,
  CompareResponse,
  HealthResponse,
  StatsResponse,
  KeywordExtractionResponse,
  BannedPhrasesResponse,
  HumanizeResponse,
  BulkScanResponse,
  ContentMode,
  HumanizeTone,
} from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  config.headers['X-Request-ID'] = crypto.randomUUID();
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      error.message = `Rate limit exceeded. Try again in ${retryAfter || 60} seconds.`;
    } else if (error.response?.status >= 500) {
      error.message = 'Server error. Please try again later.';
    } else if (!error.response) {
      error.message = 'Network error. Check your connection.';
    }
    return Promise.reject(error);
  }
);

export async function scanResume(resumeText: string, jdText: string, mode: ContentMode = 'resume'): Promise<ScanResponse> {
  const { data } = await api.post<ScanResponse>('/scan', {
    resume_text: resumeText,
    jd_text: jdText,
    mode,
  });
  return data;
}

export async function scanFile(file: File, jdText: string, mode: ContentMode = 'resume'): Promise<ScanResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('jd_text', jdText);
  formData.append('mode', mode);
  const { data } = await api.post<ScanResponse>('/scan/file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function quickScan(resumeText: string, jdText: string = '', mode: ContentMode = 'resume'): Promise<QuickScanResponse> {
  const { data } = await api.post<QuickScanResponse>('/scan/quick', {
    resume_text: resumeText,
    jd_text: jdText,
    mode,
  });
  return data;
}

export async function compareScan(
  resumeBefore: string,
  resumeAfter: string,
  jdText: string
): Promise<CompareResponse> {
  const { data } = await api.post<CompareResponse>('/compare', {
    resume_before: resumeBefore,
    resume_after: resumeAfter,
    jd_text: jdText,
  });
  return data;
}

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>('/health');
  return data;
}

export async function getStats(): Promise<StatsResponse> {
  const { data } = await api.get<StatsResponse>('/stats');
  return data;
}

export async function getBannedPhrases(): Promise<BannedPhrasesResponse> {
  const { data } = await api.get<BannedPhrasesResponse>('/banned-phrases');
  return data;
}

export async function extractKeywords(jdText: string): Promise<KeywordExtractionResponse> {
  const { data } = await api.get<KeywordExtractionResponse>('/keywords/extract', {
    params: { jd_text: jdText },
  });
  return data;
}

export async function humanizeResume(
  resumeText: string,
  jdText: string,
  tone: HumanizeTone = 'professional',
  mode: ContentMode = 'resume'
): Promise<HumanizeResponse> {
  const { data } = await api.post<HumanizeResponse>('/humanize', {
    resume_text: resumeText,
    jd_text: jdText,
    tone,
    mode,
  }, { timeout: 120000 });
  return data;
}

export async function exportPDF(resumeText: string, jdText: string, mode: string): Promise<Blob> {
  const response = await api.post('/export/pdf', {
    resume_text: resumeText,
    jd_text: jdText,
    mode,
  }, { responseType: 'blob', timeout: 60000 });
  return response.data;
}

export async function scanBulk(files: File[], jdText: string, mode: string): Promise<BulkScanResponse> {
  const formData = new FormData();
  files.forEach(f => formData.append('files', f));
  formData.append('jd_text', jdText);
  formData.append('mode', mode);
  const { data } = await api.post<BulkScanResponse>('/scan/bulk', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000,
  });
  return data;
}

export default api;
