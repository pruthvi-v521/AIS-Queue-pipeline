#!/usr/bin/env bash
set -euo pipefail

DB="${POSTGRES_DB:-ais}"
USER="${POSTGRES_USER:-appuser}"

echo "Restoring into DB=${DB} as USER=${USER}"
echo "Listing /backups:"
ls -lah /backups || true


if [ -d /backups/restore_dir ] && [ -f /backups/restore_dir/toc.dat ]; then
  echo "Detected directory-format dump at /backups/restore_dir (toc.dat found). Restoring with pg_restore..."
  pg_restore -U "$USER" -d "$DB" --clean --if-exists --no-owner /backups/restore_dir
  echo "Directory-format restore completed."
  exit 0
fi


if [ -f /backups/dump.dump ]; then
  echo "Detected custom-format dump /backups/dump.dump. Restoring with pg_restore..."
  pg_restore -U "$USER" -d "$DB" --clean --if-exists --no-owner /backups/dump.dump
  echo "Custom-format restore completed."
  exit 0
fi


if [ -f /backups/dump.sql ]; then
  echo "Detected plain SQL /backups/dump.sql. Restoring with psql..."
  psql -U "$USER" -d "$DB" -v ON_ERROR_STOP=1 -f /backups/dump.sql
  echo "SQL restore completed."
  exit 0
fi

if [ -f /backups/dump.sql.gz ]; then
  echo "Detected gzipped SQL /backups/dump.sql.gz. Restoring with psql..."
  gunzip -c /backups/dump.sql.gz | psql -U "$USER" -d "$DB" -v ON_ERROR_STOP=1
  echo "Gzipped SQL restore completed."
  exit 0
fi

echo "No supported dump found. Skipping restore."