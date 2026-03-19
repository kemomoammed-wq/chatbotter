#!/usr/bin/env python
"""
Script بسيط لتشغيل database migrations
استخدام:
    python run_migrations.py          # تطبيق جميع migrations
    python run_migrations.py --init   # إنشاء initial migration
    python run_migrations.py --upgrade # تطبيق migrations
    python run_migrations.py --downgrade # التراجع عن آخر migration
"""

import sys
import subprocess
import os

def run_command(cmd):
    """تشغيل أمر Alembic"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr, file=sys.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        print(f"Output: {e.stdout}", file=sys.stderr)
        print(f"Error: {e.stderr}", file=sys.stderr)
        return False

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--init":
            print("📝 Creating initial migration...")
            if run_command('alembic revision --autogenerate -m "Initial migration"'):
                print("✅ Initial migration created!")
                print("💡 Run 'python run_migrations.py --upgrade' to apply it.")
        elif sys.argv[1] == "--upgrade":
            print("⬆️  Upgrading database...")
            if run_command("alembic upgrade head"):
                print("✅ Database upgraded successfully!")
        elif sys.argv[1] == "--downgrade":
            print("⬇️  Downgrading database...")
            if run_command("alembic downgrade -1"):
                print("✅ Database downgraded successfully!")
        elif sys.argv[1] == "--current":
            print("📊 Current migration version:")
            run_command("alembic current")
        elif sys.argv[1] == "--history":
            print("📜 Migration history:")
            run_command("alembic history")
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print(__doc__)
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print(__doc__)
    else:
        # Default: upgrade to head
        print("⬆️  Upgrading database to latest version...")
        if run_command("alembic upgrade head"):
            print("✅ Database migrations applied successfully!")

if __name__ == "__main__":
    main()

