"""
SQLite to PostgreSQL Migration Script
This script helps migrate data from SQLite to PostgreSQL
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dough_re_mi.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.core.management import call_command
from django.conf import settings
import subprocess

def backup_sqlite():
    """Backup existing SQLite database"""
    print("Backing up SQLite database...")
    sqlite_db = settings.BASE_DIR / 'db.sqlite3'
    backup_db = settings.BASE_DIR / 'db.sqlite3.backup'
    
    if sqlite_db.exists():
        import shutil
        shutil.copy2(sqlite_db, backup_db)
        print(f"✓ SQLite database backed up to {backup_db}")
        return True
    else:
        print("✗ SQLite database not found")
        return False

def export_sqlite_data():
    """Export data from SQLite to JSON"""
    print("Exporting data from SQLite...")
    try:
        call_command('dumpdata', indent=2, output='sqlite_data.json')
        print("✓ Data exported to sqlite_data.json")
        return True
    except Exception as e:
        print(f"✗ Error exporting data: {e}")
        return False

def import_postgres_data():
    """Import data to PostgreSQL"""
    print("Importing data to PostgreSQL...")
    try:
        call_command('loaddata', 'sqlite_data.json')
        print("✓ Data imported to PostgreSQL")
        return True
    except Exception as e:
        print(f"✗ Error importing data: {e}")
        return False

def run_migrations():
    """Run Django migrations on PostgreSQL"""
    print("Running migrations on PostgreSQL...")
    try:
        call_command('migrate', '--run-syncdb')
        print("✓ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"✗ Error running migrations: {e}")
        return False

def main():
    print("=" * 60)
    print("SQLite to PostgreSQL Migration Script")
    print("=" * 60)
    
    # Check current database engine
    current_engine = settings.DATABASES['default']['ENGINE']
    print(f"Current database engine: {current_engine}")
    
    if current_engine == 'django.db.backends.sqlite3':
        print("\n⚠ WARNING: You're still using SQLite!")
        print("Please update your .env file to use PostgreSQL before running this script.")
        print("\nExample .env configuration:")
        print("DB_ENGINE=django.db.backends.postgresql")
        print("DB_NAME=dough_re_mi_db")
        print("DB_USER=dough_re_mi_user")
        print("DB_PASSWORD=your_password")
        print("DB_HOST=localhost")
        print("DB_PORT=5432")
        return
    
    print("\nStarting migration process...")
    
    # Step 1: Backup SQLite
    if not backup_sqlite():
        return
    
    # Step 2: Export SQLite data
    if not export_sqlite_data():
        return
    
    # Step 3: Run migrations on PostgreSQL
    if not run_migrations():
        return
    
    # Step 4: Import data to PostgreSQL
    if not import_postgres_data():
        return
    
    print("\n" + "=" * 60)
    print("✓ Migration completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test your application with PostgreSQL")
    print("2. If everything works, you can delete db.sqlite3.backup")
    print("3. Remove sqlite_data.json if no longer needed")

if __name__ == '__main__':
    main()
