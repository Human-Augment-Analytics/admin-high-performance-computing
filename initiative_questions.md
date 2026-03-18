# Initiative Questions

**Project:** HPC Job Submission Validation
**Organization:** HAAG

---

## Describe Your Initiative / Procedure

This initiative focuses on improving how researchers at HAAG submit jobs to the High Performance Computing (HPC) system. Right now, most researchers learn through trial and error, which leads to common mistakes like wrong resource requests, missing settings, or bad configurations. These mistakes waste compute time and slow down research.

The plan is to introduce a simple validation step before job submission — a lightweight script that checks a job file for common errors and gives the researcher feedback before anything is sent to the scheduler.

The goal is to find out whether this extra step reduces job failures and makes the process easier, especially for new researchers.

---

## Hypotheses / KPIs

**Hypothesis**

If researchers run a validation check on their job scripts before submitting, fewer jobs will fail due to configuration errors.

**KPIs Planned (Not Yet Measured)**

- Job failure rate before and after the validation step is introduced
- Number of common errors caught by the validation tool
- Time spent troubleshooting failed jobs
- Researcher confidence in submitting jobs (pre/post survey)
- Resubmission rate

> Data collection has not started yet. The next step is establishing a baseline by observing current job submissions and talking with researchers.

---

## Method for Testing — Flowcharts

**Current Workflow (Problem)**

```
Write job script
      |
      v
Submit to scheduler
      |
      v
Job fails
      |
      v
Manually read logs, guess the error, resubmit
      (repeat until it works)
```

**Proposed Workflow (With Validation)**

```
Write job script
      |
      v
Run validation script
      |
   ___|___
  |       |
PASS    ERRORS FOUND
  |       |
  v       v
Submit  Fix errors using tool feedback
        then re-run validation and submit
```

---

## Stakeholder Engagement

**Stakeholders**

- New HAAG researchers — main users of the tool
- Experienced researchers and technical leads — subject matter experts
- Faculty advisors — oversight and broader context
- HAAG staff and project leads — onboarding and workflow owners

**Current Status**

Stakeholder engagement has not formally begun yet. The next steps are to schedule conversations with experienced HPC users to understand the current workflow and confirm the problem before moving into the experiment phase.

**Expectations**

The goal is for experienced users to validate the workflow description and help identify the most common errors. New researchers will serve as the pilot group when the tool is ready to test.

---

## Documentation for Sustainability

**Planned Documentation**

- Overview of the current HPC job submission workflow
- Step-by-step guide for using the validation script
- Common errors reference sheet with suggested fixes
- Onboarding checklist for new researchers

**Hosting**

All documentation will be stored in the HAAG GitHub repository under a `/docs/hpc-validation/` folder.

> No documentation has been created yet. This is the next major deliverable after the discovery phase is complete.

---

## Measuring Progress

Progress will be measured by comparing job failure rates before and after the validation tool is introduced. Success looks like fewer failed jobs, less time spent troubleshooting, and researchers feeling more confident when submitting jobs.

> Baseline data has not been collected yet. The first step is to gather information on how researchers currently submit jobs and what errors come up most often.

---

## Obstacles and Bottlenecks

**Anticipated Challenges**

- New researchers currently have no formal documentation to reference
- Most HPC knowledge is passed informally between students
- Getting consistent time with researchers for interviews may be difficult

**Unknowns to Resolve**

- What specific errors are most common in job scripts at HAAG
- Whether historical job failure data exists and is accessible
- How complex the validation script will need to be to cover the most impactful errors
