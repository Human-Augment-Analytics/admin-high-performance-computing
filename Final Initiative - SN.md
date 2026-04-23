# HAAG Storage & Semester-to-Semester Documentation Handoff Initiative

**Author:** Sophia Nguyen
**Program:** Human Augmented Analytics Group (HAAG) — Georgia Institute of Technology
**Audience:** HAAG members, comp advisors
**Status:** In Progress
**Last Updated:** April 23, 2026

---

## Table of Contents

1. [Initiative Overview & Procedure](#1-initiative-overview--procedure)
2. [Hypotheses & KPIs](#2-hypotheses--kpis)
3. [Test Method](#3-test-method)
4. [Stakeholder Engagement](#4-stakeholder-engagement)
5. [Sustainability & Hosting](#5-sustainability--hosting)
6. [Progress Measurement](#6-progress-measurement)
7. [Obstacles & Bottlenecks](#7-obstacles--bottlenecks)
8. [Appendix A: Repository Structure](#appendix-a-repository-structure)
9. [Appendix B: Handoff Checklist](#appendix-b-handoff-checklist)
10. [Appendix C: README Template](#appendix-c-readme-template)

---

## 1. Initiative Overview & Procedure

### The Problem

HAAG is a rotating research group. When a member finishes a semester, there is no standard place to leave documentation, no agreed format, and no checklist to confirm handoff is complete. The next person wastes time searching for context that may not exist at all.

### The Fix — Three Rules, One Repo

This initiative introduces **three rules** that any HAAG member can follow with minimal effort and zero new tools:

| Rule | What It Means |
|---|---|
| **1. GitHub is the source of truth** | All project documentation lives in the GitHub repo — not personal drives, email, or Slack |
| **2. Use three folders** | `final/` for approved docs, `drafts/` for work-in-progress, `archive/` for old versions |
| **3. Fill out the checklist before you leave** | Before the semester ends, complete the one-page handoff checklist in `final/` |

That's it. Everything else in this document is context and support material.

### Folder Logic

| Folder | Use it for | Trust level |
|---|---|---|
| `final/` | Anything approved and usable by the next person | Current — use this |
| `drafts/` | Work in progress, not yet validated | Working — don't cite as definitive |
| `archive/` | Old versions of `final/` docs | Historical — reference only |

**Promotion rule:** A document moves from `drafts/` → `final/` when it's ready to hand off. The old version of any `final/` doc moves to `archive/` — never deleted.

---

## 2. Hypotheses & KPIs

### Hypotheses

**H1 — Findability:** Using a consistent `final/` / `drafts/` / `archive/` structure reduces time spent searching for current documentation.

**H2 — Continuity:** Completing a handoff checklist at semester end reduces knowledge loss when members rotate off projects.

**H3 — Onboarding speed:** New members onboard faster when there is a predictable starting point (`final/00_start-here/`).

### KPIs

| KPI | How to Measure | Target |
|---|---|---|
| Time to find a key document | Ask one new member to find a specific doc; record minutes | Reduce by ≥40% vs. no standard |
| Handoff completeness | Check `final/` against the minimum artifact list at semester end | ≥90% of required docs present |
| "Where is X?" messages | Count questions asked in project chat during onboarding | Reduce by ≥50% vs. prior semester |
| Adoption rate | Spot-check repo weekly; count docs in the correct folder | ≥85% compliance |

### Measurement Status

All KPIs are **planned but not yet measured.** Baseline data will be collected at the start of the pilot and compared at semester end. No complex instrumentation is needed — a simple count and a timer are sufficient.

---

## 3. Test Method

The test runs in three steps. Each step is self-contained and can be done without organizing meetings or coordinating large groups.

### Step 1 — Baseline (do this once, takes ~30 minutes)

1. Pick one HAAG project repo that is currently active.
2. Ask one person (yourself or a single teammate) to find three specific documents without your help — time them.
3. Note where those documents actually were and how long it took.
4. Write down the top 2–3 places people currently store things (repo, personal drive, Slack, etc.).

This is your baseline. No interviews, no observation sessions — just one quick test.

---

### Step 2 — Implement (do this once, takes ~1 hour)

1. Create the `final/`, `drafts/`, and `archive/` folders in the GitHub repo.
2. Move existing documents into the correct folder (anything ready → `final/`, anything in progress → `drafts/`, old versions → `archive/`).
3. Add a `final/00_start-here/` folder with a short README explaining where things are.
4. Share the repo link and a one-paragraph explanation with the team in Slack or email — no meeting required.

---

### Step 3 — Measure (do this at semester end, takes ~20 minutes)

1. Repeat the same timed document-find test from Step 1 with one new or returning member.
2. Check `final/` against the minimum artifact list (see Appendix B).
3. Count how many "where is X?" questions came up during onboarding.
4. Note what worked and what was ignored — update the checklist for next semester.

---

## 4. Stakeholder Engagement

### Who Needs to Be Involved (Minimum)

You do not need buy-in from everyone to start. The minimum viable set of people:

| Person | What you need from them | Time required |
|---|---|---|
| **You** | Set up the repo structure; fill out the first handoff checklist | ~1–2 hours total |
| **One comp advisor** | Awareness that this is happening; optional: quick review of `final/` at semester end | 5–10 minutes |
| **One teammate** | Complete the timed document-find test for baseline and post-pilot measurement | 10–15 minutes each time |

That's three people maximum, with no required meetings.

### Engagement Expectations

- **New members** will benefit immediately from `final/00_start-here/` — no behavior change required on their end.
- **Experienced members** may ignore `drafts/` discipline under time pressure. That's acceptable — the hard requirement is only that `final/` and the handoff checklist are complete by semester end.
- **Comp advisors** don't need to change anything. They can check `final/` at any time to see current project status without asking the team.

### Likely Adjustments

If the three-folder rule creates friction, the fallback is simpler: just require `final/` and the handoff checklist. `drafts/` and `archive/` become optional.

---

## 5. Sustainability & Hosting

### Where Everything Lives

All documentation is hosted in the HAAG GitHub repository. The procedure is self-hosting — it lives inside the same structure it defines.

### Minimum Documents to Create

You only need to create these to have a functional system:

| Document | Location | Status |
|---|---|---|
| Repo structure (this doc's Appendix A) | `final/01_procedures/storage-procedure.md` | Ready to copy |
| Handoff checklist | `final/00_start-here/handoff-checklist.md` | Ready to copy (Appendix B) |
| README / navigation guide | `final/00_start-here/README.md` | Ready to copy (Appendix C) |

Everything else (decision logs, meeting notes, full SOP library) is optional and can be added later if the team wants it.

### What Keeps This Running Long-Term

- The handoff checklist is the only required action at the end of each semester.
- No designated maintainer is required — any outgoing member completes their own checklist.
- If the structure drifts, it can be corrected in 20–30 minutes during the next semester's first week.

---

## 6. Progress Measurement

### How to Track Without Overhead

| Check | How often | How to do it |
|---|---|---|
| Are docs in the right folders? | Once a week, 2 minutes | Glance at the repo; note anything in the wrong place |
| Is `final/` complete? | Once at semester end | Compare against the 5-item minimum artifact checklist |
| Is onboarding faster? | Once per new member | Time how long it takes them to find a specific doc |

### Signs It's Working

- The next person who joins the project finds what they need without asking anyone
- `final/` has the handoff checklist and README at the end of every semester
- Fewer messages like "hey where is the [document]?"

### Signs It's Not Working

- `final/` is empty at semester end
- People are still storing docs in personal drives or Slack
- The handoff checklist is consistently skipped

---

## 7. Obstacles & Bottlenecks

| Obstacle | Why it happens | Simple fix |
|---|---|---|
| Handoff checklist skipped at semester end | Time crunch; low visibility | Add it to the last advisor check-in as a standing agenda item |
| `final/` becomes a dumping ground | No review step before promotion | Keep it simple — if it's ready to hand off, it goes in `final/` |
| Docs still living outside the repo | Habit; convenience | Don't fight it during the semester — require migration only at handoff |
| No one reads the README | Too long; too formal | Keep the README to 10 lines maximum; link don't explain |

---

## Appendix A: Repository Structure

```
haag-project-name/
├── README.md                      # 10-line overview + link to final/00_start-here/
│
├── final/                         # APPROVED — current docs; use this first
│   ├── 00_start-here/
│   │   ├── README.md              # Where things are; what's current; who to ask
│   │   └── handoff-checklist.md   # Completed by outgoing member each semester
│   └── 01_procedures/
│       └── storage-procedure.md   # This document (trimmed to 1 page)
│
├── drafts/                        # IN PROGRESS — not final; do not cite
│
└── archive/                       # OLD VERSIONS — reference only
    └── YYYY-MM_semester/
```

**Naming rules (short version):**
- Lowercase, hyphens, no spaces: `my-document.md` not `My Document.md`
- Archive folders: prefix with semester date: `2025-12_fall/`
- Never use `_v2`, `_final`, `_new` in filenames — folder location communicates version trust

---

## Appendix B: Handoff Checklist

*Copy this into `final/00_start-here/handoff-checklist.md` and fill it out before the semester ends.*

```
HAAG HANDOFF CHECKLIST
=======================
Project:          ________________________________
Semester:         ________________________________
Outgoing member:  ________________________________
Incoming member:  ________________________________
Date completed:   ________________________________

REQUIRED (must be done before semester ends):

 [ ] final/ contains a README explaining what the project is and where things are
 [ ] final/ contains this completed handoff checklist
 [ ] Any in-progress work has a note in drafts/ explaining its current state
 [ ] Incoming member (or next-semester contact) has repo access
 [ ] One sentence written below: "The most important thing to know is..."

 Most important thing to know:
 ________________________________________________________________

OPTIONAL (do if time allows):

 [ ] Old versions of final/ docs moved to archive/YYYY-MM_semester/
 [ ] Decision log updated with any major choices made this semester
 [ ] Comp advisor notified that handoff is complete

Done:  _________________________ (outgoing)   Date: ____________
```

---

## Appendix C: README Template

*Copy this into `final/00_start-here/README.md`. Keep it under 15 lines.*

```markdown
# [Project Name] — Start Here

**What this project is:** [One sentence]
**Current status:** [Active / On hold / Wrapping up]
**Last updated:** YYYY-MM-DD by [Name]

## Where things are
- Current documentation → `final/`
- Work in progress → `drafts/`
- Old versions → `archive/`

## Who to contact
- **Project lead:** [Name] — [GT username or email]
- **Comp advisor:** [Name]

## What to do first
Read `final/00_start-here/handoff-checklist.md` from the previous semester.
```
