export type AgentId = 'academic' | 'engineering' | 'commerce' | 'management' | 'law';

export interface Agent {
  id: AgentId;
  name: string;
  description: string;
  purpose: string;
  capabilities: string[];
  allowed_tools: string[];
  retrieval_domain: string | null;
}

export interface Citation {
  chunk_id: string;
  title: string;
  domain: string;
  source: string;
  section?: string;
  subsection?: string;
  text: string;
  page?: number;
  relevance_score: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  model?: string;
  token_count?: number;
  created_at: string;
  citations?: Citation[];
  diagrams?: string[];
  isStreaming?: boolean;
}

export interface Conversation {
  id: string;
  agent_id: AgentId;
  title: string;
  status: string;
  created_at: string;
  messages: Message[];
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
}

export interface StudentProfile {
  student_id: string;
  full_name: string;
  email: string;
  program: string;
  department: string;
  semester: number;
  cgpa: number;
  credits_earned: number;
  credits_required: number;
  academic_status: string;
}

export interface AttendanceRecord {
  course_code: string;
  course_name: string;
  classes_held: number;
  classes_attended: number;
  percentage: number;
  is_critical: boolean;
}

export interface MemoryItem {
  id: string;
  type: string;
  key: string;
  value: string;
  confidence: 'low' | 'medium' | 'high';
  evidence_count: number;
  last_seen: string;
}
