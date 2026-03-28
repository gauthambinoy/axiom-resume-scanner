export function validateResumeText(text: string): string | null {
  if (!text.trim()) return 'Resume text is required';
  if (text.length < 100) return 'Resume must be at least 100 characters';
  if (text.length > 15000) return 'Resume must be under 15,000 characters';
  return null;
}

export function validateJDText(text: string): string | null {
  if (!text.trim()) return 'Job description is required';
  if (text.length < 50) return 'Job description must be at least 50 characters';
  if (text.length > 8000) return 'Job description must be under 8,000 characters';
  return null;
}
