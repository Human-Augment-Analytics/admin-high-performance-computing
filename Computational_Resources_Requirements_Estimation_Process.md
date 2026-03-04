# High Performance Computing Resource Estimation  
### by Neelima Pandey  
CS6999 — Spring 2026  

## Overview  
This project will develop a repeatable process to estimate HPC resource needs for research teams **using a survey-based workflow**. The goal is to reduce guesswork in requests (e.g., cores, memory, GPU type/count, storage, walltime) and to produce a clear **resource estimate + rationale** that can be used for internal planning and for HPC allocation applications.

---

##Status: A survey already exists and will likely need modification based on stakeholder feedback.
[HAAG HPC Resource Estimation Survey](https://docs.google.com/forms/d/e/1FAIpQLScCP9jBCoPDoxk9EOnmLNihqRugzIvQNotvQCJ02VUwvMZkxw/viewform)

---

## Problem Statement  
High Performance Computational and storage needs of all HAAG projects are required to be known upfront at the start of the semester so that we can secure external resources accessible to both Georgia Tech researchers and our external computational advisors. 

This project addresses:  
- What information do we need from researchers to estimate resources reliably?  
- How do we convert survey responses into an actionable resource estimate?  
- How do we standardize this into a reusable workflow and GitHub-ready documentation?

---

## Objectives  
1. **Survey refinement:** Validate and improve the existing survey so it captures the minimum necessary information for estimation.  
2. **Estimation framework:** Define process to convert survey responses into estimates (CPU, memory, GPU, storage, runtime, queue choice).  
3. **Output template:** Create a standardized “Resource Estimation Summary” that teams can attach to proposals or internal requests.  
4. **Usability:** Ensure the process is understandable by non-HPC experts and consistent across projects.  

---

## Proposed Approach (Survey → Estimate → Summary)  

### 1) Survey Intake (Existing Survey + Modifications)  
The survey should capture:  
- **Workload type:** ML training, inference, simulation, data preprocessing, genomics, etc.  
- **Compute pattern:** single-node / multi-node, parallelism style (MPI, multithread, embarrassingly parallel)  
- **Dataset scale:** input size, intermediate artifacts, expected output size  
- **Runtime needs:** per-job runtime, number of runs/experiments, iteration frequency  
- **Hardware constraints:** GPU requirement, memory requirements, CPU-only feasibility  
- **Software stack:** containers, modules, dependencies, licensing constraints  
- **Timeline / urgency:** deadlines, expected project duration  
- **User maturity:** beginner vs advanced HPC user (to inform support needs)

### 2) Estimation Logic  
Define process to estimate resource usage based on the survey responses

Example outputs:  
- CPU cores per job + number of jobs  
- Memory per job  
- GPU type/count (if needed)  
- Storage: home/scratch/project + growth estimate  
- Walltime recommendations and queue/partition suggestions  
- Estimated total compute consumption (e.g., core-hours / GPU-hours)

### 3) Generate a “Resource Estimation Summary”  
A short report (Markdown template) that includes:  
- Project description (from survey)  
- Recommended resources (table)  
- Assumptions + risks (unknowns, variability)  
- How to validate (first pilot job plan)  
- Notes for admins / comp advisors

---

## Potential Audiences / Use Cases  
1) **New teams** preparing to onboard to HAAG/PACE or request allocations  
2) **Ongoing projects** needing to scale from pilot runs to production  
3) **Returning users** who need a refresh or standardized request format  

---

## Deliverables  
- `survey/`  
  - Updated survey questions (Markdown + optional form export)  
- `framework/`  
  - Resource estimation rubric (rules/heuristics)
- `document format/`
  - Standardized “Resource Estimation Summary” format
