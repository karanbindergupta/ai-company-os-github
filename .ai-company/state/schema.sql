-- AI Company OS - company state database
-- Human-readable artifacts live in .ai-company/**.md; this is the machine-readable half.
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, applied TEXT NOT NULL);

-- ORGANIZATION ------------------------------------------------------------
-- Least-privilege tool policy. Read by readiness_audit, capability_validation,
-- matrices.py. Was created ad hoc during an early build phase and never captured
-- here, so a clean checkout failed with "no such table: permission_policy".
CREATE TABLE IF NOT EXISTS permission_policy(
  family TEXT NOT NULL, tools TEXT NOT NULL, grant_type TEXT NOT NULL,
  PRIMARY KEY(family, tools));

CREATE TABLE IF NOT EXISTS departments (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, lead TEXT, charter TEXT);

CREATE TABLE IF NOT EXISTS agents (          -- roles are the company's employees
  id TEXT PRIMARY KEY,                       -- role slug
  department TEXT NOT NULL REFERENCES departments(id),
  title TEXT NOT NULL, reports_to TEXT, seniority TEXT NOT NULL,
  authority_level INTEGER NOT NULL,          -- 0 founder .. 4 specialist
  artifact TEXT, pack_path TEXT, status TEXT NOT NULL DEFAULT 'active',
  -- Cognitive architecture (CLAUDE.md section 7). Added ad hoc in an early phase
  -- and never captured here, so a clean checkout failed with
  -- "no such column: cognitive_style". Values are loaded from seed.sql.
  name TEXT, strengths TEXT, weaknesses TEXT, reliability TEXT,
  cognitive_profile TEXT, backup_for TEXT, last_active TEXT,
  cognitive_style TEXT, cog_strengths TEXT, blind_spots TEXT, instincts TEXT,
  decision_philosophy TEXT, risk_profile TEXT, evidence_threshold TEXT,
  debate_style TEXT, pressure_behavior TEXT, failure_behavior TEXT,
  counterbalanced_by TEXT, maturity_level INTEGER);

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

-- ---------------------------------------------------------------------------
-- APPENDED: base tables proven REQUIRED by the source audit (/tmp/inventory.json).
-- Each is referenced by at least one Company OS script; without it that script
-- fails on a clean checkout. Six further live tables (behavioral_baselines,
-- benchmarks, demonstrations, development_plans, environment_changes, sops) were
-- DELIBERATELY EXCLUDED: they exist in the live database from an earlier phase but
-- have ZERO code references. They are dead schema and are not enshrined here. A clean-checkout test proved their absence broke bootstrap
-- (behavioral_contracts, drills, provider_usage and others).
-- Copied verbatim from the live schema. Nothing above this line was modified.
-- Harness tables are deliberately NOT here: migrations in scripts/harness.py own them.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS behavioral_contracts(
  agent TEXT PRIMARY KEY REFERENCES agents(id), profile_version TEXT,
  professional_mission TEXT, core_behaviors TEXT, decision_behaviors TEXT,
  evidence_behaviors TEXT, communication_behaviors TEXT, collaboration_behaviors TEXT,
  disagreement_behaviors TEXT, escalation_behaviors TEXT, pressure_behaviors TEXT,
  failure_behaviors TEXT, learning_behaviors TEXT, quality_behaviors TEXT,
  authority_behaviors TEXT, risk_behaviors TEXT, business_behaviors TEXT,
  prohibited_behaviors TEXT, anti_patterns TEXT, success_indicators TEXT,
  measurable_outcomes TEXT, drills TEXT, regression_tests TEXT,
  review_cadence TEXT, created TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS behavioral_regressions(
  id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT NOT NULL,
  improved_dimension TEXT, improved_from REAL, improved_to REAL,
  regressed_dimension TEXT NOT NULL, regressed_from REAL, regressed_to REAL,
  severity TEXT, note TEXT, status TEXT DEFAULT 'open', detected TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS capability_readiness(
  name TEXT PRIMARY KEY, category TEXT NOT NULL, configured INTEGER DEFAULT 0,
  credentialed INTEGER DEFAULT 0, reachable INTEGER DEFAULT 0, executable INTEGER DEFAULT 0,
  observable INTEGER DEFAULT 0, inspectable INTEGER DEFAULT 0, machine_readable INTEGER DEFAULT 0,
  trusted_as_gate INTEGER DEFAULT 0, status TEXT NOT NULL, rag TEXT NOT NULL,
  evidence TEXT, budget TEXT, fallback TEXT, remediation TEXT, last_probed TEXT,
  CHECK (rag IN ('GREEN','YELLOW','RED','GRAY')));

CREATE TABLE IF NOT EXISTS ci_runs(
  id TEXT PRIMARY KEY, commit_sha TEXT, branch TEXT, workflow TEXT, trigger TEXT,
  status TEXT NOT NULL, started TEXT, finished TEXT, duration_s REAL,
  jobs_json TEXT, failure_reason TEXT, artifacts TEXT, observed INTEGER DEFAULT 0,
  CHECK (status IN ('PASS','FAIL','CANCELLED','SKIPPED','UNAVAILABLE','UNKNOWN')));

CREATE TABLE IF NOT EXISTS coaching(
  id INTEGER PRIMARY KEY AUTOINCREMENT, drill_run TEXT REFERENCES drill_runs(id),
  agent TEXT NOT NULL, failed_behavior TEXT NOT NULL, observed_evidence TEXT,
  expected_behavior TEXT, likely_cause TEXT NOT NULL, coaching_instruction TEXT NOT NULL,
  targeted_exercise TEXT, retest_drill TEXT, applied INTEGER DEFAULT 0,
  retest_run TEXT, improvement REAL, created TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS cognitive_panels(
  id TEXT PRIMARY KEY, decision TEXT, question TEXT NOT NULL, members TEXT NOT NULL,
  independent_until TEXT, consensus TEXT, disagreements TEXT, uncertainties TEXT,
  missing_evidence TEXT, status TEXT NOT NULL DEFAULT 'open', created TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS decision_quality(
  decision TEXT PRIMARY KEY, evidence_quality INTEGER, reasoning_quality INTEGER,
  assumption_quality INTEGER, downside_awareness INTEGER, upside_analysis INTEGER,
  reversibility_assessed INTEGER, strategic_alignment INTEGER, customer_impact INTEGER,
  financial_impact INTEGER, technical_impact INTEGER, security_impact INTEGER,
  confidence_calibration INTEGER, scored_by TEXT, scored_at TEXT, note TEXT);

CREATE TABLE IF NOT EXISTS drift_alerts(
  id TEXT PRIMARY KEY, agent TEXT NOT NULL REFERENCES agents(id), dimension TEXT NOT NULL,
  declared TEXT, observed TEXT, evidence TEXT, frequency INTEGER, confidence TEXT,
  severity TEXT NOT NULL, possible_causes TEXT, recommended_investigation TEXT,
  status TEXT NOT NULL DEFAULT 'open', profile_changed INTEGER NOT NULL DEFAULT 0,
  created TEXT NOT NULL,
  CHECK (severity IN ('INFO','MINOR','MODERATE','MAJOR','CRITICAL')));

CREATE TABLE IF NOT EXISTS drift_observations(
  id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL, pattern TEXT NOT NULL,
  evidence TEXT, severity TEXT, recalibration TEXT, status TEXT DEFAULT 'open', recorded TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS drill_runs(
  id TEXT PRIMARY KEY, drill TEXT NOT NULL REFERENCES drills(id),
  agent TEXT NOT NULL REFERENCES agents(id), response TEXT, observed_behaviors TEXT,
  anti_patterns_observed TEXT, score REAL, verdict TEXT NOT NULL,
  evaluator TEXT NOT NULL, evaluator_independent INTEGER DEFAULT 0, method TEXT,
  strengths TEXT, weaknesses TEXT, confidence TEXT, feedback TEXT,
  corrective_action TEXT, retest_required INTEGER DEFAULT 0, baseline_for TEXT,
  created TEXT NOT NULL, CHECK (verdict IN ('PASS','FAIL','PARTIAL','INCONCLUSIVE')));

CREATE TABLE IF NOT EXISTS drills(
  id TEXT PRIMARY KEY, category TEXT NOT NULL, role TEXT, capability TEXT,
  behavioral_target TEXT NOT NULL, difficulty TEXT, scenario TEXT NOT NULL, context TEXT,
  evidence TEXT, constraints TEXT, pressure_level TEXT, expected_behaviors TEXT NOT NULL,
  anti_patterns TEXT NOT NULL, rubric TEXT NOT NULL, pass_criteria TEXT NOT NULL,
  fail_criteria TEXT, version TEXT NOT NULL DEFAULT '1.0', created TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS evaluation_dimensions(
  evaluation TEXT NOT NULL REFERENCES evaluations(id), dimension TEXT NOT NULL,
  score REAL, evidence TEXT, confidence TEXT, sample_size INTEGER,
  trend TEXT, limitations TEXT, PRIMARY KEY(evaluation,dimension));

CREATE TABLE IF NOT EXISTS evaluations(
  id TEXT PRIMARY KEY, agent TEXT NOT NULL REFERENCES agents(id), role TEXT, department TEXT,
  profile_version TEXT, scenario TEXT, objective TEXT, difficulty TEXT, context TEXT,
  constraints TEXT, evidence_available TEXT, expected_competencies TEXT,
  authority_boundaries TEXT, tools_available TEXT, pressure_conditions TEXT,
  agent_response TEXT, decision TEXT, assumptions TEXT, confidence TEXT, evidence_used TEXT,
  risks_identified TEXT, dissent TEXT, escalation_behavior TEXT, outcome TEXT,
  evaluator TEXT NOT NULL, evaluator_independent INTEGER NOT NULL DEFAULT 0,
  evaluation_method TEXT, score REAL, weaknesses TEXT, strengths TEXT, lessons TEXT,
  eval_type TEXT, model_version TEXT, tool_environment TEXT, reproducibility TEXT,
  created TEXT NOT NULL,
  CHECK (eval_type IN ('controlled','adversarial','collaborative','failure','pressure','real_work')));

CREATE TABLE IF NOT EXISTS lessons(
  id TEXT PRIMARY KEY, source TEXT, context TEXT, expected_behavior TEXT,
  actual_behavior TEXT, outcome TEXT, root_cause TEXT, lesson TEXT NOT NULL,
  confidence TEXT, applicability TEXT, affected_roles TEXT, affected_playbooks TEXT,
  affected_agents TEXT, observation_count INTEGER NOT NULL DEFAULT 1,
  independent_confirmations INTEGER NOT NULL DEFAULT 0,
  successful_applications INTEGER NOT NULL DEFAULT 0,
  validation_status TEXT NOT NULL DEFAULT 'OBSERVATION', reviewer TEXT, created TEXT NOT NULL,
  CHECK (validation_status IN ('OBSERVATION','HYPOTHESIS','VALIDATED_LESSON','ESTABLISHED_PRACTICE')));

CREATE TABLE IF NOT EXISTS maturity_assessments(
  id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT NOT NULL REFERENCES agents(id),
  current_level TEXT, proposed_level TEXT, verdict TEXT NOT NULL,
  evaluated_assignments INTEGER, decision_quality REAL, consistency REAL,
  failure_handling REAL, authority_violations INTEGER, evidence_calibration REAL,
  independent_reviews INTEGER, learning_events INTEGER, sample_size INTEGER,
  rationale TEXT, assessed_by TEXT, assessed_at TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS playbook_coverage(
  capability TEXT PRIMARY KEY, canonical_owner TEXT NOT NULL, supporting TEXT,
  shared_playbooks TEXT, unique_procedures TEXT, authority TEXT, escalation TEXT,
  reuse_evidence TEXT, ambiguity_reports INTEGER DEFAULT 0, duplication_risk TEXT,
  recommendation TEXT NOT NULL DEFAULT 'keep_shared');

CREATE TABLE IF NOT EXISTS profile_changes(
  id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT NOT NULL REFERENCES agents(id),
  field TEXT NOT NULL, old_value TEXT, proposed_value TEXT, evidence TEXT,
  observations INTEGER, confidence TEXT, reason TEXT, reviewer TEXT,
  approved INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS provider_usage(
  id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, requested_provider TEXT NOT NULL,
  actual_provider TEXT NOT NULL, fallback_reason TEXT, research_quality TEXT,
  evidence TEXT, recorded TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS team_formations(
  id TEXT PRIMARY KEY, objective TEXT NOT NULL, capabilities TEXT, members TEXT NOT NULL,
  reviewers TEXT, executive TEXT, risk TEXT, status TEXT NOT NULL DEFAULT 'active',
  created TEXT NOT NULL, dissolved TEXT);

-- ---------------------------------------------------------------------------
-- Reconciled from the public snapshot (karanbindergupta/ai-company-os-github
-- @3a4c1bf) during repository canonicalization, 2026-09-09.
--
-- These six were previously omitted as "dead tables". That call was WRONG:
--   * benchmarks holds 7 rows of AUTHORED CONFIGURATION (scenario + rubric),
--     which a clean install was silently losing. It is seeded in seed.sql.
--   * environment_changes holds a RUNTIME OBSERVATION. Declared here, never
--     seeded - seeding it would fabricate measurement evidence.
--   * the remaining four are empty but are part of the declared architecture,
--     and omitting them left a fresh install at 47 tables against 54 for an
--     existing one. That drift is the exact defect this file exists to prevent.
--
-- sqlite_sequence is deliberately NOT declared: SQLite creates and maintains it
-- automatically for AUTOINCREMENT tables. Declaring it forces callers to
-- special-case it during replay (the public snapshot had to do exactly that).
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS behavioral_baselines(
  agent TEXT NOT NULL, dimension TEXT NOT NULL, score REAL NOT NULL,
  sample INTEGER NOT NULL, recorded TEXT NOT NULL, PRIMARY KEY(agent,dimension,recorded));

CREATE TABLE IF NOT EXISTS benchmarks(
  id TEXT PRIMARY KEY, category TEXT NOT NULL, version TEXT NOT NULL, title TEXT NOT NULL,
  scenario TEXT NOT NULL, rubric TEXT NOT NULL, target_roles TEXT, difficulty TEXT,
  leaked INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS demonstrations(
  id TEXT PRIMARY KEY, pattern TEXT NOT NULL, quality TEXT NOT NULL,
  example TEXT NOT NULL, why TEXT, CHECK (quality IN ('GOOD','BAD','AMBIGUOUS','EDGE_CASE')));

CREATE TABLE IF NOT EXISTS development_plans(
  agent TEXT PRIMARY KEY REFERENCES agents(id), strengths TEXT, weaknesses TEXT,
  behavioral_targets TEXT, drills_completed INTEGER DEFAULT 0, drills_failed INTEGER DEFAULT 0,
  trend TEXT, unresolved TEXT, recommended_assignments TEXT, counterbalancing TEXT,
  next_evaluation TEXT, drill_frequency TEXT DEFAULT 'normal', updated TEXT);

CREATE TABLE IF NOT EXISTS environment_changes(
  id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT, change_type TEXT NOT NULL,
  detail TEXT, before_score REAL, after_score REAL, sample_before INTEGER,
  sample_after INTEGER, verdict TEXT, recorded TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS sops(
  id TEXT PRIMARY KEY, name TEXT NOT NULL, purpose TEXT, owner TEXT, inputs TEXT,
  steps TEXT, decision_points TEXT, tools TEXT, outputs TEXT, quality_standard TEXT,
  failure_modes TEXT, escalation TEXT, metrics TEXT, review_date TEXT, created TEXT NOT NULL);
