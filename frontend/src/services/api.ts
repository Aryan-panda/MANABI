import { Agent, Conversation, Message, StudentProfile, AttendanceRecord, MemoryItem, Citation } from '../types';

const API_BASE = '/api/v1';

export const api = {
  // Agents
  async getAgents(): Promise<Agent[]> {
    const res = await fetch(`${API_BASE}/agents`);
    if (!res.ok) throw new Error('Failed to fetch agents');
    return res.json();
  },

  // Conversations
  async getConversations(): Promise<Conversation[]> {
    try {
      const res = await fetch(`${API_BASE}/conversations`);
      if (!res.ok) return [];
      return res.json();
    } catch {
      return [];
    }
  },

  async createConversation(agentId: string, title?: string): Promise<Conversation> {
    const res = await fetch(`${API_BASE}/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId, title: title || 'New Session' }),
    });
    if (!res.ok) throw new Error('Failed to create conversation');
    return res.json();
  },

  async getConversation(id: string): Promise<Conversation> {
    const res = await fetch(`${API_BASE}/conversations/${id}`);
    if (!res.ok) throw new Error('Failed to fetch conversation');
    return res.json();
  },

  // Streaming SSE Messages
  async streamMessage(
    conversationId: string,
    content: string,
    onToken: (token: string) => void,
    onDone: (messageId?: string) => void,
    onError: (err: Error) => void
  ) {
    try {
      const response = await fetch(`${API_BASE}/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify({ content, stream: true }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No readable stream available.');

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith('data:')) continue;
          const jsonStr = trimmed.replace(/^data:\s*/, '');
          try {
            const data = JSON.parse(jsonStr);
            if (data.type === 'token') {
              onToken(data.delta);
            } else if (data.type === 'end') {
              onDone(data.message_id);
              return;
            }
          } catch {
            // Ignore parse errors on partial frames
          }
        }
      }
      onDone();
    } catch (err: any) {
      onError(err);
    }
  },

  // Academic SIS
  async getStudentProfile(studentId: string = 'STU1001'): Promise<StudentProfile> {
    const res = await fetch(`${API_BASE}/academic/profile?student_id=${studentId}`);
    if (!res.ok) throw new Error('Student profile unavailable');
    return res.json();
  },

  async getAttendance(studentId: string = 'STU1001'): Promise<AttendanceRecord[]> {
    const res = await fetch(`${API_BASE}/academic/attendance?student_id=${studentId}`);
    if (!res.ok) return [];
    return res.json();
  },

  async reviewPlan(rawPlan: string, studentId: string = 'STU1001'): Promise<any> {
    const res = await fetch(`${API_BASE}/academic/plan/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_plan: rawPlan, student_id: studentId }),
    });
    if (!res.ok) throw new Error('Plan review failed');
    return res.json();
  },

  // Engineering Calculator & Diagrams
  async calculate(tool: string, parameters: Record<string, any>): Promise<any> {
    const res = await fetch(`${API_BASE}/engineering/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool, parameters }),
    });
    if (!res.ok) throw new Error('Calculation error');
    return res.json();
  },

  async getDiagram(diagramType: string = 'system', title?: string): Promise<{ mermaid_code: string; is_valid: boolean }> {
    const res = await fetch(`${API_BASE}/engineering/diagram`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ diagram_type: diagramType, title }),
    });
    if (!res.ok) throw new Error('Failed to generate diagram');
    return res.json();
  },

  // Memory
  async getMemories(): Promise<MemoryItem[]> {
    const res = await fetch(`${API_BASE}/memory`);
    if (!res.ok) return [];
    return res.json();
  },

  async addMemory(key: string, value: string, type: string = 'preference'): Promise<MemoryItem> {
    const res = await fetch(`${API_BASE}/memory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, value, type }),
    });
    if (!res.ok) throw new Error('Failed to save memory');
    return res.json();
  },

  async deleteMemory(id: string): Promise<boolean> {
    const res = await fetch(`${API_BASE}/memory/${id}`, { method: 'DELETE' });
    return res.ok;
  },
};
