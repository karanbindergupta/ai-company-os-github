-- AI Company OS - company state database
-- Human-readable artifacts live in .ai-company/**.md; this is the machine-readable half.
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, applied TEXT NOT NULL);

-- ORGANIZATION ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS departments (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, lead TEXT, charter TEXT);

CREATE TABLE IF NOT EXISTS agents (          -- roles are the company's employees
  id TEXT PRIMARY KEY,                       -- role slug
  department TEXT NOT NULL REFERENCES departments(id),
  title TEXT NOT NULL, reports_to TEXT, seniority TEXT NOT NULL,
  authority_level INTEGER NOT NULL,          -- 0 founder .. 4 specialist
  artifact TEXT, pack_path TEXT, status TEXT NOT NULL DEFAULT 'active');

-- AUTHORITY ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS decision_rights (
  domain TEXT PRIMARY KEY,                   -- e.g. 'technical_architecture'
  owner TEXT NOT NULL REFERENCES agents(id),
  reviewers TEXT NOT NULL,                   -- comma-separated role ids
  veto_holders TEXT NOT NULL DEFAULT '',
  founder_required INTEGER NOT NULL DEFAULT 0,
  escalation_level INTEGER NOT NULL DEFAULT 3);

CREATE TABLE IF NOT EXISTS tool_permissions (
  role TEXT NOT NULL REFERENCES agents(id), tool TEXT NOT NULL,
  grant_type TEXT NOT NULL DEFAULT 'allow',  -- allow | confirm | deny
  PRIMARY KEY (role, tool));

-- WORK --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active',
  objective TEXT, created TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  parent TEXT REFERENCES tasks(id),          -- project>epic>feature>task>subtask
  kind TEXT NOT NULL DEFAULT 'task',
  project TEXT REFERENCES projects(id),
  title TEXT NOT NULL, owner TEXT NOT NULL REFERENCES agents(id),
  reviewer TEXT REFERENCES agents(id),       -- separation of duties: != owner
  department TEXT, objective TEXT, inputs TEXT, outputs TEXT,
  acceptance TEXT NOT NULL DEFAULT '', priority INTEGER NOT NULL DEFAULT 3,
  risk TEXT NOT NULL DEFAULT 'low', phase TEXT,
  status TEXT NOT NULL DEFAULT 'todo',
  parallel_group TEXT, attempts INTEGER NOT NULL DEFAULT 0,
  evidence TEXT NOT NULL DEFAULT '', blocked_on TEXT,
  created TEXT NOT NULL, updated TEXT NOT NULL,
  CHECK (status IN ('todo','in_progress','blocked','failed','review','done','cancelled','accepted_risk')),
  CHECK (owner <> COALESCE(reviewer,'~')));  -- an agent may never review its own work

CREATE TABLE IF NOT EXISTS task_deps (
  task TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  depends_on TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  PRIMARY KEY (task, depends_on), CHECK (task <> depends_on));

CREATE TABLE IF NOT EXISTS handoffs (        -- structured agent-to-agent handoff
  id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT REFERENCES tasks(id),
  from_role TEXT NOT NULL, to_role TEXT NOT NULL, context TEXT,
  work_done TEXT, evidence TEXT, artifacts TEXT, decisions TEXT,
  open_questions TEXT, risks TEXT, next_action TEXT, acceptance TEXT,
  created TEXT NOT NULL);

-- DECISIONS ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS decisions (
  id TEXT PRIMARY KEY, date TEXT NOT NULL, domain TEXT, title TEXT NOT NULL,
  problem TEXT, context TEXT, options TEXT, args_for TEXT, args_against TEXT,
  risks TEXT, financial_impact TEXT, technical_impact TEXT, product_impact TEXT,
  customer_impact TEXT, rejected TEXT, decision TEXT,
  owner TEXT NOT NULL REFERENCES agents(id), approvers TEXT NOT NULL DEFAULT '',
  confidence TEXT NOT NULL DEFAULT 'MEDIUM',
  status TEXT NOT NULL DEFAULT 'proposed',
  review_date TEXT, outcome TEXT,
  CHECK (status IN ('proposed','under_review','decided','vetoed','superseded','revisited')));

CREATE TABLE IF NOT EXISTS dissent (         -- minority opinions are preserved verbatim
  id INTEGER PRIMARY KEY AUTOINCREMENT, decision TEXT NOT NULL REFERENCES decisions(id),
  role TEXT NOT NULL, position TEXT NOT NULL, argument TEXT NOT NULL, created TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS decision_evidence (
  decision TEXT NOT NULL REFERENCES decisions(id),
  research TEXT NOT NULL, PRIMARY KEY (decision, research));

CREATE TABLE IF NOT EXISTS vetoes (
  id TEXT PRIMARY KEY, target_type TEXT NOT NULL, target TEXT NOT NULL,
  role TEXT NOT NULL REFERENCES agents(id), domain TEXT NOT NULL,
  reason TEXT NOT NULL, evidence TEXT NOT NULL, severity TEXT NOT NULL,
  remediation TEXT NOT NULL, lift_conditions TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active', created TEXT NOT NULL, lifted TEXT,
  CHECK (severity IN ('low','medium','high','critical')),
  CHECK (status IN ('active','lifted','overridden')));

-- INTELLIGENCE ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS research (
  id TEXT PRIMARY KEY, query TEXT NOT NULL, level INTEGER NOT NULL DEFAULT 2,
  engines TEXT, findings TEXT, confidence TEXT NOT NULL DEFAULT 'MEDIUM',
  volatility TEXT NOT NULL DEFAULT 'MEDIUM', retrieved TEXT NOT NULL,
  refresh_after TEXT, auditor TEXT, audit_verdict TEXT, artifact TEXT);

CREATE TABLE IF NOT EXISTS evidence (
  id TEXT PRIMARY KEY, research TEXT REFERENCES research(id),
  claim TEXT NOT NULL, claim_type TEXT NOT NULL DEFAULT 'FACT',
  source TEXT, source_tier INTEGER, source_url TEXT,
  date_published TEXT, date_accessed TEXT NOT NULL,
  confidence TEXT NOT NULL DEFAULT 'MEDIUM',
  independent_confirmation TEXT, contradicting TEXT,
  CHECK (claim_type IN ('FACT','INFERENCE','HYPOTHESIS','ASSUMPTION','UNKNOWN')));

CREATE TABLE IF NOT EXISTS memory (
  id TEXT PRIMARY KEY, tier TEXT NOT NULL, topic TEXT NOT NULL, content TEXT NOT NULL,
  owner TEXT, source TEXT, created TEXT NOT NULL, updated TEXT NOT NULL,
  expires TEXT, review_after TEXT, version INTEGER NOT NULL DEFAULT 1,
  CHECK (tier IN ('permanent','longterm','working','ephemeral')));

CREATE TABLE IF NOT EXISTS knowledge_edges (  -- the company knowledge graph
  src_type TEXT NOT NULL, src TEXT NOT NULL, relation TEXT NOT NULL,
  dst_type TEXT NOT NULL, dst TEXT NOT NULL,
  PRIMARY KEY (src_type, src, relation, dst_type, dst));

-- RISK / QUALITY / DELIVERY ----------------------------------------------
CREATE TABLE IF NOT EXISTS risks (
  id TEXT PRIMARY KEY, description TEXT NOT NULL, category TEXT,
  probability TEXT NOT NULL, impact TEXT NOT NULL, severity TEXT NOT NULL,
  owner TEXT NOT NULL REFERENCES agents(id), evidence TEXT,
  mitigation TEXT, contingency TEXT, status TEXT NOT NULL DEFAULT 'open',
  accepted_by TEXT, created TEXT NOT NULL, review_date TEXT);

CREATE TABLE IF NOT EXISTS bugs (
  id TEXT PRIMARY KEY, title TEXT NOT NULL, severity TEXT NOT NULL,
  owner TEXT REFERENCES agents(id), reproduction TEXT, root_cause TEXT,
  status TEXT NOT NULL DEFAULT 'open', regression_test TEXT,
  verified_by TEXT, created TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS experiments (
  id TEXT PRIMARY KEY, hypothesis TEXT NOT NULL, metric TEXT NOT NULL,
  threshold TEXT, owner TEXT REFERENCES agents(id),
  status TEXT NOT NULL DEFAULT 'designed', result TEXT, learning TEXT,
  decision TEXT REFERENCES decisions(id), created TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS incidents (
  id TEXT PRIMARY KEY, title TEXT NOT NULL, severity TEXT NOT NULL,
  owner TEXT, detection TEXT, diagnosis TEXT, containment TEXT, fix TEXT,
  verification TEXT, postmortem TEXT, preventive_action TEXT,
  status TEXT NOT NULL DEFAULT 'open', created TEXT NOT NULL, resolved TEXT);

CREATE TABLE IF NOT EXISTS releases (
  id TEXT PRIMARY KEY, version TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'preparing',
  product_ready INTEGER DEFAULT 0, engineering_ready INTEGER DEFAULT 0,
  qa_passed INTEGER DEFAULT 0, security_passed INTEGER DEFAULT 0,
  performance_ok INTEGER DEFAULT 0, docs_ready INTEGER DEFAULT 0,
  rollback_ready INTEGER DEFAULT 0, founder_approval TEXT,
  created TEXT NOT NULL, released TEXT);

-- MEASUREMENT -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agent_performance (
  id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL REFERENCES agents(id),
  task TEXT, outcome TEXT NOT NULL, rework INTEGER DEFAULT 0,
  review_failed INTEGER DEFAULT 0, escalated INTEGER DEFAULT 0,
  notes TEXT, recorded TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL,
  name TEXT NOT NULL, value TEXT NOT NULL, unit TEXT, recorded TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS integrations (
  name TEXT PRIMARY KEY, purpose TEXT NOT NULL, provider TEXT,
  capabilities TEXT, credentials_required TEXT, agents_allowed TEXT,
  permissions TEXT, security_class TEXT NOT NULL DEFAULT 'internal',
  fallback TEXT, status TEXT NOT NULL DEFAULT 'active');

CREATE TABLE IF NOT EXISTS escalations (
  id TEXT PRIMARY KEY, level INTEGER NOT NULL, subject TEXT NOT NULL,
  raised_by TEXT NOT NULL, recommendation TEXT, evidence TEXT, risks TEXT,
  status TEXT NOT NULL DEFAULT 'open', resolution TEXT,
  created TEXT NOT NULL, resolved TEXT,
  CHECK (level BETWEEN 0 AND 4));

CREATE TABLE IF NOT EXISTS audit_log (       -- every state change is traceable
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, actor TEXT,
  action TEXT NOT NULL, entity_type TEXT, entity TEXT, detail TEXT);

CREATE INDEX IF NOT EXISTS ix_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS ix_tasks_owner ON tasks(owner);
CREATE INDEX IF NOT EXISTS ix_vetoes_status ON vetoes(status);
CREATE INDEX IF NOT EXISTS ix_audit_ts ON audit_log(ts);
