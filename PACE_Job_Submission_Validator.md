# PACE Job Submission Validator
### Zachary Wallace
This is an initiative for the CS 8803 Leadership in CS course Spring 2026

A Python command line tool that checks Slurm job scripts for common mistakes before they are submitted to PACE. Researchers run the validator against their script and get back a plain language summary of what needs to be fixed. Main targets: new HAAG researchers, returning students, and project leads reviewing scripts written by their team.

## Who This Is For:
1) The researcher just finished writing their first Slurm script and wants to verify it is correct before submitting for the first time.
2) The researcher has been submitting jobs that keep failing and needs a fast way to figure out what is wrong without digging through documentation.
3) The returning student is picking up a project after time away and wants a quick sanity check on their scripts before jumping back in.

## What the Validator Checks:
- Resource requests — memory, CPUs, GPUs, and wall time are defined and make sense for the job type
- Parameter configuration — partition names, job names, and QoS settings are valid and compatible
- Output and error files — log files are properly set up so debugging is actually possible
- Environment setup — module loads and required variables are present before the job tries to run
- Feedback — every flagged issue includes a plain language explanation and a concrete suggestion for how to fix it

## How to Run It:
- Clone this repository and run the tool from the command line with your job script as the input
- The validator returns a list of warnings and errors with explanations
- Fix the issues, rerun the validator, and submit once the script is clean

## Deliverable:
An open source Python tool on this repository with full documentation, usage instructions, and example scripts that demonstrate the types of mistakes the validator is designed to catch.
