---
name: data-fold
description: Folds heterogeneous information from any sources into a verified, consistent picture.
---

START_data_fold

START_goal
### Goal
Bring the picture to a state where every statement used in conclusions is either verified or explicitly marked unverified, with who will close it and how. The conveyor runs for convergence: the demand registry empties; contradictions are resolved or registered with an owner. The output is a packaged slice of verified data, sufficient for the declared action without returning to raw sources.

The action is the sufficiency anchor: whatever a human builds on the data, it is declared by them, tested at entry and refinable in course; without a declared action the goal is undefined.
END_goal

START_task
### Task
Run the convergence cycle from raw input to sufficiency. The steps are the scope, not the order — the order is executed by the state machine (Working Patterns).

1. Intake: a portion of information of any form is split into units — minimal statements that can be confirmed or refuted independently; digital artifacts are saved to the task directory.
2. Status assignment: each unit gets an origin (source, time, channel; a derivation also gets its supports) and a status changed only by operations.
3. Verification fork: each decision-influencing unit gets one branch — verify myself / ask the source / accept as default labeled whose decision.
4. Demand delta: the registry of open questions is recomputed — closed, remained, born.
5. Packaging: with no blocking questions (blocking = an open question without which the declared action cannot be built), the product is assembled from verified units; disputed, defaults and open go to separate sections.

Input. The cycle is started by a delta: information without status, a question without an answer, or a contradiction. A human message may be of any completeness; the goal and the sufficiency criterion are set by this skill, not by the input. Any participant may start any step — a human demand becomes the input of the corresponding state.

Action. Declared by the human at entry and tested before the cycle runs (state action_check). The approved wording sets the initial composition of the demand registry and unfolds through the question "what must be known to act?"; the original wording stays as task context. A change of the action is human-decided only — self-declared or confirming the executor's proposal; the refined action passes the same test and supersedes the old one with a supersedes edge in the same vector; the registry re-unfolds; verified data is inherited. The action is always singular; a composite decomposes — replacement within the vector or a new task with its own directory.

State. A graph of units, links, operations and demand (form in state_shape); it lives within the task, after it only the product matters. The graph lives in a draft file, not in dialogue: action_check creates data-draft-<slug>.xml at task start with the approved action; every cycle pass rewrites it whole — the current state is always on disk, a dead session loses no graph. One reality, the file is its record. Data from past tasks enters only through regular intake, as new units.
END_task

START_environment
### Environment
Sources differ by access, and each speaks its own language:
- own the goal: decide what is needed, do not know the mechanics;
- know the environment: its facts and structure;
- reachable without dialogue: read or executed.
Routing is by access: goal questions go to the goal owner, environment questions to the one who knows it.

Connectivity:
- channels are multiple and lossy: information arrives by the wrong route and not at once;
- sources answer with delay, off-substance, or silence — silence is data too;
- the environment changes without the conveyor knowing: any check is a snapshot.

The executor is strong at understanding but drifts without external anchors:
- takes its own interpretation for a fact;
- loses marks in a long dialogue.
Therefore anchors live in the state, not in memory.

Economics: a round with a source is expensive; an instrument check is usually cheaper.
END_environment

START_working_patterns
### Working Patterns

The cycle is a state machine. A state holds until its GOAL is met; between dialogue turns the executor returns to the current state by its trigger. Several states active — executed in cycle order, each to its GOAL. Moving forward without the previous state's GOAL met is an error.

START_state_action_check
State action_check — the declared action against the information criterion.
TRIGGER: the task starts; an action is declared or awaits declaration.
ACTION: test whether the action is informational — decided by knowledge: with an empty registry nothing remains to execute (e.g. "understand whether X is possible"); an action requiring execution in the world (e.g. "obtain X") fails the test. An undeclared or failed action is the first blocking question; propose an information wording to the human. On approval create the draft with the action; the original wording stays as task context.
GOAL: the action is informational, human-approved and recorded in the draft. Until then the cycle holds — intake without an approved action collects in the wrong direction.
END_state_action_check

START_state_intake
State intake.
TRIGGER: a portion of information has arrived.
ACTION: split it into units; assign each an origin — source, time, channel; a derivation also gets its supports. An already accepted thesis re-delivered by any channel is not expanded again: the unit stays single, the re-delivery appends another origin and by itself is not independent confirmation — independence comes only from the protocol 4 depth check.
GOAL: no units without origin; the portion remainder stays in the state until fully processed.
END_state_intake

START_state_status_fork
State status_fork — status assignment and fork.
TRIGGER: units have origins but no verification branch.
ACTION: assign each unit a TYPE from the case taxonomy; for each decision-influencing unit choose a branch: verify myself / ask the source / accept as default labeled whose decision.
GOAL: every decision-influencing unit has a branch; branchless units are explicitly deferred with a reason.
END_state_status_fork

START_state_verify
State verify — executing branches.
TRIGGER: a chosen branch is not yet executed.
ACTION: execute the chosen branch — run an instrument check / send the question to the source / record the default with its owner label. Until an answer the branch stays open: the question holds it in the demand registry; execution may span replies and sessions. Silence is data: a re-asked question left unanswered becomes a default owned by the human or a dated question; blocking silence leads to freeze.
GOAL: each unit either received independent confirmation (a confirms edge), or produced a registered question in the demand registry, or is recorded as a labeled default.
END_state_verify

START_state_demand_delta
State demand_delta.
TRIGGER: a registry question closed or a new portion absorbed.
ACTION: recompute the demand registry — closed, remained, born; assign new questions a branch and a closure owner.
GOAL: the registry matches the current picture; no new question stays outside it.
END_state_demand_delta

START_state_package
State package.
TRIGGER: no blocking questions in the registry.
ACTION: run the orphan audit (protocol 13); present readiness to the human — the draft's picture: verified units, defaults, open questions.
GOAL: the human approved the readiness. Until approval the state holds; human edits are accepted as new units and pass the cycle again.
END_state_package

START_state_check
State check — the deterministic gate.
TRIGGER: the readiness is approved by the human.
ACTION: run the checking script load(path="scripts/check_draft.py") on the task directory; fix mechanical findings and show the human a mini-report; repeat until a clean pass.
GOAL: the script passes with no fail findings.
END_state_check

START_state_audit
State audit — independent semantic verification.
TRIGGER: the script has passed clean.
ACTION: launch a subagent in a clean context with the prompt template below; replace the template variables with real paths (<skill-dir> — the installed skill directory, <task-dir> — the task directory .data-folds/data-fold-<slug>/):

    Independent audit. Load and follow the protocol: load(path="<skill-dir>/reference/data-fold-auditor.md"). Subject: load(path="<task-dir>"). Work and report in English; report only, no edits.

Present the received report to the human with your judgment on what must be fixed; the decision is the human's. Fixes pass the cycle; before a re-audit — the check state again.
GOAL: after an audit round the human explicitly decides "assemble".
END_state_audit

START_state_assembly
State assembly.
TRIGGER: the human has decided "assemble".
ACTION: final run of the script — a failure returns to check; then assemble the product from verified units only (as-of units — with a pre-check at assembly time; disputed, defaults and open go to explicit sections) and write the file.
GOAL: the product is assembled and its file written.
END_state_assembly

START_state_freeze
State freeze.
TRIGGER: demand is blocked externally — the source is unavailable, is executing its part, or contradiction resolution is blocked — and no cycle step can advance the picture.
ACTION: record the open questions, who blocks them, what lifts the block; compile a dead-end report; stop the cycle.
GOAL: the dead-end report is handed to the human; the task is frozen with an explicit resume condition.
END_state_freeze

START_protocols
Protocols. A protocol violation is an error, not an acceptable execution variant.

1. Origin is mandatory. Each unit carries source, time and channel; a derivation also its supports. A unit without origin participates in no conclusion and never enters the product. The origin link is resolvable: web — the primary-source URL (fetched content saved as a snapshot artifact, referenced as the URL + path pair); file — a path relative to .data-folds/; spoken remark — channel, person, date; check — instrument and date, reproducible. A name pointing nowhere is a forbidden form.
Rationale: an originless statement looks like a fact and slips into decisions; an origin that cannot be re-read by its link cannot be checked — an unverifiable origin equals no origin.

2. Derived is not fact. A derivation unit does not get "verified" until it receives independent confirmation — a confirms edge from another source or instrument.
Rationale: passing one's own interpretation off as a verified fact is an executor's typical error.

3. The executor's words are units. The executor's statements — spoken and internal inferences — enter the graph through intake on equal terms: origin, supports, status assignment; an internal inference is forbidden to bypass intake. Trust is not implied: decision-influencing material is checked as anyone else's.
Rationale: one's own interpretation is the typical source of a false fact; whatever bypassed the graph is invisible to the protocols.

4. Confirmation reaches for the primary source. A primary source has direct access to the fact (e.g.: a legal text — to the law; an instrument — to the measurement; the declarer — to their intent); a retelling is secondary. Confirmation counts only from a source not below the required depth; sources ascending to one origin are not independent. The required depth grows with the error cost; unmet depth at high cost is a question into the demand registry.
Rationale: a check chain closed on secondary sources produces convergence optics without verification — staleness and error replicate as fact.

5. Data shelf life. A known term — the unit carries a date or range; a live deadline under a live task is a dated registry question. Unknown term — VALIDITY="as-of": such data requires a pre-check on reliance. A known expiry condition — the unit carries the condition; pre-check on reliance or on the condition's signal. Outdated is superseded: status "superseded", the unit remains dated history — not falsehood, not deletion, a supersedes edge from the current one. A conclusion inherits the shortest shelf life of its supports.
Rationale: a check is a snapshot in time; the world changes without the conveyor knowing; confidence without a time label is false.

6. Demotion by error cost. A statement presented as fact, without independent confirmation, with error cost above pause cost, is not used as a basis for conclusions and actions until verified — and is never asserted as fact in any outgoing message: held as a signal, verification is launched.
Rationale: unverified-with-fact-appearance enters decisions from any side — from sources and from the executor itself; a pause is cheaper than an error.

7. Demand delta after every intake and every question closure: closed, remained, born.
Rationale: without recomputation convergence is invisible, and questions born from answers get lost.

8. Closure carries a match verdict. The question's form and the answer's substance are recorded next to the closure; an answer "about something else" does not close the question. A dependent question (depends-on edge) does not close while its support is open.
Rationale: sources regularly answer the neighboring question and demand closes fictitiously; a conditional directive with an unverified premise is not executed.

9. Defaults are labeled. An accepted default carries whose decision it is — the human's or the executor's — and enters the product as the "accepted defaults" section for confirmation. On axes owned by the goal owner, defaults are not set — only a question. Silence counts as acceptance only if explicitly declared at installation.
Rationale: a silent assumption is indistinguishable from a requirement and stays so until a late stage.

10. History changes only by folding. Journal compaction is a summary node with a supersedes edge; originals are never discarded outside operations. The state file is written only by the cycle.
Rationale: a rewritten history breaks statuses without a visible trace.

11. Contradictions are registered. A found contradiction is fixed by a contradicts edge and a demand-registry item with a resolution owner; both sides are kept. Resolution — only by superseding or refuting one side; silently picking a side is forbidden.
Rationale: a contradiction dissolved by omission is a hidden choice without an owner; the next stage receives the appearance of agreement where there is none.

12. The product is built from verified only. Disputed, unverified and open go into explicit product sections, not its body.
Rationale: the product is the trust boundary; the next stage must not have to tell verified from conceivable.

13. Orphan audit before packaging. A unit without origin, a question without an answer, a derivation without supports — detected and processed: close, verify or explicitly leave open.
Rationale: unprocessed tails are the main source of false convergence.
END_protocols

START_guides
Guides. Heuristics with a declared benefit; they speed up but do not replace judgment.

- Taxonomy is minted per case. Unit types are one-two words by the domain's logic, not inherited from past tasks, not built in advance. Benefit: one core for any domain.
- Prioritize streams. Process first what unblocks other participants or carries more dependencies. Benefit: fewer waiting rounds on the critical path.
- Don't ask the verifiable. If a fact is reachable by an instrument — verify first, then ask attaching the fact. Benefit: the question closes in one round.
- Mature the question. First "off-substance" answer — prepare the binary form with a fact and importance axes for the answerer; second — send it. Benefit: a matured question closes at once.
- Don't offer the unconfirmed. A variant whose feasibility is not confirmed is not offered to the human. Benefit: promises never have to be withdrawn.
- Mind the source load. Bundle questions, speak the recipient's language and tone, don't promise the next stage while participants have open questions. Benefit: the source keeps answering.
- Pin the delegation language. A delegated task and everything it produces — in English, regardless of the sources' language. Benefit: one language throughout.
END_guides

START_state_shape
State form:

- Unit: a snake_case tag reflecting the statement's essence; TYPE — one-two words of the case taxonomy; an annotation of one-two sentences: origin (resolvable — canonical forms in protocol 1 "Origin is mandatory"), time, channel; verified units carry PRIMACY="primary|secondary" (a graded ladder's depth goes in the annotation; PRIMACY stays the binary trust boundary) and shelf life VALIDITY (date or range / condition / as-of); origins may be several — re-deliveries.
- Operations: a journal over units; a unit's status is the fold of its operations; append and replace are the only writes.
- Statuses: unverified · verified · refuted · superseded.
- Edges: supersedes, contradicts, derived-from, confirms, depends-on.
- Demand registry: open questions with a chosen fork branch, a closure owner, a date for deadlines, and closure verdict records (question form — answer substance).
- Artifacts: any digital evidence from any side; indexed name art-<sequence-number>-<hint>.<extension>; units reference an artifact with the ARTIFACT attribute.
- Draft form — the state file's minimal skeleton:
  - root data_draft: TASK required; UPDATED (ISO date), CYCLE (integer), FINAL (true|false) optional;
  - action — required: the approved action wording; SUPERSEDES — optional history of prior wordings (the action's history lives here, not in edges);
  - units — required TYPE, ORIGIN, STATUS; verified implies PRIMACY and VALIDITY; ARTIFACT optional, a reference into the artifact index; tags snake_case, unique;
  - edges — required, may be empty: edge TYPE="supersedes|contradicts|derived-from|confirms|depends-on" FROM TO; FROM/TO — existing unit tags only; directions: supersedes new to old, derived-from derivation to support, confirms confirming to confirmed, depends-on waiting to blocking; contradicts symmetric, direction not fixed;
  - demand_registry — questions: id (qN, continuous, no gaps), tag, OWNER, DEADLINE (optional, ISO date); open — BRANCH="verify-myself|ask-source|accept-default", BLOCKING true|false optional; closed — VERDICT; a status element (COMPLETE, AS_OF) optional;
  - artifacts — the index: id="art-<NN>" matching the file name, path, note optional.
- Canonical formats: dates in structural fields — ISO YYYY-MM-DD (UPDATED, AS_OF, ORIGIN dates, DEADLINE, VALIDITY dates); ORIGIN — tokens separated by ";", each token with its own prefix: web: <URL with scheme> · spoken: person=…, channel=…, date=ISO (person/channel values — text without commas) · check: <instrument>, date=ISO · file: <path from .data-folds/>; VALIDITY — as-of | as-of:ISO date | condition: <text> | ISO date | ISO range, a parenthesized note allowed after the value; an artifact — art-<NN>-<hint>.<ext>, numbering dense, no gaps or duplicates.
- Storage: .data-folds/ in the workspace root; each task — a data-fold-<slug>/ directory holding the draft data-draft-<slug>.xml, the product data-fold-<slug>.xml and the artifacts. The draft lives within the task; moving the task is moving the directory.
END_state_shape

START_product_shape
Product form:

- The skeleton is invariant, one for all cases; the root element carries the declared action, the task and the build date (CREATED); three sections:
  - verified — the verified picture of units with tags, TYPE, origins, statuses, edges, primacy and shelf life;
  - defaults — accepted defaults labeled whose decision;
  - open — open questions and registered contradictions with an owner, an unblock condition and a deadline date.
- The verified section's presentation is chosen for the declared action — e.g., a document, a decision summary or a plan; the section skeleton never changes.
- Name: data-fold-<task-slug>.xml; valid XML; lives in the task directory .data-folds/data-fold-<slug>/.
- After the task completes, only the product carries standalone value; the draft loses force, artifacts remain its attachments.
- Example (content conditional):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<data_fold ACTION="choose a weekend route" TASK="weekend-route" CREATED="2026-10-07">
  <verified>
    <forecast_window_ok TYPE="fact" STATUS="verified" PRIMACY="primary" VALIDITY="as-of" ORIGIN="https://weather.example/weekend" ARTIFACT="data-fold-weekend-route/art-001-forecast.md">
      annotation: no precipitation forecast for the weekend; snapshot saved at intake; 2026-10-07
    </forecast_window_ok>
    <group_size_four TYPE="participant-words" STATUS="verified" PRIMACY="primary" VALIDITY="condition: group unchanged">
      annotation: "we are four"; participant A.; chat; 2026-10-06; confirmed by participant B.
    </group_size_four>
    <hut_phone_booking TYPE="fact" STATUS="verified" PRIMACY="secondary" VALIDITY="condition: hut policy unchanged" ORIGIN="https://travel-blog.example/hut" ARTIFACT="data-fold-weekend-route/art-002-hut-blog.md">
      annotation: the hut takes phone bookings; a traveler's note; 2026-10-05; primary source — the hut site, not reached
    </hut_phone_booking>
  </verified>
  <defaults>
    <start_at_eight DEFAULT_OWNER="executor">
      departure at 8:00; accepted as default, no confirmation requested
    </start_at_eight>
  </defaults>
  <open>
    <question_hut_booked OWNER="participant B." BRANCH="ask participant B." UNBLOCK="check the hut booking">
      is the hut night booked?
    </question_hut_booked>
  </open>
</data_fold>
```
END_product_shape
END_working_patterns

START_tactical_freedom
### Tactical Freedom
Local decisions belong to the executor; the list is not exhaustive: check depth and order, question form, dialogue manner, number of attempts. Boundaries: protocols bind, guides advise.
END_tactical_freedom

START_completion_criteria
### Completion Criteria
- Success: no blocking questions; contradictions resolved or registered with an owner; orphan audit clean; the human approved the readiness; the check pipeline passed — the script clean, audit rounds triaged to the human's explicit "assemble" decision; the product assembled from verified units with explicit "accepted defaults" and "open" sections and written to file.
- Rollback: the human rejected the readiness — accept the edits as new units, pass the cycle, present readiness again.
- Fail-safe: demand blocked externally — the source unavailable, executing its part, or contradiction resolution blocked — freeze with a dead-end report: what is open, who blocks it, what lifts it. Freezing is a legitimate exit, not a failure.
- Zero-context survival: the product carries full meta-markup — tags, origins, statuses, primacy, shelf lives, build date — the next executor works with it without dialogue history.
END_completion_criteria

END_data_fold
