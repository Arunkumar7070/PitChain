"""
verify_db.py  — Run AFTER migrations to confirm all tables exist.
Usage: python verify_db.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pitchain.settings.development')
django.setup()

from django.db import connection

EXPECTED_TABLES = [
    'users',
    'ipl_teams',
    'players',
    'player_match_stats',
    'matches',
    'contests',
    'prize_distributions',
    'admin_earnings',
    'user_teams',
    'user_team_players',
]

print("\n" + "=" * 60)
print("🔍  PITCHAIN DB VERIFICATION")
print("=" * 60)

with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES;")
    existing = {row[0] for row in cursor.fetchall()}

all_ok = True
for table in EXPECTED_TABLES:
    exists = table in existing
    status = "✅" if exists else "❌  MISSING"
    print(f"  {status}  {table}")
    if not exists:
        all_ok = False

print("=" * 60)
if all_ok:
    print("✅  All tables present — database is ready!\n")
else:
    print("❌  Some tables are missing — run migrations again.\n")

# Show row counts
print("📊  Row counts (should all be 0 on fresh DB):")
with connection.cursor() as cursor:
    for table in EXPECTED_TABLES:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`;")
            count = cursor.fetchone()[0]
            print(f"     {table:<25} → {count} rows")
        except Exception:
            print(f"     {table:<25} → ⚠️  could not query")
print()
