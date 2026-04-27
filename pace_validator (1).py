#!/usr/bin/env python3
"""
PACE Job Submission Validator
==============================
Checks Slurm job scripts for common mistakes before submission to PACE.

Author: Zachary Wallace | Georgia Tech | Spring 2026
Course: CS 8803 Leadership in CS

Usage:
    python pace_validator.py job.sh
    python pace_validator.py *.sh --strict
    python pace_validator.py job.sh --exit-code
"""

import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ──────────────────────────────────────────────
# Data models
# ──────────────────────────────────────────────

# Severity levels mirror standard log levels.
# ERROR   = will cause job failure or incorrect behavior; must be fixed before submission.
# WARNING = likely a problem; should be reviewed before submission.
# INFO    = best-practice suggestion; does not block submission.
class Severity(Enum):
    ERROR   = "ERROR"
    WARNING = "WARNING"
    INFO    = "INFO"


# ANSI escape codes for terminal color output.
# Skipped automatically when stdout is not a TTY (e.g. piped to a file).
COLORS = {
    "red":     "\033[91m",   # errors
    "yellow":  "\033[93m",   # warnings
    "cyan":    "\033[96m",   # info / suggestions
    "green":   "\033[92m",   # pass
    "bold":    "\033[1m",    # section headers
    "dim":     "\033[2m",    # secondary text (line content, path)
    "reset":   "\033[0m",    # reset all formatting
}

# Maps each severity level to a color key for consistent output formatting.
SEV_COLOR = {
    Severity.ERROR:   "red",
    Severity.WARNING: "yellow",
    Severity.INFO:    "cyan",
}

# Unicode icons shown next to each severity level in the report.
SEV_ICON = {
    Severity.ERROR:   "✗",
    Severity.WARNING: "⚠",
    Severity.INFO:    "ℹ",
}


@dataclass
class Issue:
    """
    Represents a single validation finding.

    Attributes:
        severity     -- how critical the issue is (ERROR, WARNING, INFO)
        category     -- grouping label shown in the report (e.g. "Resource Requests")
        message      -- plain-language description of what is wrong
        suggestion   -- concrete instruction for how to fix it
        line_number  -- optional line in the script where the issue was found
        line_content -- the raw text of that line, shown in the report for context
    """
    severity: Severity
    category: str
    message: str
    suggestion: str
    line_number: Optional[int] = None
    line_content: Optional[str] = None


@dataclass
class ValidationResult:
    """
    Accumulates all issues found during a single script validation run.

    Attributes:
        script_path -- path to the script that was validated (used in report header)
        issues      -- list of Issue objects appended by each check function
        directives  -- parsed #SBATCH directives; also used to pass state between checks
                       (_partition is stored here so check_gpus can read it)
    """
    script_path: str
    issues: list[Issue] = field(default_factory=list)
    directives: dict = field(default_factory=dict)

    @property
    def errors(self):
        """Return only ERROR-level issues."""
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self):
        """Return only WARNING-level issues."""
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def infos(self):
        """Return only INFO-level issues."""
        return [i for i in self.issues if i.severity == Severity.INFO]

    @property
    def passed(self):
        """True if no ERROR-level issues found. Warnings/infos do not fail the script."""
        return len(self.errors) == 0


# ──────────────────────────────────────────────
# Known PACE values (update as cluster evolves)
# ──────────────────────────────────────────────

# Known valid PACE partition names as of Spring 2026.
# If PACE adds or removes partitions, update this set.
# Reference: https://docs.pace.gatech.edu
VALID_PARTITIONS = {
    "cpu-small", "cpu-medium", "cpu-large", "cpu-xlarge",
    "gpu-small", "gpu-medium", "gpu-large",
    "inferno", "phoenix", "ice",
    "embers", "roc", "hive",
}

# Known valid QoS (Quality of Service) values on PACE.
# QoS controls job priority and wall time limits per partition policy.
VALID_QOS = {
    "inferno", "phoenix", "ice",
    "embers-default", "embers-high", "embers-low",
    "debug", "short", "long",
}

# Derived sets used for GPU/partition cross-validation.
# GPU_PARTITIONS: partitions that have GPU nodes attached.
# CPU_ONLY_PARTITIONS: partitions with no GPU nodes.
GPU_PARTITIONS = {p for p in VALID_PARTITIONS if "gpu" in p}
CPU_ONLY_PARTITIONS = VALID_PARTITIONS - GPU_PARTITIONS

# Wall time thresholds used in check_wall_time.
# Jobs over WARN threshold get an INFO; over MAX threshold get a WARNING.
MAX_WALL_TIME_HOURS = 504   # 21 days — conservative upper bound
WARN_WALL_TIME_HOURS = 168  # 7 days

# Commonly used PACE modules, referenced in environment setup guidance.
COMMON_MODULES = {
    "cuda", "python", "anaconda3", "gcc", "openmpi",
    "intel", "pytorch", "tensorflow", "julia", "r",
}


# ──────────────────────────────────────────────
# Parser
# ──────────────────────────────────────────────

def parse_script(path: Path) -> tuple[dict, list[tuple[int, str]]]:
    """
    Read a Slurm job script and extract all #SBATCH directives.

    Returns a tuple of:
        directives -- dict mapping normalized option name -> (value, line_number, raw_line)
                      Keys use underscores (e.g. "mem_per_cpu", not "mem-per-cpu").
        all_lines  -- list of (line_number, raw_line) for every line in the file,
                      used by checks that scan the full script body.

    Opened with errors="replace" so scripts with non-UTF-8 bytes don't crash the validator.
    """
    directives = {}
    all_lines = []

    with open(path, "r", errors="replace") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            all_lines.append((lineno, line))

            # Match lines of the form:
            #   #SBATCH --option=value
            #   #SBATCH --option value
            #   #SBATCH -o value
            # Group 1 = option name, group 2 = value (may be empty).
            m = re.match(r"^#SBATCH\s+--?([\w-]+)(?:[=\s]+(.*))?$", line.strip())
            if m:
                # Normalize: lowercase, hyphens -> underscores
                key = m.group(1).strip().lower().replace("-", "_")
                val = (m.group(2) or "").strip()
                directives[key] = (val, lineno, line)

    return directives, all_lines


# ──────────────────────────────────────────────
# Individual checks
# ──────────────────────────────────────────────
# Each check follows the same pattern:
#   - Accepts parsed directives and/or all_lines, plus a ValidationResult
#   - Appends Issue objects to result.issues for any problems found
#   - Returns nothing (mutates result in place)
# ──────────────────────────────────────────────

def check_shebang(all_lines: list, result: ValidationResult):
    """
    Verify the script starts with a valid shebang line.

    Slurm passes the script to the shell specified by the shebang.
    A missing or unusual shebang can cause the job to fail silently.
    PACE jobs almost always use #!/bin/bash.
    """
    # Empty file — flag as error and return early.
    if not all_lines:
        result.issues.append(Issue(
            Severity.ERROR, "Structure",
            "Script is empty.",
            "Add a shebang line (#!/bin/bash) and your #SBATCH directives."
        ))
        return

    first_line = all_lines[0][1].strip()

    if not first_line.startswith("#!"):
        # No shebang — Slurm defaults to /bin/sh which may not behave as expected.
        result.issues.append(Issue(
            Severity.ERROR, "Structure",
            "Missing shebang line at the top of the script.",
            "Add '#!/bin/bash' as the very first line.",
            line_number=1, line_content=all_lines[0][1]
        ))
    elif "bash" not in first_line and "sh" not in first_line:
        # Shebang points to something other than a shell (e.g. Python, Perl).
        # Warning rather than error since it may be intentional.
        result.issues.append(Issue(
            Severity.WARNING, "Structure",
            f"Unusual shebang: '{first_line}'. PACE jobs typically use bash.",
            "Consider using '#!/bin/bash' unless you have a specific reason.",
            line_number=1, line_content=all_lines[0][1]
        ))


def check_job_name(d: dict, result: ValidationResult):
    """
    Check that a job name is present, non-empty, has no spaces, and is not too long.

    A job name makes it easier to identify your job in 'squeue' output.
    Slurm rejects names with spaces. Names over 64 characters may be truncated.
    """
    # Check both --job-name (stored as "job_name") and the short form -J.
    if "job_name" not in d and "J" not in d:
        result.issues.append(Issue(
            Severity.WARNING, "Parameter Configuration",
            "No job name specified (--job-name / -J).",
            "Add '#SBATCH --job-name=my_job' so you can identify it in the queue with 'squeue'."
        ))
    else:
        val, lineno, line = d.get("job_name") or d.get("J")

        if not val:
            # Directive present but value is blank.
            result.issues.append(Issue(
                Severity.ERROR, "Parameter Configuration",
                "--job-name is present but has no value.",
                "Provide a descriptive name, e.g. '#SBATCH --job-name=training_run_v2'.",
                line_number=lineno, line_content=line
            ))
        elif re.search(r"\s", val):
            # Slurm does not allow whitespace in job names — scheduler will reject the job.
            result.issues.append(Issue(
                Severity.ERROR, "Parameter Configuration",
                f"Job name '{val}' contains spaces, which Slurm does not allow.",
                "Use underscores or hyphens instead of spaces: e.g. 'training_run_v2'.",
                line_number=lineno, line_content=line
            ))
        elif len(val) > 64:
            # Soft limit — not a hard Slurm error but can cause display/logging confusion.
            result.issues.append(Issue(
                Severity.WARNING, "Parameter Configuration",
                f"Job name is {len(val)} characters. Some schedulers truncate at 64.",
                "Keep job names under 64 characters."
            ))


def check_partition(d: dict, result: ValidationResult):
    """
    Verify a partition is specified and matches a known PACE partition name.

    Without a partition, Slurm uses a default that may not match the job's needs.
    An unrecognized partition name will cause the job to be rejected at submission.

    Stores the normalized partition name in result.directives["_partition"]
    so check_gpus can cross-reference it without re-parsing.
    """
    if "partition" not in d and "p" not in d:
        result.issues.append(Issue(
            Severity.ERROR, "Parameter Configuration",
            "No partition specified (--partition / -p).",
            "Add '#SBATCH --partition=<partition>' — check PACE docs for available partitions."
        ))
        return  # No point checking the value if the directive isn't there.

    val, lineno, line = d.get("partition") or d.get("p")

    if not val:
        result.issues.append(Issue(
            Severity.ERROR, "Parameter Configuration",
            "--partition is present but has no value.",
            "Specify a partition, e.g. '#SBATCH --partition=cpu-medium'.",
            line_number=lineno, line_content=line
        ))
        return

    partition = val.lower()

    if partition not in VALID_PARTITIONS:
        # WARNING not ERROR — PACE may have added new partitions since this tool was updated.
        result.issues.append(Issue(
            Severity.WARNING, "Parameter Configuration",
            f"Partition '{val}' is not in the known PACE partition list.",
            f"Known partitions include: {', '.join(sorted(VALID_PARTITIONS))}. "
            "Check https://docs.pace.gatech.edu for the latest list.",
            line_number=lineno, line_content=line
        ))

    # Store for use by check_gpus.
    result.directives["_partition"] = partition


def check_qos(d: dict, result: ValidationResult):
    """
    Check that the QoS value, if present, is recognized.

    QoS controls job priority and wall time limits. An incorrect QoS causes Slurm
    to reject the job. Missing QoS is acceptable — partition default is used.
    """
    if "qos" not in d:
        # Missing QoS is not an error — partition default applies.
        result.issues.append(Issue(
            Severity.INFO, "Parameter Configuration",
            "No QoS specified (--qos). The default QoS will be used.",
            "If you need priority or extended wall time, set '#SBATCH --qos=<qos>'."
        ))
        return

    val, lineno, line = d["qos"]
    if val.lower() not in VALID_QOS:
        result.issues.append(Issue(
            Severity.WARNING, "Parameter Configuration",
            f"QoS '{val}' is not in the known PACE QoS list.",
            f"Known QoS values: {', '.join(sorted(VALID_QOS))}.",
            line_number=lineno, line_content=line
        ))


def _parse_mem_mb(mem_str: str) -> Optional[int]:
    """
    Convert a Slurm memory string to megabytes.

    Accepts: 8G, 16384M, 4096, 512K, 2T (with or without trailing B).
    Returns MB as int, or None if parsing fails.
    Helper for check_memory — not a standalone check.
    """
    m = re.match(r"^(\d+(?:\.\d+)?)\s*([KMGT]?B?)?$", mem_str.strip(), re.IGNORECASE)
    if not m:
        return None
    val = float(m.group(1))
    # Strip trailing 'B' so "GB" and "G" are treated the same.
    unit = (m.group(2) or "MB").upper().rstrip("B")
    multipliers = {"": 1, "K": 1/1024, "M": 1, "G": 1024, "T": 1024*1024}
    return int(val * multipliers.get(unit, 1))


def check_memory(d: dict, result: ValidationResult):
    """
    Verify a memory request is present, parseable, and within a sane range.

    Without an explicit memory request, Slurm assigns the partition default,
    which is often too low and can cause the job to be OOM-killed mid-run.
    Accepts --mem, --mem-per-cpu, --mem-per-gpu.

    Thresholds:
        < 256 MB  -> WARNING (suspiciously low)
        > 500 GB  -> WARNING (suspiciously high; likely a typo)
    """
    mem_key = next((k for k in ["mem", "mem_per_cpu", "mem_per_gpu"] if k in d), None)

    if not mem_key:
        result.issues.append(Issue(
            Severity.ERROR, "Resource Requests",
            "No memory requested (--mem, --mem-per-cpu, or --mem-per-gpu).",
            "Add '#SBATCH --mem=8G' (or appropriate size). Without this, Slurm assigns "
            "the partition default, which may be far too small for your job."
        ))
        return

    val, lineno, line = d[mem_key]

    if not val:
        result.issues.append(Issue(
            Severity.ERROR, "Resource Requests",
            f"--{mem_key.replace('_','-')} is present but has no value.",
            "Specify a memory amount, e.g. '#SBATCH --mem=16G'.",
            line_number=lineno, line_content=line
        ))
        return

    mb = _parse_mem_mb(val)

    if mb is None:
        # Value present but not parseable — likely a typo or wrong format.
        result.issues.append(Issue(
            Severity.ERROR, "Resource Requests",
            f"Memory value '{val}' could not be parsed.",
            "Use a format like '8G', '16384M', or '4096'. Units: K, M, G, T.",
            line_number=lineno, line_content=line
        ))
    elif mb < 256:
        # Valid Slurm syntax but almost certainly too low for a real job.
        result.issues.append(Issue(
            Severity.WARNING, "Resource Requests",
            f"Requested memory ({val}) is very low (< 256 MB).",
            "Most real jobs need at least 1–4 GB. Check your actual memory needs.",
            line_number=lineno, line_content=line
        ))
    elif mb > 500 * 1024:
        # Valid if the node supports it, but almost always a mistake.
        result.issues.append(Issue(
            Severity.WARNING, "Resource Requests",
            f"Requested memory ({val}) is very large (> 500 GB).",
            "Verify this is intentional. Requesting excessive memory can delay scheduling.",
            line_number=lineno, line_content=line
        ))


def _parse_wall_time_hours(t: str) -> Optional[float]:
    """
    Parse a Slurm time string and return hours as a float.

    Supported formats:
        D-HH:MM:SS, HH:MM:SS, MM:SS, MM

    Returns None if no format matches.
    Helper for check_wall_time — not a standalone check.
    """
    t = t.strip()

    m = re.match(r"^(\d+)-(\d+):(\d+):(\d+)$", t)  # D-HH:MM:SS
    if m:
        return int(m.group(1))*24 + int(m.group(2)) + int(m.group(3))/60 + int(m.group(4))/3600

    m = re.match(r"^(\d+):(\d+):(\d+)$", t)  # HH:MM:SS
    if m:
        return int(m.group(1)) + int(m.group(2))/60 + int(m.group(3))/3600

    m = re.match(r"^(\d+):(\d+)$", t)  # MM:SS
    if m:
        return int(m.group(1))/60 + int(m.group(2))/3600

    m = re.match(r"^(\d+)$", t)  # minutes only
    if m:
        return int(m.group(1))/60

    return None


def check_wall_time(d: dict, result: ValidationResult):
    """
    Verify wall time is present, parseable, non-zero, and within partition limits.

    Without wall time, Slurm uses partition default which may be shorter than needed.
    Zero wall time kills the job immediately. Excessively long times may be rejected.
    """
    time_key = next((k for k in ["time", "t"] if k in d), None)

    if not time_key:
        result.issues.append(Issue(
            Severity.ERROR, "Resource Requests",
            "No wall time specified (--time / -t).",
            "Add '#SBATCH --time=HH:MM:SS'. Without it, the partition default applies "
            "and your job may be killed earlier than expected."
        ))
        return

    val, lineno, line = d[time_key]

    if not val:
        result.issues.append(Issue(
            Severity.ERROR, "Resource Requests",
            "--time is present but has no value.",
            "Specify a duration, e.g. '#SBATCH --time=04:00:00' for 4 hours.",
            line_number=lineno, line_content=line
        ))
        return

    hours = _parse_wall_time_hours(val)

    if hours is None:
        result.issues.append(Issue(
            Severity.ERROR, "Resource Requests",
            f"Wall time '{val}' could not be parsed.",
            "Use the format D-HH:MM:SS, HH:MM:SS, MM:SS, or just MM.",
            line_number=lineno, line_content=line
        ))
    elif hours == 0:
        # Valid syntax but job is killed before it starts.
        result.issues.append(Issue(
            Severity.ERROR, "Resource Requests",
            "Wall time is set to zero.",
            "Specify a non-zero duration. Your job would be killed immediately.",
            line_number=lineno, line_content=line
        ))
    elif hours > MAX_WALL_TIME_HOURS:
        result.issues.append(Issue(
            Severity.WARNING, "Resource Requests",
            f"Wall time ({val}) exceeds {MAX_WALL_TIME_HOURS} hours.",
            "Many PACE partitions cap wall time. Check the partition limit and split "
            "long jobs into checkpointed segments if needed.",
            line_number=lineno, line_content=line
        ))
    elif hours > WARN_WALL_TIME_HOURS:
        # Over 7 days is allowed on some partitions but unusual enough to flag.
        result.issues.append(Issue(
            Severity.INFO, "Resource Requests",
            f"Wall time ({val}) is more than 7 days. Make sure this is intentional.",
            "Consider using checkpointing if your job supports it."
        ))


def check_cpus(d: dict, result: ValidationResult):
    """
    Verify a CPU count is specified and is a valid positive integer.

    Slurm defaults to 1 CPU per task without an explicit request — fine for
    single-threaded jobs but wrong for multithreaded or MPI workloads.
    Accepts --ntasks, -n, --ntasks-per-node, --cpus-per-task, -c.
    """
    cpu_key = next((k for k in ["ntasks", "n", "ntasks_per_node", "cpus_per_task", "c"] if k in d), None)

    if not cpu_key:
        result.issues.append(Issue(
            Severity.WARNING, "Resource Requests",
            "No CPU count specified (--ntasks, --cpus-per-task, etc.).",
            "Add '#SBATCH --ntasks=1' for single-process jobs or "
            "'#SBATCH --cpus-per-task=N' for multithreaded jobs."
        ))
        return

    val, lineno, line = d[cpu_key]

    if not val or not val.isdigit():
        result.issues.append(Issue(
            Severity.ERROR, "Resource Requests",
            f"--{cpu_key.replace('_','-')} has no valid integer value.",
            "Specify an integer count, e.g. '#SBATCH --ntasks=4'.",
            line_number=lineno, line_content=line
        ))
        return

    n = int(val)

    if n <= 0:
        result.issues.append(Issue(
            Severity.ERROR, "Resource Requests",
            f"CPU count must be at least 1 (got {n}).",
            "Set a positive integer for the CPU count.",
            line_number=lineno, line_content=line
        ))
    elif n > 1024:
        # Soft threshold — valid on some clusters but almost always a mistake.
        result.issues.append(Issue(
            Severity.WARNING, "Resource Requests",
            f"Requesting {n} CPUs is very high. Verify this is correct.",
            "Most jobs use 1–32 CPUs. Overly large requests can sit in the queue for a long time.",
            line_number=lineno, line_content=line
        ))


def check_gpus(d: dict, result: ValidationResult):
    """
    Cross-validate GPU resource requests against the selected partition.

    Two failure modes:
        1. GPU requested on a CPU-only partition -> ERROR (job will be rejected)
        2. GPU partition selected but no GPU requested -> WARNING (wastes node slot)

    Also validates --gres format since malformed GRES strings are a common mistake.
    Relies on result.directives["_partition"] set by check_partition.
    """
    gpu_key = next((k for k in ["gpus", "gres", "gpus_per_node", "gpus_per_task"] if k in d), None)
    partition = result.directives.get("_partition", "")  # Empty if partition wasn't set/recognized.

    if gpu_key:
        val, lineno, line = d[gpu_key]

        # GPU requested on a CPU-only partition — Slurm will reject this job.
        if partition and partition in CPU_ONLY_PARTITIONS:
            result.issues.append(Issue(
                Severity.ERROR, "Resource Requests",
                f"GPU requested via --{gpu_key.replace('_','-')} but partition '{partition}' "
                "does not have GPUs.",
                f"Switch to a GPU partition (e.g. 'gpu-medium') or remove the GPU request.",
                line_number=lineno, line_content=line
            ))

        # Validate --gres format: expected "gpu[:type]:count" e.g. "gpu:1" or "gpu:v100:2"
        if gpu_key == "gres" and val:
            if not re.match(r"gpu(:[a-zA-Z0-9_]+)?:\d+", val):
                result.issues.append(Issue(
                    Severity.WARNING, "Resource Requests",
                    f"--gres value '{val}' does not look like a standard GPU GRES string.",
                    "Typical format: '--gres=gpu:1' or '--gres=gpu:v100:2'.",
                    line_number=lineno, line_content=line
                ))
    else:
        # GPU partition selected but no GPU requested — job lands on GPU node without GPU access.
        # This wastes an expensive resource and may cause the job to silently underperform.
        if partition and partition in GPU_PARTITIONS:
            result.issues.append(Issue(
                Severity.WARNING, "Resource Requests",
                f"Partition '{partition}' has GPUs, but no GPU resource is requested "
                "(--gpus, --gres, etc.).",
                "Add '#SBATCH --gpus=1' or '--gres=gpu:1' to actually use the GPU nodes."
            ))


def check_output_files(d: dict, result: ValidationResult):
    """
    Check that stdout and stderr log files are configured.

    Without --output, Slurm writes to slurm-<jobid>.out in the working directory.
    Without --error, stderr is merged into stdout.
    Separating them with explicit paths makes debugging significantly easier.

    Also warns if the output path's parent directory may not exist at submit time —
    Slurm will fail silently if it can't open the log file.
    """
    has_output = "output" in d or "o" in d
    has_error  = "error"  in d or "e" in d

    if not has_output:
        result.issues.append(Issue(
            Severity.WARNING, "Output & Error Files",
            "No output file specified (--output / -o).",
            "Add '#SBATCH --output=logs/%j.out' to capture stdout. "
            "Without it, output goes to slurm-<jobid>.out in the submission directory."
        ))
    else:
        val, lineno, line = d.get("output") or d.get("o")
        if val and "/" in val:
            # Slurm won't create missing directories — the job fails to open the log file.
            parent = Path(val).parent
            result.issues.append(Issue(
                Severity.INFO, "Output & Error Files",
                f"Output file is set to '{val}'. Make sure the directory '{parent}' exists before submission.",
                f"Create it with: mkdir -p {parent}"
            ))

    if not has_error:
        result.issues.append(Issue(
            Severity.INFO, "Output & Error Files",
            "No separate error file specified (--error / -e).",
            "Add '#SBATCH --error=logs/%j.err' to separate stderr from stdout, "
            "making debugging much easier."
        ))


def check_environment(all_lines: list, d: dict, result: ValidationResult):
    """
    Scan the script body for environment setup issues.

    Checks for:
        - Missing module loads or environment activation (conda/venv)
        - 'module purge' without subsequent 'module load'
        - 'cd ~' (home directory has limited quota on PACE)
        - '$HOME/scratch' path (PACE scratch is $SCRATCH, not $HOME/scratch)
        - Missing email notification directives

    Uses regex on the full script text since these are shell commands,
    not #SBATCH directives.
    """
    content = "\n".join(ln for _, ln in all_lines)

    # Three common ways to activate a software environment on PACE.
    has_module_load = bool(re.search(r"^\s*module\s+(load|add)\s+\S+", content, re.MULTILINE))
    has_conda       = bool(re.search(r"conda\s+activate", content))
    has_venv        = bool(re.search(r"source\s+\S+/activate", content))

    if not has_module_load and not has_conda and not has_venv:
        # No env setup — job will likely fail because required software won't be available.
        result.issues.append(Issue(
            Severity.WARNING, "Environment Setup",
            "No module loads or environment activation detected.",
            "Add 'module load <module>' lines before your executable, or activate a conda/venv "
            "environment. Otherwise your job may fail due to missing software."
        ))

    # 'module purge' clears all loaded modules. Without subsequent loads, env is empty.
    if re.search(r"^\s*module\s+purge", content, re.MULTILINE) and not has_module_load:
        result.issues.append(Issue(
            Severity.WARNING, "Environment Setup",
            "'module purge' found but no 'module load' follows it.",
            "After purging, reload the modules your job needs."
        ))

    # Home directory has tight storage quota on PACE — large outputs can fill it.
    if re.search(r"^\s*cd\s+~", content, re.MULTILINE):
        result.issues.append(Issue(
            Severity.INFO, "Environment Setup",
            "Script changes to home directory (~). PACE home directories have limited quota.",
            "Run computationally intensive jobs from $SCRATCH or your project storage instead."
        ))

    # $HOME/scratch is a common mistake — PACE scratch is at $SCRATCH.
    if re.search(r"\$HOME/scratch", content):
        result.issues.append(Issue(
            Severity.INFO, "Environment Setup",
            "Path contains '$HOME/scratch'. On PACE, scratch is typically at $SCRATCH.",
            "Use '$SCRATCH' or the full path to your scratch directory."
        ))

    # Email notifications are optional but strongly recommended for long-running jobs.
    if "mail_user" not in d and "mail_type" not in d:
        result.issues.append(Issue(
            Severity.INFO, "Environment Setup",
            "No email notification configured (--mail-user / --mail-type).",
            "Add '#SBATCH --mail-user=your@gatech.edu' and "
            "'#SBATCH --mail-type=END,FAIL' to get notified when your job finishes or fails."
        ))


def check_account(d: dict, result: ValidationResult):
    """
    Verify that a PACE account is specified.

    The account determines which research group's allocation is charged.
    Without it, Slurm may use a default account that causes accounting errors
    or job rejection.
    """
    if "account" not in d and "A" not in d:
        result.issues.append(Issue(
            Severity.WARNING, "Parameter Configuration",
            "No account specified (--account / -A).",
            "Add '#SBATCH --account=<your-PACE-account>' to charge the right project. "
            "Use 'pace-check-queue' to see your available accounts."
        ))


def check_duplicate_directives(all_lines: list, result: ValidationResult):
    """
    Detect duplicate #SBATCH directives in the same script.

    Slurm uses the last value seen when a directive appears more than once.
    This is almost always unintentional — common cause is copy-paste from another script.
    """
    seen = {}  # Maps directive name -> line number of first occurrence.

    for lineno, line in all_lines:
        m = re.match(r"^#SBATCH\s+--?([\w-]+)", line.strip())
        if m:
            key = m.group(1).lower()
            if key in seen:
                result.issues.append(Issue(
                    Severity.WARNING, "Structure",
                    f"Duplicate directive '--{key}' found (first at line {seen[key]}, again at line {lineno}).",
                    "Remove the duplicate. Slurm uses the last value seen, which may not be what you intended.",
                    line_number=lineno, line_content=line
                ))
            else:
                seen[key] = lineno


def check_executable(all_lines: list, result: ValidationResult):
    """
    Verify the script contains at least one executable command after the #SBATCH block.

    A script with only directives and no commands is valid Slurm syntax but does nothing.
    Common when a script is still being written and the actual command hasn't been added.
    """
    sbatch_block = True   # True while still in the leading #SBATCH section.
    has_command = False

    for _, line in all_lines:
        stripped = line.strip()

        if sbatch_block and stripped.startswith("#SBATCH"):
            continue  # Still in the directive block.

        if stripped.startswith("#") or not stripped:
            continue  # Skip comments and blank lines anywhere in the file.

        sbatch_block = False  # First non-comment, non-empty line ends the directive block.

        if not stripped.startswith("#"):
            has_command = True
            break

    if not has_command:
        result.issues.append(Issue(
            Severity.ERROR, "Structure",
            "No executable command found after the #SBATCH directives.",
            "Add the command(s) you want Slurm to run, e.g. 'python train.py' or 'srun ./my_program'."
        ))


# ──────────────────────────────────────────────
# Main validation runner
# ──────────────────────────────────────────────

def validate(path: Path) -> ValidationResult:
    """
    Run all checks against a single Slurm script and return the results.

    Check order is intentional:
        1. Structure (shebang, duplicates) — file-level issues first
        2. Parameters (name, partition, QoS, account) — scheduler-rejection issues
        3. Resources (time, memory, CPUs, GPUs) — runtime failure issues
        4. Output/environment — debugging and setup issues
        5. Executable — catch empty scripts last

    Never raises for script content issues — all problems become Issue objects.
    """
    result = ValidationResult(script_path=str(path))

    # Can't run any checks if the file can't be read.
    try:
        directives, all_lines = parse_script(path)
    except (OSError, PermissionError) as exc:
        result.issues.append(Issue(
            Severity.ERROR, "File", f"Cannot read script: {exc}",
            "Check that the file path is correct and you have read permissions."
        ))
        return result

    # Each function appends Issues to result.issues in place.
    check_shebang(all_lines, result)
    check_duplicate_directives(all_lines, result)
    check_job_name(directives, result)
    check_partition(directives, result)          # Must run before check_gpus (sets _partition).
    check_qos(directives, result)
    check_account(directives, result)
    check_wall_time(directives, result)
    check_memory(directives, result)
    check_cpus(directives, result)
    check_gpus(directives, result)               # Reads _partition set by check_partition.
    check_output_files(directives, result)
    check_environment(all_lines, directives, result)
    check_executable(all_lines, result)

    return result


# ──────────────────────────────────────────────
# Output formatter
# ──────────────────────────────────────────────

def c(text: str, color: str) -> str:
    """
    Wrap text in ANSI color escape codes.
    Skips coloring when stdout is not a TTY so piped output stays clean.
    """
    if not sys.stdout.isatty():
        return text
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def print_report(result: ValidationResult, verbose: bool = False):
    """
    Print a human-readable validation report to stdout.

    Issues are grouped by category and each entry shows:
        - Severity icon + label (colored)
        - Problem description
        - Offending line if available
        - Fix suggestion

    Summary bar shows error/warning/info counts and PASS/FAIL verdict.
    PASS = zero errors. Warnings alone do not fail unless --strict is used.
    """
    width = 72

    print()
    print(c("━" * width, "bold"))
    print(c("  PACE Job Script Validator", "bold"))
    print(c(f"  {result.script_path}", "dim"))
    print(c("━" * width, "bold"))
    print()

    if not result.issues:
        print(c("  ✔  No issues found. Script looks good!", "green"))
    else:
        # Group issues by category to keep related findings together.
        categories = {}
        for issue in result.issues:
            categories.setdefault(issue.category, []).append(issue)

        for cat, issues in categories.items():
            print(c(f"  ▸ {cat}", "bold"))
            for issue in issues:
                icon  = SEV_ICON[issue.severity]
                color = SEV_COLOR[issue.severity]
                sev   = issue.severity.value

                print(f"    {c(icon, color)} {c(sev, color)}  {issue.message}")
                if issue.line_number:
                    # Show the offending line to help the user find it quickly.
                    print(c(f"         Line {issue.line_number}: {issue.line_content}", "dim"))
                print(c(f"         → {issue.suggestion}", "cyan"))
                print()

    # Summary bar
    e = len(result.errors)
    w = len(result.warnings)
    i = len(result.infos)

    print(c("─" * width, "dim"))
    parts = []
    if e: parts.append(c(f"{e} error{'s' if e!=1 else ''}", "red"))
    if w: parts.append(c(f"{w} warning{'s' if w!=1 else ''}", "yellow"))
    if i: parts.append(c(f"{i} info", "cyan"))
    if not parts: parts = [c("0 issues", "green")]

    status = c("✗  FAIL", "red") if not result.passed else c("✔  PASS", "green")
    print(f"  {status}  —  " + "  ·  ".join(parts))
    print(c("━" * width, "bold"))
    print()


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """
    Build and return the argument parser.

    Flags:
        scripts        -- one or more script paths to validate (positional, required)
        --strict       -- treat warnings as failures (good for CI enforcement)
        --exit-code    -- exit 1 on any errors (enables pipeline integration)
        --verbose/-v   -- reserved for future use
        --summary-only -- one-line PASS/FAIL per script, no details
    """
    p = argparse.ArgumentParser(
        prog="pace_validator",
        description="Validate Slurm job scripts before submitting to PACE.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pace_validator.py job.sh
  python pace_validator.py job.sh --strict
  python pace_validator.py *.sh --exit-code
        """
    )
    p.add_argument("scripts", nargs="+", metavar="SCRIPT",
                   help="One or more Slurm job scripts to validate.")
    p.add_argument("--strict", action="store_true",
                   help="Treat warnings as errors (non-zero exit if any warnings).")
    p.add_argument("--exit-code", action="store_true",
                   help="Exit with code 1 if any errors are found (useful in CI).")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Show additional detail.")
    p.add_argument("--summary-only", action="store_true",
                   help="Print only the pass/fail summary line, no details.")
    return p


def main():
    """
    CLI entry point.

    Validates each provided script and prints a full report or summary line.

    Exit behavior:
        Default     : exits 0 regardless of findings
        --exit-code : exits 1 if any script has errors
        --strict    : also exits 1 if any script has warnings
    """
    parser = build_parser()
    args = parser.parse_args()

    all_passed = True  # Tracks overall pass/fail across all scripts for --exit-code.

    for script_str in args.scripts:
        path = Path(script_str)

        if not path.exists():
            # Print to stderr and keep going so other scripts still get validated.
            print(c(f"  ✗ File not found: {script_str}", "red"), file=sys.stderr)
            all_passed = False
            continue

        result = validate(path)

        if args.summary_only:
            # Compact one-liner — useful for validating many scripts at once.
            status = c("PASS", "green") if result.passed else c("FAIL", "red")
            e, w = len(result.errors), len(result.warnings)
            print(f"{status}  {path}  ({e} errors, {w} warnings)")
        else:
            print_report(result, verbose=args.verbose)

        # Update global pass/fail based on strictness mode.
        if args.strict and (result.errors or result.warnings):
            all_passed = False
        elif result.errors:
            all_passed = False

    if args.exit_code and not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
