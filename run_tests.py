#!/usr/bin/env python3
"""
Test runner for Morse Code Decoder API
Runs all tests and provides coverage summary
"""

import sys
import unittest
import coverage
import os

def run_tests_with_coverage():
    """Run tests with coverage analysis"""
    print("=" * 60)
    print("MORSE CODE DECODER API - TEST SUITE")
    print("=" * 60)
    
    # Start coverage measurement
    cov = coverage.Coverage()
    cov.start()
    
    # Load and run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('test_app')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Stop coverage measurement
    cov.stop()
    cov.save()
    
    # Print coverage report
    print("\n" + "=" * 60)
    print("COVERAGE REPORT")
    print("=" * 60)
    
    cov.report()
    
    # Get coverage percentage
    total_coverage = cov.report()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    # Determine overall success
    success = result.wasSuccessful()
    if success:
        print("\n✅ ALL TESTS PASSED!")
        print("🚀 Ready for deployment!")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("🔧 Please fix the issues before deployment.")
    
    return success

def run_quick_tests():
    """Run a quick smoke test"""
    print("=" * 60)
    print("QUICK SMOKE TEST")
    print("=" * 60)
    
    # Import and test basic functionality
    try:
        from app import app, load_morse_mapping, morse_to_text, extract_flag
        
        # Test basic imports
        print("✅ All modules imported successfully")
        
        # Test app creation
        test_app = app.test_client()
        print("✅ Flask app created successfully")
        
        # Test health endpoint
        response = test_app.get('/health')
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print("❌ Health endpoint failed")
            return False
        
        # Test basic Morse decoding
        load_morse_mapping()
        result = morse_to_text(".... . .-.. .-.. ---")
        if result == "HELLO":
            print("✅ Basic Morse decoding working")
        else:
            print("❌ Basic Morse decoding failed")
            return False
        
        # Test flag extraction
        flag = extract_flag("FLAG{test}")
        if flag == "FLAG{test}":
            print("✅ Flag extraction working")
        else:
            print("❌ Flag extraction failed")
            return False
        
        print("\n✅ QUICK TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        success = run_quick_tests()
    else:
        success = run_tests_with_coverage()
    
    sys.exit(0 if success else 1) 