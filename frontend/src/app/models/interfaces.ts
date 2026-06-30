/** TypeScript interfaces mirroring the backend Pydantic models. */

/** Chat message displayed in the UI. */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  mode?: 'chat' | 'verification' | 'analysis' | 'roadmap' | 'challenge_response';
  challengeData?: ChallengeData;
  skillScores?: SkillScore[];
  analysis?: AnalysisResult;
  roadmap?: Roadmap;
}

/** Skill verification challenge data. */
export interface ChallengeData {
  type: 'code' | 'math' | 'logic';
  question: string;
  skill_being_tested: string;
  difficulty: 'easy' | 'intermediate' | 'hard';
  options?: string[];
  code_template?: string;
  expected_format?: string;
  time_limit_seconds: number;
}

/** Individual skill score after verification. */
export interface SkillScore {
  skill_name: string;
  claimed_level: string;
  verified_score: number;
  max_score: number;
  feedback: string;
}

/** Full analysis output. */
export interface AnalysisResult {
  target_career: string;
  skill_scores: SkillScore[];
  overall_score: number;
  strengths: string[];
  gaps: string[];
  summary: string;
}

/** A learning resource in a roadmap step. */
export interface RoadmapResource {
  title: string;
  url: string;
  type: 'video' | 'article' | 'course' | 'project' | 'book';
  is_free: boolean;
}

/** Single step in the career roadmap. */
export interface RoadmapStep {
  phase: number;
  title: string;
  description: string;
  skills_covered: string[];
  resources: RoadmapResource[];
  duration_weeks: number;
  milestone: string;
}

/** Complete career roadmap. */
export interface Roadmap {
  target_career: string;
  total_duration_weeks: number;
  phases: RoadmapStep[];
  summary: string;
}

/** API request/response types. */
export interface ChatRequest {
  session_id: string;
  message: string;
  mode: 'chat' | 'challenge_response';
}

export interface ChatResponse {
  message: string;
  mode: 'chat' | 'verification' | 'analysis' | 'roadmap';
  challenge_data?: ChallengeData;
  skill_scores?: SkillScore[];
  analysis?: AnalysisResult;
  roadmap?: Roadmap;
}

export interface SessionState {
  session_id: string;
  current_mode: string;
  target_career?: string;
  claimed_skills: string[];
  verified_scores: SkillScore[];
  overall_score?: number;
  roadmap?: Roadmap;
}
