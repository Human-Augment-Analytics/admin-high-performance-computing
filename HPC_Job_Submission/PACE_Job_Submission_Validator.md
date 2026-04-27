# PACE Job Submission Validator
**Zachary Wallace | Georgia Tech | Spring 2026**
CS 8803 Management & Leadership in CS  Spring 2026

---

## Initiative Scope

The PACE Job Submission Validator is a Python command-line tool designed to catch common mistakes in Slurm job scripts before they are submitted to Georgia Tech's Partnership for an Advanced Computing Environment (PACE). The tool accepts a job script as input and returns a structured, plain-language report categorizing every issue found — errors that will likely cause job failure, warnings that should be reviewed, and informational best-practice suggestions — along with a concrete fix for each. The scope covers five core categories of validation: resource requests (memory, CPUs, GPUs, and wall time), parameter configuration (partition names, QoS settings, account, and job naming), output and error file setup, environment initialization (module loads and environment activation), and overall script structure (shebang line, duplicate directives, and the presence of an executable command). The tool requires no external dependencies beyond Python 3.10 and is fully open source.

The initiative was scoped specifically to address a recurring pain point observed in the HAAG research environment: new and returning researchers spending significant time debugging failed jobs that could have been caught before submission. Rather than modifying PACE infrastructure or requiring administrative access, the validator operates entirely on the researcher's local machine or login node as a pre-submission step. This made adoption low-friction and realistic for the HAAG researcher population. The deliverable includes the validator script, a README with full usage documentation, and two example scripts demonstrating the types of mistakes the tool is designed to catch, all hosted in a public GitHub repository at https://github.com/Human-Augment-Analytics/admin-high-performance-computing/tree/main/HPC_Job_Submission.

---

## Who This Is For

1) The researcher just finished writing their first Slurm script and wants to verify it is correct before submitting for the first time.
2) The researcher has been submitting jobs that keep failing and needs a fast way to figure out what is wrong without digging through documentation.
3) The returning student is picking up a project after time away and wants a quick sanity check on their scripts before jumping back in.

---

## Procedure: Pre-Submission Slurm Script Validation

**Repository Link:** https://github.com/Human-Augment-Analytics/admin-high-performance-computing/tree/main/HPC_Job_Submission

**Purpose**

This procedure ensures that HAAG researchers validate their Slurm job scripts using the PACE Job Submission Validator before submitting to PACE. It is intended to reduce job failures caused by common, preventable configuration errors and to establish a consistent quality standard for scripts submitted by all HAAG members regardless of experience level.

**Intended Audience**

All HAAG researchers who submit jobs to PACE, including first-time users, returning students, and project leads reviewing scripts written by teammates.

**Prerequisites**

A PACE login node account, or a local machine with Python 3.10 or later. To verify your Python version, run:
python3 --version

If the version is below 3.10, load the Python module on PACE first:
module load python/3.10

**Steps**

**Step 1.** Clone the validator repository to your PACE login node or local machine:
git clone https://github.com/Human-Augment-Analytics/admin-high-performance-computing/tree/main/HPC_Job_Submission && cd pace-job-validator

**Step 2.** Run the validator against your job script before submitting:
python pace_validator.py your_job.sh

**Step 3.** Review the output. Issues are labeled by severity:

- `ERROR` — must be resolved before submission. Indicates conditions that will cause job failure.
- `WARNING` — should be reviewed and resolved unless you have a deliberate reason to proceed.
- `INFO` — best-practice suggestions that do not block submission.

**Step 4.** Edit your script to address all errors and applicable warnings. Rerun the validator until it reports PASS.

**Step 5.** Submit the clean script to PACE using your normal sbatch workflow.

**Integration & Enforcement**

Project leads reviewing scripts written by teammates should run the validator as part of their review step before approving submission. For onboarding new members, this procedure should be introduced alongside PACE account setup as a standard part of the HAAG new-member checklist. The tool can also be integrated into a CI/CD or pre-commit hook using the `--exit-code` flag, which returns a non-zero exit status on failure, enabling automated enforcement in shared project repositories.

---

## Example Scripts

- `examples/bad_job.sh` — intentionally broken script that demonstrates the types of mistakes the validator catches
- `examples/good_job.sh` — a clean, well-formed script that passes validation

---

## License

MIT — open source and free to use, modify, and distribute.You said: add the steps as welladd the steps as well3:21 PMClaude responded: Here you go — copy and paste the whole thing:Here you go — copy and paste the whole thing:
markdown# PACE Job Submission Validator
**Zachary Wallace | Georgia Tech | Spring 2026**
CS 8803 Management & Leadership in CS — Spring 2026

---

## Initiative Scope

The PACE Job Submission Validator is a Python command-line tool designed to catch common mistakes in Slurm job scripts before they are submitted to Georgia Tech's Partnership for an Advanced Computing Environment (PACE). The tool accepts a job script as input and returns a structured, plain-language report categorizing every issue found — errors that will likely cause job failure, warnings that should be reviewed, and informational best-practice suggestions — along with a concrete fix for each. The scope covers five core categories of validation: resource requests (memory, CPUs, GPUs, and wall time), parameter configuration (partition names, QoS settings, account, and job naming), output and error file setup, environment initialization (module loads and environment activation), and overall script structure (shebang line, duplicate directives, and the presence of an executable command). The tool requires no external dependencies beyond Python 3.10 and is fully open source.

The initiative was scoped specifically to address a recurring pain point observed in the HAAG research environment: new and returning researchers spending significant time debugging failed jobs that could have been caught before submission. Rather than modifying PACE infrastructure or requiring administrative access, the validator operates entirely on the researcher's local machine or login node as a pre-submission step. This made adoption low-friction and realistic for the HAAG researcher population. The deliverable includes the validator script, a README with full usage documentation, and two example scripts demonstrating the types of mistakes the tool is designed to catch, all hosted in a public GitHub repository at https://github.com/Human-Augment-Analytics/admin-high-performance-computing/tree/main/HPC_Job_Submission.

---

## Who This Is For

1) The researcher just finished writing their first Slurm script and wants to verify it is correct before submitting for the first time.
2) The researcher has been submitting jobs that keep failing and needs a fast way to figure out what is wrong without digging through documentation.
3) The returning student is picking up a project after time away and wants a quick sanity check on their scripts before jumping back in.

---

## What the Validator Checks

- **Resource requests** — memory, CPUs, GPUs, and wall time are defined and make sense for the job type
- **Parameter configuration** — partition names, job names, and QoS settings are valid and compatible
- **Output and error files** — log files are properly set up so debugging is actually possible
- **Environment setup** — module loads and required variables are present before the job tries to run
- **Feedback** — every flagged issue includes a plain language explanation and a concrete suggestion for how to fix it

---

## How to Run It

Clone this repository and run the tool from the command line with your job script as the input. The validator returns a list of warnings and errors with explanations. Fix the issues, rerun the validator, and submit once the script is clean.
Validate a single script
python pace_validator.py job.sh
Validate multiple scripts at once
python pace_validator.py *.sh
Treat warnings as errors
python pace_validator.py job.sh --strict
Exit with code 1 on failure (useful for CI hooks)
python pace_validator.py job.sh --exit-code
Print only the pass/fail summary line
python pace_validator.py *.sh --summary-only

---

## Procedure: Pre-Submission Slurm Script Validation

**Repository Link:** https://github.com/Human-Augment-Analytics/admin-high-performance-computing/tree/main/HPC_Job_Submission

**Purpose**

This procedure ensures that HAAG researchers validate their Slurm job scripts using the PACE Job Submission Validator before submitting to PACE. It is intended to reduce job failures caused by common, preventable configuration errors and to establish a consistent quality standard for scripts submitted by all HAAG members regardless of experience level.

**Intended Audience**

All HAAG researchers who submit jobs to PACE, including first-time users, returning students, and project leads reviewing scripts written by teammates.

**Prerequisites**

A PACE login node account, or a local machine with Python 3.10 or later. To verify your Python version, run:
python3 --version

If the version is below 3.10, load the Python module on PACE first:
module load python/3.10

**Steps**

**Step 1.** Clone the validator repository to your PACE login node or local machine:
git clone https://github.com/Human-Augment-Analytics/admin-high-performance-computing/tree/main/HPC_Job_Submission && cd pace-job-validator

**Step 2.** Run the validator against your job script before submitting:
python pace_validator.py your_job.sh

**Step 3.** Review the output. Issues are labeled by severity:

- `ERROR` — must be resolved before submission. Indicates conditions that will cause job failure.
- `WARNING` — should be reviewed and resolved unless you have a deliberate reason to proceed.
- `INFO` — best-practice suggestions that do not block submission.

**Step 4.** Edit your script to address all errors and applicable warnings. Rerun the validator until it reports PASS.

**Step 5.** Submit the clean script to PACE using your normal `sbatch` workflow.

**Integration & Enforcement**

Project leads reviewing scripts written by teammates should run the validator as part of their review step before approving submission. For onboarding new members, this procedure should be introduced alongside PACE account setup as a standard part of the HAAG new-member checklist. The tool can also be integrated into a CI/CD or pre-commit hook using the `--exit-code` flag, which returns a non-zero exit status on failure, enabling automated enforcement in shared project repositories.

---

## Example Scripts

- `examples/bad_job.sh` — intentionally broken script that demonstrates the types of mistakes the validator catches
- `examples/good_job.sh` — a clean, well-formed script that passes validation

---

## Deliverable

An open source Python tool on this repository with full documentation, usage instructions, and example scripts that demonstrate the types of mistakes the validator is designed to catch.

---
- `examples/bad_job.sh` — intentionally broken script that demonstrates the types of mistakes the validator catches
- `examples/good_job.sh` — a clean, well-formed script that passes validation

---
