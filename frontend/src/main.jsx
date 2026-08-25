import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Activity, AlertTriangle, ArrowUpRight, BarChart3, BookOpen, BrainCircuit, Check,
  ChevronRight, CircleHelp, GraduationCap, LayoutDashboard, LogOut, Menu, Search,
  Settings, ShieldCheck, Sparkles, Target, Users, X,
} from 'lucide-react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { authApi, facultyApi, studentApi, tutorApi } from './api/apis';
import './styles.css';

const roleLinks = {
  STUDENT: [
    ['Overview', 'overview', LayoutDashboard], ['Learn', 'learn', BookOpen], ['Mastery', 'mastery', Target], ['Sessions', 'sessions', Activity],
  ],
  FACULTY: [
    ['Overview', 'overview', LayoutDashboard], ['At-risk students', 'students', Users], ['Learning insights', 'insights', BarChart3], ['Interventions', 'interventions', ShieldCheck],
  ],
  ADMIN: [['System overview', 'overview', LayoutDashboard], ['User management', 'users', Users], ['Faculty views', 'faculty', BarChart3]],
};

const unwrap = (value) => value?.data ?? value;
const pick = (object, keys, fallback = 0) => keys.reduce((found, key) => found ?? object?.[key], null) ?? fallback;
const displayName = (user) => user?.full_name || user?.name || user?.email?.split('@')[0] || 'there';
const formatNumber = (value, suffix = '') => value === null || value === undefined ? '—' : `${typeof value === 'number' ? Math.round(value * 10) / 10 : value}${suffix}`;
const apiErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg || item.detail).join(', ');
  return detail || error?.message || fallback;
};
const rolePath = (role) => {
  const normalizedRole = String(role || 'STUDENT').toUpperCase();
  return normalizedRole === 'FACULTY' ? '/faculty' : normalizedRole === 'ADMIN' ? '/admin' : '/student';
};
const pageFromPath = (role, pathname = window.location.pathname) => {
  const base = rolePath(role).slice(1);
  const parts = pathname.split('/').filter(Boolean);
  if (parts[0] !== base) return 'overview';
  if (role === 'FACULTY' && parts[1] === 'students' && parts[2]) return 'student:' + decodeURIComponent(parts[2]);
  return parts[1] || 'overview';
};
const pathForPage = (role, page) => {
  const base = rolePath(role);
  if (page === 'overview') return base;
  if (page.startsWith('student:')) return base + '/students/' + encodeURIComponent(page.slice(8));
  return base + '/' + page;
};
const displayValue = (value) => {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'object') {
    if (Array.isArray(value)) return value.map(displayValue).join(', ');
    return value.name || value.label || value.title || value.category || value.actions || JSON.stringify(value);
  }
  return String(value);
};

function App() {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem('user') || 'null'));
  const [restore, setRestore] = useState(Boolean(localStorage.getItem('access_token')) && !user);
  const [page, setPage] = useState('overview');
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    if (!restore) return;
    authApi.me().then(({ data }) => { localStorage.setItem('user', JSON.stringify(data)); setUser(data); }).catch(() => setUser(null)).finally(() => setRestore(false));
  }, [restore]);

  useEffect(() => {
    const syncRoute = () => user && setPage(pageFromPath(String(user.role || user.user_role || 'STUDENT').toUpperCase()));
    syncRoute();
    window.addEventListener('popstate', syncRoute);
    return () => window.removeEventListener('popstate', syncRoute);
  }, [user]);

  if (restore) return <div className="center-state"><div className="loader" /><span>Restoring your workspace</span></div>;
  if (!user) { if (window.location.pathname !== '/login') window.history.replaceState({}, '', '/login'); return <Login onLogin={setUser} />; }

  const role = String(user.role || user.user_role || 'STUDENT').toUpperCase();
  const navigate = (nextPage) => { window.history.pushState({}, '', pathForPage(role, nextPage)); setPage(nextPage); };
  const logout = () => { localStorage.removeItem('access_token'); localStorage.removeItem('user'); window.history.replaceState({}, '', '/login'); setUser(null); };
  return <Shell user={user} role={role} page={page} setPage={navigate} menuOpen={menuOpen} setMenuOpen={setMenuOpen} logout={logout}><Page role={role} page={page} user={user} setPage={navigate} /></Shell>;
}

function Login({ onLogin }) {
  const [form, setForm] = useState({ email: '', password: '' });
  const [state, setState] = useState({ loading: false, error: '' });
  const submit = async (event) => {
    event.preventDefault(); setState({ loading: true, error: '' });
    try {
      const { data } = await authApi.login(form);
      const token = data.access_token || data.token;
      if (!token) throw new Error('The server did not return an access token.');
      localStorage.setItem('access_token', token);
      const me = await authApi.me();
      localStorage.setItem('user', JSON.stringify(me.data));
      window.history.replaceState({}, '', rolePath(me.data.role));
      onLogin(me.data);
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      setState({ loading: false, error: apiErrorMessage(error, 'Unable to sign in.') });
    }
  };
  return <main className="login-page"><div className="login-aside"><div className="brand-mark"><Sparkles size={18} /> EDUCOMPASS</div><div className="login-message"><p className="eyebrow">AI student success platform</p><h1>Make every learning signal useful.</h1><p>One calm workspace for helping students build momentum and giving faculty the context to act early.</p></div><div className="aside-foot"><span>SIH26 production workspace</span><span className="dot" /><span>Secure by design</span></div></div><section className="login-panel"><div className="login-form-wrap"><div className="mobile-brand brand-mark"><Sparkles size={18} /> EDUCOMPASS</div><p className="eyebrow">Welcome back</p><h2>Sign in to your workspace</h2><p className="muted">Use your institutional account to continue.</p><form onSubmit={submit}><label>Email<input type="email" required placeholder="you@university.edu" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label><label>Password<input type="password" required placeholder="Enter your password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>{state.error && <div className="form-error"><AlertTriangle size={16} />{state.error}</div>}<button className="button primary wide" disabled={state.loading}>{state.loading ? 'Signing in...' : 'Continue'} <ArrowUpRight size={16} /></button></form><p className="login-note"><ShieldCheck size={15} /> Your role and permissions are managed by your institution.</p></div></section></main>;
}

function Shell({ user, role, page, setPage, menuOpen, setMenuOpen, logout, children }) {
  const links = roleLinks[role] || roleLinks.STUDENT;
  const title = links.find((link) => link[1] === page)?.[0] || 'Overview';
  return <div className="app-shell"><aside className={`sidebar ${menuOpen ? 'open' : ''}`}><div className="brand-mark"><Sparkles size={18} /> EDUCOMPASS</div><div className="workspace-label">{role === 'STUDENT' ? 'Learning workspace' : 'Insights workspace'}</div><nav>{links.map(([label, key, Icon]) => <button className={page === key ? 'active' : ''} key={key} onClick={() => { setPage(key); setMenuOpen(false); }}><Icon size={18} /><span>{label}</span>{page === key && <ChevronRight size={15} className="nav-arrow" />}</button>)}</nav><div className="sidebar-bottom"><button><Settings size={18} /><span>Settings</span></button><button className="user-mini" onClick={logout}><div className="avatar">{displayName(user)[0].toUpperCase()}</div><div><strong>{displayName(user)}</strong><small>{role.toLowerCase()}</small></div><LogOut size={16} /></button></div></aside>{menuOpen && <button className="scrim" onClick={() => setMenuOpen(false)} aria-label="Close navigation" />}<main className="main"><header className="topbar"><button className="icon-button menu-button" onClick={() => setMenuOpen(true)} aria-label="Open navigation"><Menu size={20} /></button><div><p className="breadcrumb">Workspace <ChevronRight size={13} /> {role.toLowerCase()}</p><h1>{title}</h1></div><div className="top-actions"><button className="icon-button"><CircleHelp size={19} /></button><div className="profile-chip"><div className="avatar">{displayName(user)[0].toUpperCase()}</div><span>{displayName(user)}</span></div></div></header><div className="content">{children}</div></main></div>;
}

function Page({ role, page, user, setPage }) {
  if (role === 'STUDENT') {
    if (page === 'overview') return <StudentDashboard setPage={setPage} />;
    if (page === 'learn') return <LearnPage user={user} />;
    if (page === 'mastery') return <MasteryPage />;
    if (page === 'sessions') return <SessionsPage user={user} />;
  }
  if (role === 'FACULTY') return page === 'overview' ? <FacultyOverview setPage={setPage} role={role} /> : <FacultyDataPage page={page} setPage={setPage} />;
  if (role === 'ADMIN') return page === 'overview' ? <FacultyOverview setPage={setPage} role={role} /> : page === 'users' ? <AdminUsers /> : <AdminPlaceholder page={page} />;
  return <AdminPlaceholder page={page} />;
}

function StudentDashboard({ setPage }) {
  const [state, setState] = useState({ loading: true, data: null, error: '' });
  useEffect(() => { studentApi.dashboard().then(({ data }) => setState({ loading: false, data: unwrap(data), error: '' })).catch((e) => setState({ loading: false, data: null, error: e.response?.status === 503 ? 'AI services are temporarily unavailable.' : 'We could not load your learning overview.' })); }, []);
  const data = state.data || {};
  const kpis = [
    ['Average mastery', pick(data, ['average_mastery', 'avg_mastery'], null), '%', Target],
    ['Mastered concepts', pick(data, ['mastered_concepts', 'mastered_count'], null), '', Check],
    ['Practice queue', pick(data, ['concepts_needing_practice', 'needs_practice'], null), '', BookOpen],
    ['Completed sessions', pick(data, ['completed_sessions', 'sessions_completed'], null), '', Activity],
  ];
  return <><div className="welcome-row"><div><p className="eyebrow">Your learning pulse</p><h2>Keep your momentum, one concept at a time.</h2><p className="muted">Your workspace updates as you learn. Focused practice is already waiting.</p></div><button className="button primary" onClick={() => setPage('learn')}><Sparkles size={16} /> Start learning</button></div>{state.error && <Notice text={state.error} />}<div className="kpi-grid">{kpis.map(([label, value, suffix, Icon]) => <Metric key={label} label={label} value={formatNumber(value, suffix)} icon={Icon} loading={state.loading} />)}</div><div className="dashboard-grid"><section className="panel support-panel"><div className="panel-heading"><div><p className="eyebrow">Support status</p><h3>{data.support_message || 'Your learning plan is ready'}</h3></div><span className={`status-dot ${String(data.support_status || 'ON_TRACK').toLowerCase()}`} /></div><p className="muted">{data.support_detail || 'Complete a practice session to keep your progress visible here.'}</p><div className="status-line"><span>Current pathway</span><strong>{data.pathway || 'Personalized practice'}</strong></div></section><section className="panel next-panel"><div className="panel-heading"><div><p className="eyebrow">Recommended next</p><h3>Build confidence where it counts</h3></div><ArrowUpRight size={18} /></div>{data.recommended_concepts?.length ? data.recommended_concepts.slice(0, 2).map((concept) => <div className="recommendation" key={concept.concept_id || concept.id}><div className="concept-icon"><BrainCircuit size={18} /></div><div><strong>{concept.topic || concept.name}</strong><p>{concept.reason || 'Recommended for your next practice session.'}</p></div><button className="text-button" onClick={() => setPage('learn')}>Learn <ChevronRight size={15} /></button></div>) : <EmptyState icon={BrainCircuit} title="Recommendations will appear here" text="Your next concept will be selected from backend learning signals." />}</section></div><section className="panel"><div className="section-heading"><div><p className="eyebrow">Recent activity</p><h3>Learning sessions</h3></div><button className="text-button" onClick={() => setPage('sessions')}>View history <ArrowUpRight size={15} /></button></div>{data.recent_sessions?.length ? <div className="table-wrap"><table><thead><tr><th>Session</th><th>Progress</th><th>Accuracy</th><th>Status</th></tr></thead><tbody>{data.recent_sessions.map((session, i) => <tr key={session.session_id || i}><td><strong>{session.concept_name || session.topic || 'Learning session'}</strong><small>{session.created_at ? new Date(session.created_at).toLocaleDateString() : 'Recent'}</small></td><td>{session.answered ?? 0} / {session.target_questions ?? session.target ?? '—'} answered</td><td>{formatNumber(session.accuracy, '%')}</td><td><span className="table-status">{session.status || 'IN PROGRESS'}</span></td></tr>)}</tbody></table></div> : <EmptyState icon={Activity} title="No sessions yet" text="Start a learning session to see your progress build here." action="Start learning" onAction={() => setPage('learn')} />}</section></>;
}

function FacultyOverview({ setPage, role }) { const [state, setState] = useState({ loading: true, data: {}, risk: {} }); const [evalState, setEvalState] = useState({ busy: false, message: '' }); useEffect(() => { Promise.allSettled([facultyApi.overview(), facultyApi.riskSummary()]).then(([overview, risk]) => setState({ loading: false, data: unwrap(overview.value?.data) || {}, risk: unwrap(risk.value?.data) || {} })); }, []); const d = state.data; const r = state.risk; const metrics = [['Total students', d.students?.total, Users], ['Evaluated students', d.risk?.evaluated_students, ShieldCheck], ['Average mastery', formatNumber(d.learning?.average_mastery_percentage, '%'), Target], ['Pending interventions', d.faculty?.pending_interventions, AlertTriangle]]; const risks = [['LOW', r.low_risk_students, 'low'], ['MODERATE', r.moderate_risk_students, 'moderate'], ['CRITICAL', r.critical_risk_students, 'critical']]; const evaluate = async (event) => { setEvalState({ busy: true, message: '' }); try { const { data } = await facultyApi.evaluateAll(Number(event.target.limit.value), event.target.force.checked); setEvalState({ busy: false, message: `Evaluated ${data.evaluated}, skipped ${data.skipped}, failed ${data.failed}. Refreshing analytics...` }); const [overview, risk] = await Promise.all([facultyApi.overview(), facultyApi.riskSummary()]); setState({ loading: false, data: unwrap(overview.data), risk: unwrap(risk.data) }); } catch (e) { setEvalState({ busy: false, message: e.response?.data?.detail || 'Evaluation failed. This action requires an ADMIN account.' }); } }; return <><div className="welcome-row"><div><p className="eyebrow">Faculty command center</p><h2>See where attention can change outcomes.</h2><p className="muted">A focused view of learning health, risk signals, and follow-through.</p></div><div className="overview-actions"><button className="button secondary" onClick={() => setPage('students')}><Users size={16} /> Review students</button>{role === 'ADMIN' && <form className="evaluate-form" onSubmit={evaluate}><label>Evaluate up to <input name="limit" type="number" min="1" max="5000" defaultValue="100" /></label><label className="check-label"><input name="force" type="checkbox" /> Re-evaluate</label><button className="button primary" disabled={evalState.busy}>{evalState.busy ? 'Evaluating...' : 'Evaluate students'} <Activity size={15} /></button></form>}</div></div>{evalState.message && <Notice text={evalState.message} />}<div className="kpi-grid">{metrics.map(([label, value, Icon]) => <Metric key={label} label={label} value={state.loading ? '—' : formatNumber(value)} icon={Icon} loading={state.loading} />)}</div><div className="faculty-grid"><section className="panel risk-panel"><div className="section-heading"><div><p className="eyebrow">Early warning system</p><h3>Risk distribution</h3></div><span className="muted">Current snapshot</span></div><div className="risk-display"><div className="donut"><div><strong>{formatNumber(pick(r, ['total_students', 'total'], d.students?.total))}</strong><small>students</small></div></div><div className="risk-legend">{risks.map(([name, value, tone]) => <div key={name}><span><i className={`legend-dot ${tone}`} />{name}</span><strong>{formatNumber(value)}</strong></div>)}</div></div></section><section className="panel"><div className="section-heading"><div><p className="eyebrow">Learning insights</p><h3>Concepts needing attention</h3></div><BarChart3 size={18} /></div><EmptyState icon={BarChart3} title="Explore learning insights" text="Open the Learning insights section for live weak-concept and misconception rankings." action="View insights" onAction={() => setPage('insights')} /></section></div><section className="panel"><div className="section-heading"><div><p className="eyebrow">Faculty queue</p><h3>Students who may need a closer look</h3></div><button className="text-button" onClick={() => setPage('students')}>Open roster <ArrowUpRight size={15} /></button></div><EmptyState icon={Users} title="Open the at-risk roster" text="Review backend-evaluated risk, mastery, and predictive factors in one place." action="View students" onAction={() => setPage('students')} /></section></> }

function Metric({ label, value, icon: Icon, loading }) { return <div className="metric"><div className="metric-icon"><Icon size={18} /></div><div><span>{label}</span><strong>{loading ? <i className="skeleton" /> : value}</strong></div></div>; }
function Notice({ text }) { return <div className="notice"><AlertTriangle size={17} /><span>{text}</span></div>; }
function EmptyState({ icon: Icon, title, text, action, onAction }) { return <div className="empty-state"><div className="empty-icon"><Icon size={19} /></div><strong>{title}</strong><p>{text}</p>{action && <button className="button secondary small" onClick={onAction}>{action} <ArrowUpRight size={14} /></button>}</div>; }
function LearnPage({ user }) {
  const studentCode = user?.student_code || user?.student?.student_code;
  const [state, setState] = useState({ loading: true, concepts: [], error: '' });
  const [selected, setSelected] = useState('');
  const [target, setTarget] = useState(5);
  const [language, setLanguage] = useState('en-IN');
  const [started, setStarted] = useState(null);
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    tutorApi.concepts().then(({ data }) => {
      const concepts = unwrap(data)?.concepts || [];
      setState({ loading: false, concepts, error: '' });
      setSelected(concepts[0]?.concept_id || '');
    }).catch((e) => setState({ loading: false, concepts: [], error: e.response?.data?.detail || 'Could not load concepts.' }));
  }, []);

  const start = async () => {
    if (!studentCode || !selected) return;
    setBusy(true);
    try {
      const { data } = await tutorApi.startSession({ student_code: studentCode, concept_id: selected, target_questions: Number(target), language_code: language });
      const session = unwrap(data);
      localStorage.setItem('active_session_id', session.session_id);
      setStarted(session);
      setMessages(session.next?.question ? [{ role: 'tutor', text: session.next.question.text }] : []);
    } catch (e) { setState((current) => ({ ...current, error: e.response?.data?.detail || 'Could not start the learning session.' })); } finally { setBusy(false); }
  };

  const submit = async (event) => {
    event.preventDefault();
    const question = started?.next?.question;
    if (!answer.trim() || !question) return;
    setBusy(true);
    setError('');
    try {
      const { data } = await tutorApi.answer(started.session_id, { question_id: question.question_id, student_answer: answer });
      const result = unwrap(data);
      const attempt = result.attempt;
      setFeedback(attempt);
      setMessages((current) => [...current, { role: 'student', text: answer }, { role: 'tutor', text: attempt.tutor?.message || 'Your response was reviewed.' }, ...(attempt.tutor?.follow_up_question ? [{ role: 'tutor', text: attempt.tutor.follow_up_question, followUp: true }] : []), ...(result.next?.question ? [{ role: 'tutor', text: result.next.question.text }] : [])]);
      setStarted((current) => ({ ...current, next: result.next, progress: result.progress }));
      setAnswer('');
    } catch (e) {
      const message = apiErrorMessage(e, 'Could not submit this answer.');
      setError(message);
      setMessages((current) => [...current, { role: 'tutor', text: `I could not process that answer: ${message}` }]);
      if (e.response?.status === 400 && /already answered/i.test(message)) {
        try {
          const { data } = await tutorApi.nextSessionQuestion(started.session_id);
          setStarted((current) => ({ ...current, next: unwrap(data) }));
        } catch (refreshError) {
          if (/not active/i.test(apiErrorMessage(refreshError, ''))) {
            localStorage.removeItem('active_session_id');
            setStarted(null);
          }
        }
      }
    } finally { setBusy(false); }
  };

  const end = async () => { if (!window.confirm('End this learning session?')) return; setBusy(true); try { await tutorApi.endSession(started.session_id); localStorage.removeItem('active_session_id'); setStarted(null); setFeedback(null); } finally { setBusy(false); } };
  if (started) return <TutorChat session={started} feedback={feedback} messages={messages} answer={answer} setAnswer={setAnswer} submit={submit} busy={busy} end={end} error={error} />;
  return <><div className="welcome-row"><div><p className="eyebrow">Adaptive learning</p><h2>Choose a concept and start a focused session.</h2><p className="muted">EduCompass selects each next question from your backend learning state.</p></div></div>{state.error && <Notice text={state.error} />}<section className="panel session-start"><div className="session-start-icon"><BrainCircuit size={23} /></div><div><p className="eyebrow">Start a session</p><h3>What would you like to practice?</h3><p className="muted">Answer in natural language and receive guidance after each response.</p></div><div className="session-fields"><label>Concept<select value={selected} onChange={(e) => setSelected(e.target.value)} disabled={state.loading || !state.concepts.length}><option value="">{state.loading ? 'Loading concepts...' : 'Select a concept'}</option>{state.concepts.map((concept) => <option key={concept.concept_id} value={concept.concept_id}>{concept.topic_name}</option>)}</select></label><label>Questions<select value={target} onChange={(e) => setTarget(e.target.value)}><option value="3">3 questions</option><option value="5">5 questions</option><option value="10">10 questions</option></select></label><label>Language<select value={language} onChange={(e) => setLanguage(e.target.value)}><option value="en-IN">English</option><option value="hi-IN">Hindi</option><option value="mr-IN">Marathi</option></select></label></div><button className="button primary" onClick={start} disabled={busy || !selected || !studentCode}>{busy ? 'Starting session...' : 'Start learning session'} <ArrowUpRight size={16} /></button>{!studentCode && <p className="field-hint">Your account does not have a student code. Ask an administrator to link your student profile.</p>}</section></>;
}

function TutorChat({ session, feedback, messages, answer, setAnswer, submit, busy, end, error }) {
  const progress = session.progress || { answered: 0, target: session.target_questions };
  const next = session.next?.question;
  const complete = session.next?.session_complete;
  return <><div className="welcome-row"><div><p className="eyebrow">AI tutor session</p><h2>{session.concept?.topic_name || session.primary_concept?.topic_name || 'Focused practice'}</h2><p className="muted">{progress.answered} of {progress.target} questions answered <span className="inline-divider" /> {progress.accuracy_percentage ?? 0}% accuracy</p></div><div className="session-progress"><strong>{progress.answered}</strong><span>/ {progress.target}</span><button className="text-button" onClick={end}>End session</button></div></div><div className="progress-track"><div style={{ width: `${Math.min(100, (progress.answered / progress.target) * 100)}%` }} /></div><section className="panel chat-panel"><div className="chat-header"><div className="tutor-avatar"><Sparkles size={17} /></div><div><strong>EduCompass Tutor</strong><small>Gemini + LangGraph guidance</small></div><span className="online-dot" /></div><div className="chat-messages">{messages.map((message, index) => <div className={`chat-bubble ${message.role}`} key={`${message.role}-${index}`}><span>{message.role === 'tutor' ? 'Tutor' : 'You'}</span><p>{message.text}</p></div>)}{busy && <div className="chat-bubble tutor typing"><span>Tutor</span><p><i /><i /><i /></p></div>}</div>{complete ? <div className="chat-complete"><Check size={18} /><strong>Session complete</strong><p>Your backend learning state has been updated.</p></div> : <form className="chat-composer" onSubmit={submit}><textarea value={answer} onChange={(e) => setAnswer(e.target.value)} placeholder="Reply to your tutor..." rows="2" disabled={busy || !next} /><button className="button primary" disabled={busy || !answer.trim() || !next}>{busy ? 'Thinking...' : 'Send answer'} <ArrowUpRight size={15} /></button></form>}</section>{feedback && <div className="chat-feedback"><span className={`tag ${feedback.evaluation?.is_correct ? 'success-tag' : ''}`}>{feedback.evaluation?.diagnosis || 'Response reviewed'}</span><span>{feedback.tutor?.encouragement || 'Keep exploring the idea.'}</span></div>}</>;
}

function SessionWorkspace({ session, feedback, answer, setAnswer, submit, busy, end }) {
  const progress = session.progress || { answered: 0, target: session.target_questions };
  const next = session.next?.question;
  const complete = session.next?.session_complete;
  return <><div className="welcome-row"><div><p className="eyebrow">Active learning session</p><h2>{session.concept?.topic_name || session.primary_concept?.topic_name || 'Focused practice'}</h2><p className="muted">Question {Math.min(progress.answered + 1, progress.target)} of {progress.target} <span className="inline-divider" /> {progress.accuracy_percentage ?? 0}% accuracy</p></div><div className="session-progress"><strong>{progress.answered}</strong><span>/ {progress.target} answered</span><button className="text-button" onClick={end}>End session</button></div></div><div className="progress-track"><div style={{ width: `${Math.min(100, (progress.answered / progress.target) * 100)}%` }} /></div>{complete ? <section className="panel completion"><div className="empty-icon"><Check size={21} /></div><p className="eyebrow">Session complete</p><h2>Nice work staying with it.</h2><p className="muted">You answered {progress.answered} questions with {progress.accuracy_percentage ?? 0}% accuracy. Your mastery has been updated.</p></section> : <div className="session-layout"><section className="panel question-panel"><div className="question-meta"><span className="tag">{next?.difficulty || 'Adaptive'} difficulty</span><span className="muted">Current mastery {next?.current_mastery == null ? '—' : `${Math.round(next.current_mastery * 100)}%`}</span></div><h3>{next?.text || 'Loading your next question...'}</h3><form onSubmit={submit}><textarea value={answer} onChange={(e) => setAnswer(e.target.value)} placeholder="Write how you would solve this..." rows="7" disabled={busy} /><button className="button primary" disabled={busy || !answer.trim()}>{busy ? 'Checking answer...' : 'Submit answer'} <ArrowUpRight size={16} /></button></form></section><aside className="panel feedback-panel">{feedback ? <><p className="eyebrow">Tutor feedback</p><h3>{feedback.evaluation?.diagnosis || 'Response reviewed'}</h3><p className="feedback-copy">{feedback.socratic_message || feedback.evaluation?.feedback || 'Keep going. Your next question is ready.'}</p>{feedback.encouragement && <div className="encouragement"><Sparkles size={16} />{feedback.encouragement}</div>}<div className="mastery-change"><span>Mastery change</span><strong>{feedback.mastery?.before == null ? '—' : `${Math.round(feedback.mastery.before * 100)}% -> ${Math.round(feedback.mastery.after * 100)}%`}</strong></div></> : <EmptyState icon={Sparkles} title="Your tutor is ready" text="Submit your answer to receive guidance and your next adaptive question." />}</aside></div>}</>;
}

function MasteryPage() {
  const [state, setState] = useState({ loading: true, data: null, error: '' });
  const [selected, setSelected] = useState('');
  const [trend, setTrend] = useState({ loading: false, points: [], error: '' });
  useEffect(() => { studentApi.mastery().then(({ data }) => { const result = unwrap(data); setState({ loading: false, data: result, error: '' }); setSelected(result?.concepts?.[0]?.concept_id || ''); }).catch((e) => setState({ loading: false, data: null, error: e.response?.data?.detail || 'Could not load mastery.' })); }, []);
  useEffect(() => { if (!selected) return; setTrend({ loading: true, points: [], error: '' }); studentApi.trend(selected).then(({ data }) => { const points = unwrap(data)?.points || []; setTrend({ loading: false, points: points.map((point, index) => ({ ...point, attempt: index + 1, mastery: point.mastery_after_percentage })), error: '' }); }).catch(() => setTrend({ loading: false, points: [], error: 'No trend data is available for this concept yet.' })); }, [selected]);
  const concepts = state.data?.concepts || [];
  return <><div className="welcome-row"><div><p className="eyebrow">Concept mastery</p><h2>See your progress across the curriculum.</h2><p className="muted">Mastery values and attempts come directly from your learning activity.</p></div></div>{state.error && <Notice text={state.error} />}<section className="panel trend-panel"><div className="section-heading"><div><p className="eyebrow">Mastery trend</p><h3>Progress over attempts</h3></div><select value={selected} onChange={(e) => setSelected(e.target.value)}>{concepts.map((concept) => <option key={concept.concept_id} value={concept.concept_id}>{concept.topic_name}</option>)}</select></div>{trend.loading ? <div className="chart-loading"><div className="loader" /> Loading trend...</div> : trend.points.length ? <div className="chart-wrap"><ResponsiveContainer width="100%" height={240}><LineChart data={trend.points}><XAxis dataKey="attempt" /><YAxis domain={[0, 100]} unit="%" /><Tooltip formatter={(value) => [`${value}%`, 'Mastery']} /><Line type="monotone" dataKey="mastery" stroke="#2458e6" strokeWidth={3} dot={{ r: 4 }} /></LineChart></ResponsiveContainer></div> : <EmptyState icon={Activity} title="No trend data yet" text={trend.error || 'Complete an attempt to see mastery progression.'} />}</section>{state.loading ? <div className="mastery-grid">{[1, 2, 3].map((item) => <div className="panel mastery-card" key={item}><i className="skeleton" /><i className="skeleton short" /></div>)}</div> : concepts.length ? <div className="mastery-grid">{concepts.map((concept) => <div className="panel mastery-card" key={concept.concept_id}><div className="panel-heading"><div><p className="eyebrow">{concept.mastered ? 'Mastered' : 'In progress'}</p><h3>{concept.topic_name}</h3></div><strong className="mastery-value">{concept.mastery_percentage}%</strong></div><div className="mastery-track"><div style={{ width: `${concept.mastery_percentage}%` }} /></div><div className="mastery-meta"><span>{concept.total_attempts} attempts</span><span>{concept.consecutive_correct} consecutive correct</span>{concept.prerequisite_topic_name && <span>Prerequisite: {concept.prerequisite_topic_name}</span>}</div></div>)}</div> : <section className="panel empty-page"><div className="empty-icon"><Target size={23} /></div><h2>No mastery data yet</h2><p className="muted">Start a learning session to build your concept map.</p></section>}</>;
}

function MasteryCards() {
  const [state, setState] = useState({ loading: true, data: null, error: '' });
  useEffect(() => { studentApi.mastery().then(({ data }) => setState({ loading: false, data: unwrap(data), error: '' })).catch((e) => setState({ loading: false, data: null, error: e.response?.data?.detail || 'Could not load mastery.' })); }, []);
  const concepts = state.data?.concepts || [];
  return <><div className="welcome-row"><div><p className="eyebrow">Concept mastery</p><h2>See your progress across the curriculum.</h2><p className="muted">Mastery values and attempts come directly from your learning activity.</p></div></div>{state.error && <Notice text={state.error} />}{state.loading ? <div className="mastery-grid">{[1, 2, 3].map((item) => <div className="panel mastery-card" key={item}><i className="skeleton" /><i className="skeleton short" /></div>)}</div> : concepts.length ? <div className="mastery-grid">{concepts.map((concept) => <div className="panel mastery-card" key={concept.concept_id}><div className="panel-heading"><div><p className="eyebrow">{concept.mastered ? 'Mastered' : 'In progress'}</p><h3>{concept.topic_name}</h3></div><strong className="mastery-value">{concept.mastery_percentage}%</strong></div><div className="mastery-track"><div style={{ width: `${concept.mastery_percentage}%` }} /></div><div className="mastery-meta"><span>{concept.total_attempts} attempts</span><span>{concept.consecutive_correct} consecutive correct</span>{concept.prerequisite_topic_name && <span>Prerequisite: {concept.prerequisite_topic_name}</span>}</div></div>)}</div> : <section className="panel empty-page"><div className="empty-icon"><Target size={23} /></div><h2>No mastery data yet</h2><p className="muted">Start a learning session to build your concept map.</p></section>}</>;
}

function SessionsPage({ user }) {
  const code = user?.student_code;
  const [state, setState] = useState({ loading: true, data: null, history: null, recommendations: null, error: '' });
  useEffect(() => { if (!code) return; Promise.all([tutorApi.sessions(code), tutorApi.history(code), tutorApi.recommendations(code)]).then(([sessions, history, recommendations]) => setState({ loading: false, data: unwrap(sessions.data), history: unwrap(history.data), recommendations: unwrap(recommendations.data), error: '' })).catch((e) => setState({ loading: false, data: null, history: null, recommendations: null, error: e.response?.data?.detail || 'Could not load learning history.' })); }, [code]);
  const sessions = state.data?.sessions || state.data?.learning_sessions || [];
  if (state.loading) return <LoadingScreen text="Loading session history..." />;
  if (state.error) return <Notice text={state.error} />;
  const interactions = state.history?.interactions || []; const recommendations = state.recommendations?.recommendations || [];
  return <><div className="welcome-row"><div><p className="eyebrow">Session history</p><h2>Review your learning rhythm.</h2><p className="muted">Every session and tutor interaction is stored by the backend.</p></div></div>{sessions.length ? <div className="session-history">{sessions.map((session) => <section className="panel history-row" key={session.session_id}><div><strong>{session.topic_name || 'Learning session'}</strong><small>{session.started_at ? new Date(session.started_at).toLocaleString() : 'Recent session'}</small></div><span>{session.status || '—'}</span><b>{session.accuracy_percentage ?? 0}%</b></section>)}</div> : <section className="panel empty-page"><div className="empty-icon"><Activity size={23} /></div><h2>No sessions yet</h2><p className="muted">Start your first session from Learn.</p></section>}<div className="history-columns"><section className="panel"><p className="eyebrow">Recommendations</p><h3>Next best concepts</h3>{recommendations.length ? recommendations.map((item, index) => <div className="insight-item" key={item.concept_id || index}><div><strong>{item.topic_name || item.topic || item.concept_name}</strong><small>{item.reason || 'Suggested by your learning signals.'}</small></div><b><ArrowUpRight size={15} /></b></div>) : <EmptyState icon={Sparkles} title="No recommendations yet" text="Complete a session to refresh your recommendations." />}</section><section className="panel"><p className="eyebrow">Tutor history</p><h3>Recent interactions</h3>{interactions.length ? interactions.slice(0, 5).map((item) => <div className="insight-item" key={item.interaction_id}><div><strong>{item.concept?.topic_name || 'Tutor interaction'}</strong><small>{item.diagnosis || 'Reviewed'} · {item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}</small></div></div>) : <EmptyState icon={BookOpen} title="No tutor history yet" text="Your Socratic interactions will appear here." />}</section></div></>;
}
function FacultyDataPage({ page, setPage }) {
  const [state, setState] = useState({ loading: true, data: null, error: '' });
  const [query, setQuery] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  useEffect(() => {
    const request = page.startsWith('student:') ? Promise.all([facultyApi.student(page.slice(8)), facultyApi.studentRisk(page.slice(8)), facultyApi.riskHistory(page.slice(8))]) : page === 'students' ? facultyApi.atRisk(100) : page === 'insights' ? Promise.all([facultyApi.weakConcepts(20), facultyApi.misconceptions(20)]) : facultyApi.interventions(100);
    request.then((result) => setState({ loading: false, data: Array.isArray(result) ? result.map((item) => unwrap(item.data)) : unwrap(result.data), error: '' })).catch((e) => setState({ loading: false, data: null, error: e.response?.data?.detail || `Could not load ${page}.` }));
  }, [page]);
  if (state.error) return <Notice text={state.error} />;
  if (state.loading) return <LoadingScreen text={`Loading ${page === 'students' ? 'at-risk students' : page}...`} />;
  if (page.startsWith('student:')) return <FacultyStudentDetail data={state.data} />;
  if (page === 'students') { const students = state.data?.students || []; const filteredStudents = students.filter((student) => { const matchesText = [student.display_name, student.student_code, student.program_stream].some((value) => String(value || '').toLowerCase().includes(query.toLowerCase())); return matchesText && (riskFilter === 'ALL' || student.risk_tier === riskFilter); }); return <div className="data-page"><div className="welcome-row"><div><p className="eyebrow">At-risk students</p><h2>A focused roster for timely support.</h2><p className="muted">Risk results are shown only after backend evaluation.</p></div><div className="roster-tools"><label className="search-field"><Search size={16} /><input aria-label="Search students" placeholder="Search name, code, or program" value={query} onChange={(e) => setQuery(e.target.value)} /></label><select aria-label="Filter by risk tier" value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)}><option value="ALL">All risk tiers</option><option value="MODERATE">Moderate</option><option value="CRITICAL">Critical</option></select></div></div>{students.length ? <div className="panel table-panel"><div className="table-wrap"><table><thead><tr><th>Student</th><th>Program</th><th>Risk</th><th>Predictive factor</th><th>Evaluated</th></tr></thead><tbody>{filteredStudents.map((student) => <tr className="clickable-row" onClick={() => setPage(`student:${student.student_code}`)} key={student.student_id}><td><strong>{student.display_name}</strong><small>{student.student_code}</small></td><td>{student.program_stream || '—'}</td><td><span className={`risk-pill ${student.risk_tier?.toLowerCase()}`}>{student.risk_tier} · {student.risk_percentage}%</span></td><td>{student.top_factor || '—'}</td><td>{student.evaluated_at ? new Date(student.evaluated_at).toLocaleDateString() : '—'}</td></tr>)}</tbody></table>{!filteredStudents.length && <div className="empty-inline">No students match these filters.</div>}</div></div> : <EmptyState icon={Users} title="No evaluated at-risk students" text="Run evaluation from the overview, then refresh this roster." />}</div>; }
  if (page === 'insights') { const weak = state.data?.[0]?.concepts || []; const misconceptions = state.data?.[1]?.misconceptions || []; return <div className="data-page"><div className="welcome-row"><div><p className="eyebrow">Learning insights</p><h2>Patterns worth a closer look.</h2><p className="muted">These rankings are calculated from faculty learning activity.</p></div></div><div className="insight-grid"><section className="panel"><p className="eyebrow">Weak concepts</p><h3>Lowest average mastery</h3>{weak.length ? weak.map((item) => <div className="bar-row" key={item.concept_id}><span>{item.topic_name}</span><div className="bar-track"><div className="bar-fill" style={{ width: `${Math.min(100, item.avg_mastery * 100 || 0)}%` }} /></div><strong>{formatNumber(item.avg_mastery == null ? null : item.avg_mastery * 100, '%')}</strong></div>) : <EmptyState icon={BarChart3} title="No weak-concept data" text="Learning activity will appear here after students complete sessions." />}</section><section className="panel"><p className="eyebrow">Misconceptions</p><h3>Most frequent diagnoses</h3>{misconceptions.length ? misconceptions.map((item) => <div className="insight-item" key={`${item.concept_id}-${item.diagnosis}`}><div><strong>{item.diagnosis}</strong><small>{item.topic_name}</small></div><b>{item.occurrences}</b></div>) : <EmptyState icon={CircleHelp} title="No misconception data" text="Tutor diagnoses will be ranked here." />}</section></div></div>; }
  const interventions = state.data?.interventions || []; return <div className="data-page"><div className="welcome-row"><div><p className="eyebrow">Interventions</p><h2>Turn signals into support.</h2><p className="muted">Pending review tasks from the backend intervention queue.</p></div></div>{interventions.length ? <div className="intervention-list">{interventions.map((item) => <InterventionCard item={item} key={item.task_id} />)}</div> : <EmptyState icon={ShieldCheck} title="No pending interventions" text="New intervention tasks will appear after risk evaluation." />}</div>;
}

function InterventionCard({ item }) {
  const [status, setStatus] = useState(item.status);
  const [busy, setBusy] = useState(false);
  const update = async (approve) => { if (!window.confirm(`${approve ? 'Approve' : 'Reject'} this intervention?`)) return; setBusy(true); try { const { data } = await (approve ? facultyApi.approveIntervention(item.task_id) : facultyApi.rejectIntervention(item.task_id)); setStatus(data.status); } finally { setBusy(false); } };
  return <section className="panel intervention"><div className="panel-heading"><div><p className="eyebrow">{item.risk_tier} · {item.risk_percentage}% risk</p><h3>{item.display_name} <small>{item.student_code}</small></h3></div><span className="tag">{status}</span></div><div className="intervention-details"><div><span>Route</span><strong>{displayValue(item.route)}</strong></div><div><span>Plan</span><strong>{displayValue(item.plan)}</strong></div></div>{item.outreach_message && <p className="muted">{displayValue(item.outreach_message)}</p>}{status === 'PENDING_REVIEW' && <div className="intervention-actions"><button className="button secondary small" disabled={busy} onClick={() => update(false)}>Reject</button><button className="button primary small" disabled={busy} onClick={() => update(true)}>Approve</button></div>}</section>;
}

function FacultyStudentDetail({ data }) {
  const combined = data?.[0] || {}; const riskData = data?.[1] || {}; const history = data?.[2]?.history || []; const student = combined.student || {}; const risk = combined.risk || riskData.risk || {}; const mastery = combined.mastery?.concepts || combined.concepts || [];
  return <><div className="welcome-row"><div><p className="eyebrow">Faculty student detail</p><h2>{student.display_name || riskData.display_name || 'Student profile'}</h2><p className="muted">{student.student_code || riskData.student_code || '—'} · {student.program_stream || '—'}</p></div><span className={`risk-pill ${risk.risk_tier?.toLowerCase()}`}>{risk.risk_tier || 'NOT EVALUATED'} {risk.risk_percentage == null ? '' : `· ${risk.risk_percentage}%`}</span></div><div className="detail-grid"><section className="panel"><p className="eyebrow">Top Predictive Risk Factors</p>{risk.top_risk_factors?.length ? risk.top_risk_factors.map((factor, index) => <div className="insight-item" key={factor.factor || index}><div><strong>{displayValue(factor.factor)}</strong><small>Predictive driver</small></div><b>{displayValue(factor.contribution_percentage)}%</b></div>) : <EmptyState icon={ShieldCheck} title="No predictive factors" text="Risk factors appear after evaluation." />}</section><section className="panel"><div className="section-heading"><div><p className="eyebrow">Risk history</p><h3>Evaluation snapshots</h3></div></div>{history.length ? <div className="chart-wrap"><ResponsiveContainer width="100%" height={220}><LineChart data={history}><XAxis dataKey="week_start_date" /><YAxis domain={[0, 100]} unit="%" /><Tooltip /><Line type="monotone" dataKey="risk_percentage" stroke="#c94e4e" strokeWidth={3} /></LineChart></ResponsiveContainer></div> : <EmptyState icon={Activity} title="No risk history" text="Evaluate this student to create a snapshot." />}</section></div><section className="panel"><p className="eyebrow">Mastery by concept</p>{mastery.length ? <div className="mastery-grid">{mastery.map((item) => <div className="mastery-card" key={item.concept_id}><h3>{item.topic_name || item.concept_name}</h3><div className="mastery-track"><div style={{ width: `${item.mastery_percentage || 0}%` }} /></div><strong>{item.mastery_percentage ?? 0}%</strong></div>)}</div> : <EmptyState icon={Target} title="No mastery data" text="This student's learning activity will appear here." />}</section></>;
}
function AdminPlaceholder({ page }) { return <section className="panel empty-page"><div className="empty-icon"><Settings size={23} /></div><p className="eyebrow">{page}</p><h2>System workspace</h2><p className="muted">Admin controls stay behind the authenticated backend. User management is ready for the exact deployed payloads.</p></section>; }

function AdminUsers() {
  const [state, setState] = useState({ loading: true, users: [], error: '' });
  const [form, setForm] = useState({ email: '', password: '', display_name: '', role: 'STUDENT', student_code: '' });
  const [message, setMessage] = useState('');
  const load = () => { setState((current) => ({ ...current, loading: true, error: '' })); adminApi.users().then(({ data }) => setState({ loading: false, users: unwrap(data)?.users || [], error: '' })).catch((e) => setState({ loading: false, users: [], error: e.response?.data?.detail || 'The backend user-list endpoint is not available yet.' })); };
  useEffect(load, []);
  const create = async (event) => { event.preventDefault(); setMessage(''); try { await adminApi.createUser({ ...form, student_code: form.role === 'STUDENT' ? form.student_code : null }); setMessage('User created successfully.'); setForm({ email: '', password: '', display_name: '', role: 'STUDENT', student_code: '' }); load(); } catch (e) { setMessage(e.response?.data?.detail || 'Could not create user.'); } };
  const toggle = async (user) => { try { await adminApi.setUserStatus(user.user_id, !user.is_active); setState((current) => ({ ...current, users: current.users.map((item) => item.user_id === user.user_id ? { ...item, is_active: !user.is_active } : item) })); } catch (e) { setMessage(e.response?.data?.detail || 'Could not update user status.'); } };
  return <><div className="welcome-row"><div><p className="eyebrow">Admin</p><h2>Manage workspace access.</h2><p className="muted">Create accounts and keep institutional access current.</p></div></div><div className="admin-grid"><section className="panel"><p className="eyebrow">Create user</p><h3>New account</h3><form className="admin-form" onSubmit={create}><label>Display name<input required value={form.display_name} onChange={(e) => setForm({ ...form, display_name: e.target.value })} /></label><label>Email<input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label><label>Password<input required minLength="8" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label><label>Role<select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}><option>STUDENT</option><option>FACULTY</option><option>ADMIN</option></select></label>{form.role === 'STUDENT' && <label>Student code<input required value={form.student_code} onChange={(e) => setForm({ ...form, student_code: e.target.value })} /></label>}<button className="button primary">Create user</button>{message && <p className="field-hint">{message}</p>}</form></section><section className="panel"><div className="section-heading"><div><p className="eyebrow">Directory</p><h3>Users</h3></div><button className="button secondary small" onClick={load}>Refresh</button></div>{state.loading ? <LoadingScreen text="Loading users..." /> : state.error ? <Notice text={state.error} /> : state.users.length ? <div className="table-wrap"><table><thead><tr><th>User</th><th>Role</th><th>Status</th><th>Action</th></tr></thead><tbody>{state.users.map((user) => <tr key={user.user_id}><td><strong>{user.display_name}</strong><small>{user.email}</small></td><td>{user.role}</td><td>{user.is_active ? 'Active' : 'Inactive'}</td><td><button className="text-button" onClick={() => toggle(user)}>{user.is_active ? 'Deactivate' : 'Activate'}</button></td></tr>)}</tbody></table></div> : <EmptyState icon={Users} title="No users returned" text="Create an account to populate the directory." />}</section></div></>;
}

function LoadingScreen({ text = 'Loading workspace...' }) { return <section className="loading-screen"><div className="loader" /><strong>{text}</strong><span>Fetching the latest backend data</span></section>; }
function LoadingOverlay({ text }) { return <div className="loading-overlay"><div className="loading-card"><div className="loader" /><strong>{text}</strong><span>This may take a moment while the backend evaluates students.</span></div></div>; }

createRoot(document.getElementById('root')).render(<App />);
