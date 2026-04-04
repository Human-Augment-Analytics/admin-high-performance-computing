# Script Developed By:
# Wai Lung Justin Yiu | Georgia Tech | HAAG Admin | OMSCS | CS 6999 Spring 2026

#SBATCH --job-name=storage-audit-once
#SBATCH --partition=ice-cpu
#SBATCH --qos=coc-ice
#SBATCH --account=coc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=02:00:00
#SBATCH --output=/storage/ice-shared/cs8903onl/storage_audit_once.%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=wyiu31@gatech.edu

set -euo pipefail

TARGET_DIR="/storage/ice-shared/cs8903onl"
SCRIPT_PATH="${TARGET_DIR}/storage_audit_script.py"
REPORT_PATH="${TARGET_DIR}/storage_audit_report_$(date +%Y%m%d).txt"
EMAIL_TO="first_person@gatech.edu second_person@gatech.edu"

python "${SCRIPT_PATH}"

if [[ ! -f "${REPORT_PATH}" ]]; then
  echo "Expected report not found: ${REPORT_PATH}" >&2
  exit 1
fi

mail -s "Storage audit report $(date +%Y-%m-%d)" "${EMAIL_TO}" < "${REPORT_PATH}"
echo "Sent ${REPORT_PATH} to ${EMAIL_TO}"
