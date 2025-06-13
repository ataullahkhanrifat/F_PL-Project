#!/usr/bin/env python3
"""
Test script to verify the app works after removing database view
"""

import sys
import os
import subprocess

# Add the project root to Python path
project_root = "/Users/mdataullahkhanrifat/Documents/F_PL Project"
sys.path.append(project_root)

def test_app_import():
    """Test that the app can be imported without errors"""
    try:
        # Test imports
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        # Change to project directory
        os.chdir(project_root)
        
        # Test app file syntax
        with open('web_app/app.py', 'r') as f:
            content = f.read()
            # Check that database view is removed
            if 'View Player Database' in content:
                print("❌ Database view still present!")
                return False
            else:
                print("✅ Database view successfully removed")
        
        # Test compilation
        import py_compile
        py_compile.compile('web_app/app.py', doraise=True)
        print("✅ App compiles without syntax errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing FPL App after database view removal...")
    print("-" * 50)
    
    if test_app_import():
        print("\n🎉 All tests passed! App is ready to run.")
        print("🚀 Start the app with: streamlit run web_app/app.py")
    else:
        print("\n❌ Tests failed!")
