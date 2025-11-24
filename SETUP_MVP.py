#!/usr/bin/env python
"""
Quick setup guide for AutoAI Hackathon MVP
Provides interactive setup with helpful guidance
"""

import os
import sys
import subprocess
from pathlib import Path

class AutoAISetup:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.success_count = 0
        
    def print_header(self):
        print("\n" + "="*60)
        print("🚗 AutoAI Hackathon MVP - Setup Guide")
        print("="*60 + "\n")
        
    def check_python(self):
        print("✓ Step 1: Checking Python...")
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"  ✅ Python {version.major}.{version.minor} found\n")
            self.success_count += 1
            return True
        else:
            print(f"  ❌ Python 3.8+ required (found {version.major}.{version.minor})\n")
            return False
    
    def check_dependencies(self):
        print("✓ Step 2: Checking dependencies...")
        required = ['django', 'rest_framework', 'anthropic', 'psycopg2']
        missing = []
        
        for pkg in required:
            try:
                __import__(pkg.replace('-', '_'))
            except ImportError:
                missing.append(pkg)
        
        if not missing:
            print("  ✅ All dependencies installed\n")
            self.success_count += 1
            return True
        else:
            print(f"  ⚠️  Missing: {', '.join(missing)}")
            print(f"  Run: pip install -r requirements.txt\n")
            return False
    
    def check_env(self):
        print("✓ Step 3: Checking environment...")
        env_file = self.project_dir / '.env'
        if env_file.exists():
            print("  ✅ .env file found\n")
            self.success_count += 1
            return True
        else:
            print("  ⚠️  .env file not found")
            print("  Run: cp .env.example .env")
            print("  Then add your ANTHROPIC_API_KEY\n")
            return False
    
    def check_database(self):
        print("✓ Step 4: Checking database...")
        db_file = self.project_dir / 'db.sqlite3'
        if db_file.exists():
            print("  ✅ Database found\n")
            self.success_count += 1
            return True
        else:
            print("  ⚠️  Database not initialized")
            print("  Run:")
            print("    python manage.py migrate")
            print("    python manage.py init_sample_data\n")
            return False
    
    def print_final_status(self):
        print("="*60)
        print(f"Setup Status: {self.success_count}/4 checks passed")
        print("="*60 + "\n")
        
        if self.success_count == 4:
            print("🎉 Setup complete! Ready to run:")
            print("   python manage.py runserver\n")
            print("Then open: http://localhost:8000\n")
        else:
            print("⚠️  Please complete the setup steps above.\n")
    
    def run(self):
        self.print_header()
        self.check_python()
        self.check_dependencies()
        self.check_env()
        self.check_database()
        self.print_final_status()

if __name__ == '__main__':
    setup = AutoAISetup()
    setup.run()
