#!/usr/bin/env bash
set -euo pipefail
: "${DATABASE_URL:?Set DATABASE_URL}"
: "${BACKUP_DIR:=./backups}"
mkdir -p "$BACKUP_DIR"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
case "$DATABASE_URL" in
  postgresql://*|postgresql+psycopg2://*)
    URL=${DATABASE_URL#*://}
    HOSTPART=${URL#*@}; HOST=${HOSTPART%%/*}; DB=${HOSTPART#*/}; DB=${DB%%\?*}
    USERPASS=${URL%%@*}; USER=${USERPASS%%:*}; PASS=${USERPASS#*:}
    PGPASSWORD="$PASS" pg_dump -Fc -h "$HOST" -U "$USER" "$DB" > "$BACKUP_DIR/qtransplant-$STAMP.dump"
    ;;
  sqlite:///*)
    DBFILE=${DATABASE_URL#sqlite:///}
    cp --reflink=auto "$DBFILE" "$BACKUP_DIR/qtransplant-$STAMP.sqlite"
    ;;
  *) echo "Unsupported DATABASE_URL for backup" >&2; exit 2;;
esac
printf '%s\n' "$BACKUP_DIR/qtransplant-$STAMP.*"
