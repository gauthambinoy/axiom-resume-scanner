export type Priority = 'critical' | 'high' | 'medium' | 'low';
export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
export type Grade = 'A+' | 'A' | 'B+' | 'B' | 'C+' | 'C' | 'D' | 'F';
export type ReadinessLevel = 'INTERVIEW_READY' | 'NEEDS_WORK' | 'AT_RISK';

export interface KeywordMatchResponse {
  keyword: string;
  found_in_sections: string[];
  frequency_in_resume: number;
}

export interface ATSScoreResponse {
  overall_score: number;
  keyword_match_score: number;
  keyword_placement_score: number;
  section_score: number;
  formatting_score: number;
  relevance_score: number;
  matched_keywords: KeywordMatchResponse[];
  missing_keywords: string[];
  skills_only_keywords: string[];
  section_warnings: string[];
  formatting_warnings: string[];
  grade: Grade;
}

export interface SignalResponse {
  name: string;
  score: number;
  max_score: number;
  percentage: number;
  details: string;
  flagged_items: string[];
}

export interface BulletAnalysisResponse {
  text: string;
  word_count: number;
  structure_type: string;
  first_word: string;
  flags: string[];
  ai_risk: 'clean' | 'suspicious' | 'flagged';
  diff_from_previous: number | null;
}

export interface SummaryAnalysisResponse {
  adjective_count: number;
  adjectives_found: string[];
  starts_with_adjective: boolean;
  word_count: number;
  has_years_experience: boolean;
  has_seniority_label: boolean;
}

export interface AIDetectionResponse {
  overall_score: number;
  risk_level: RiskLevel;
  signals: SignalResponse[];
  per_bullet_analysis: BulletAnalysisResponse[];
  summary_analysis: SummaryAnalysisResponse;
  top_issues: string[];
}

export interface FixResponse {
  category: string;
  priority: Priority;
  title: string;
  description: string;
  affected_bullets: number[];
  estimated_impact: string;
}

export interface CombinedScoreResponse {
  interview_readiness_score: number;
  readiness_level: ReadinessLevel;
  competitor_percentile: number;
  ats_weight: number;
  ai_weight: number;
}

export interface ScanMetadata {
  processing_time_ms: number;
  engines_used: string[];
  degraded_mode: boolean;
  warnings: string[];
}

export interface ScanResponse {
  scan_id: string;
  timestamp: string;
  ats_score: ATSScoreResponse;
  ai_score: AIDetectionResponse;
  fixes: FixResponse[];
  combined: CombinedScoreResponse;
  metadata: ScanMetadata;
}

export interface QuickScanResponse {
  scan_id: string;
  ats_keyword_score: number;
  ai_detection_score: number;
  readiness_level: ReadinessLevel;
  processing_time_ms: number;
}

export interface CompareResponse {
  before: ScanResponse;
  after: ScanResponse;
  ats_change: number;
  ai_change: number;
  readiness_change: number;
  improved_keywords: string[];
  still_missing: string[];
}

export interface HealthResponse {
  status: string;
  version: string;
  engines: Record<string, boolean>;
}

export interface StatsResponse {
  total_scans: number;
  avg_ats_score: number;
  avg_ai_score: number;
  scans_today: number;
}

export interface KeywordExtractionResponse {
  technical_skills: string[];
  soft_skills: string[];
  tools_and_platforms: string[];
  action_verbs: string[];
  domain_terms: string[];
  certifications: string[];
  all_keywords: string[];
  priority_keywords: string[];
}

export interface BannedPhrasesResponse {
  banned_phrases: string[];
  banned_words: string[];
  ai_patterns: string[];
}

export interface HumanizeResponse {
  original_text: string;
  humanized_text: string;
  original_ai_score: number;
  new_ai_score: number;
  improvement: number;
  retries_used: number;
  success: boolean;
}

export interface ErrorResponse {
  error_code: string;
  message: string;
  details: Record<string, unknown> | null;
  timestamp: string;
}
