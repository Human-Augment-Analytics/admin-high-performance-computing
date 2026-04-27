#!/bin/bash
# =============================================================================
# BAD JOB EXAMPLE — pace_validator demo script
# =============================================================================
# This script is intentionally broken to demonstrate what the validator catches.
# Run: python pace_validator.py bad_job.sh
# Expected output: multiple ERRORs and WARNINGs
# =============================================================================

# MISTAKE 1: Job name contains spaces — Slurm will reject this.
#            Fix: use underscores, e.g. --job-name=my_training_run
#SBATCH --job-name=my training run

# MISTAKE 2: GPU partition selected but no --gpus or --gres directive.
#            Fix: add '#SBATCH --gpus=1' or switch to a CPU partition.
#SBATCH --partition=gpu-large

# MISTAKE 3: Wall time set to zero — job is killed before it starts.
#            Fix: set a non-zero duration, e.g. --time=04:00:00
#SBATCH --time=0

# MISTAKE 4: Requesting 2048 CPUs — almost certainly a typo.
#            Fix: most jobs need 1–32 CPUs.
#SBATCH --ntasks=2048

# MISTAKE 5: Output path points to a directory that likely doesn't exist.
#            Fix: create the directory first with 'mkdir -p /nonexistent/path'
#SBATCH --output=/nonexistent/path/out.txt

# MISSING: --mem (no memory request — Slurm will use partition default)
# MISSING: --account (no account specified)
# MISSING: --error (no separate error log)
# MISSING: module load (no software environment set up)

# MISTAKE 6: 'cd ~' changes to home directory, which has limited quota on PACE.
#            Fix: use $SCRATCH for job working directories.
cd ~

echo "Starting job"
