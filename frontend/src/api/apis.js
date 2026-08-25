import api, { cachedGet, clearApiCache } from './client';

export const authApi = {
  login: (payload) => api.post('/auth/login', payload),
  me: () => cachedGet('/auth/me'),
};

export const studentApi = {
  dashboard: () => cachedGet('/student-dashboard/me'),
  academics: () => cachedGet('/student-dashboard/me/academics'),
  mastery: () => cachedGet('/student-dashboard/me/mastery'),
  trend: (conceptId) => cachedGet('/student-dashboard/me/mastery-trend', { params: { concept_id: conceptId } }),
  recentActivity: (limit = 20) => cachedGet('/student-dashboard/me/recent-activity', { params: { limit } }),
};

export const tutorApi = {
  concepts: () => cachedGet('/tutor/concepts'),
  nextQuestion: (studentCode, conceptId) => cachedGet(`/tutor/next-question/${encodeURIComponent(studentCode)}/${encodeURIComponent(conceptId)}`),
  adaptiveAttempt: (payload) => api.post('/tutor/adaptive-attempt', payload),
  startSession: (payload) => api.post('/tutor/sessions/start', payload),
  session: (sessionId) => cachedGet(`/tutor/sessions/${sessionId}`),
  nextSessionQuestion: (sessionId) => cachedGet(`/tutor/sessions/${sessionId}/next-question`),
  answer: (sessionId, payload) => api.post(`/tutor/sessions/${sessionId}/answer`, payload),
  endSession: (sessionId, reason = 'STUDENT_ENDED') => api.post(`/tutor/sessions/${sessionId}/end`, { reason }),
  sessions: (studentCode, limit = 20) => cachedGet(`/tutor/sessions/student/${encodeURIComponent(studentCode)}`, { params: { limit } }),
  history: (studentCode, conceptId, limit = 50) => cachedGet(`/tutor/history/${encodeURIComponent(studentCode)}${conceptId ? `/${encodeURIComponent(conceptId)}` : ''}`, { params: { limit } }),
  recommendations: (studentCode, limit = 3) => cachedGet(`/tutor/recommendations/${encodeURIComponent(studentCode)}`, { params: { limit } }),
};

export const facultyApi = {
  overview: () => cachedGet('/faculty/learning/overview'),
  riskSummary: () => cachedGet('/dashboard/summary'),
  atRisk: (limit = 50) => cachedGet('/dashboard/at-risk', { params: { limit } }),
  weakConcepts: (limit = 10) => cachedGet('/faculty/learning/weak-concepts', { params: { limit } }),
  misconceptions: (limit = 20) => cachedGet('/faculty/learning/misconceptions', { params: { limit } }),
  student: (code) => cachedGet(`/faculty/learning/student/${encodeURIComponent(code)}`),
  studentRisk: (code) => cachedGet(`/dashboard/student/${encodeURIComponent(code)}`),
  riskHistory: (code) => cachedGet(`/dashboard/student/${encodeURIComponent(code)}/risk-history`),
  interventions: (limit = 100) => cachedGet('/dashboard/interventions', { params: { status: 'PENDING_REVIEW', limit } }),
  evaluateAll: (limit, force = false) => api.post('/risk/evaluate-all', null, { params: { limit, force } }),
  approveIntervention: (taskId) => api.patch(`/risk/interventions/${taskId}/approve`).then((response) => { clearApiCache(); return response; }),
  rejectIntervention: (taskId) => api.patch(`/risk/interventions/${taskId}/reject`).then((response) => { clearApiCache(); return response; }),
};

export const adminApi = {
  users: () => cachedGet('/auth/users'),
  createUser: (payload) => api.post('/auth/users', payload),
  setUserStatus: (userId, isActive) => api.patch(`/auth/users/${userId}/status`, { is_active: isActive }),
};
