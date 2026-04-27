#!/bin/bash
# =============================================================================
# GOOD JOB EXAMPLE — pace_validator demo script
# =============================================================================
# This script demonstrates a well-formed Slurm job submission.
# Run: python pace_validator.py good_job.sh
# Expected output: PASS (one INFO note about the logs/ directory)
# =============================================================================

# Job identity — descriptive name with no spaces, valid account.
#SBATCH --job-name=train_resnet50
#SBATCH --account=gt-cs8803-spring26

# Partition and QoS — GPU partition with matching QoS.
#SBATCH --partition=gpu-medium
#SBATCH --qos=embers-default

# Resource requests — node count, CPU, memory, GPU, and wall time all specified.
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --gpus=1
#SBATCH --time=08:00:00

# Output and error logs — separate files using %j (job ID) for unique names.
# Note: make sure the logs/ directory exists before submitting: mkdir -p logs
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

# Email notifications — get alerted when the job ends or fails.
#SBATCH --mail-user=zwallace@gatech.edu
#SBATCH --mail-type=END,FAIL

# Environment setup — purge defaults, then load only what the job needs.
module purge
module load anaconda3

# Activate the project conda environment.
conda activate dl_env

# Change to scratch space (not home directory) to avoid quota issues.
cd $SCRATCH/resnet_project

# Run the training script.
python train.py --epochs 50 --lr 0.001
