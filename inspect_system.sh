#!/usr/bin/env bash
# Previously used read-only setup checks, saved together for reuse.
echo "=== UBUNTU ==="
lsb_release -a

echo "=== GPU ==="
nvidia-smi

echo "=== MEMORY ==="
free -h

echo "=== DISK SPACE ==="
df -h /

echo "=== PYTHON ==="
python3 --version
command -v python3

echo "=== ACTIVE PYTHON ENVIRONMENT ==="
printenv VIRTUAL_ENV CONDA_DEFAULT_ENV

echo "=== RUNNING CARLA PROCESSES ==="
pgrep -af 'CarlaUE4|CarlaUnreal|CarlaUE5'

echo "=== CARLA LAUNCH FILES ==="
find "$HOME" /opt /mnt /media -maxdepth 6 -type f \
  \( -name 'CarlaUE4.sh' -o -name 'CarlaUnreal.sh' -o -name 'CarlaUE5.sh' \) \
  2>/dev/null

echo "=== CONDA ENVIRONMENTS ==="
conda env list
