#!/usr/bin/env python3
"""
AI OS - Phase 1 Dependency Test Script (Windows)
Tests all critical imports and basic functionality
"""

import sys
import importlib

def test_import(module_name):
    try:
        importlib.import_module(module_name)
        print(f"{module_name:15}: ✅ OK")
        return True
    except ImportError as e:
        print(f"{module_name:15}: ❌ FAIL: {e}")
        return False

print("🧪 AI OS Dependency Test")
print("=" * 50)
tests = [
    "torch", "transformers", "spacy", "numpy", "pandas", "sklearn",
    "yaml", "psutil", "schedule", "sqlite3", "PyQt5", "requests", "pytest"
]
passed = 0
for mod in tests:
    if test_import(mod):
        passed += 1

print(f"\n📊 Passed: {passed}/{len(tests)}")
if passed == len(tests):
    print("🎉 All dependencies are working!")
    sys.exit(0)
else:
    print("❌ Some dependencies failed! Please check above.")
    sys.exit(1)
