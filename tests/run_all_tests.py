import unittest
import sys
import os

def run_suite():
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n==========================================")
    print("PROJECT AURA RELEASE GATES VERIFICATION:")
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("==========================================")

    if result.wasSuccessful():
        print(">> ALL AURA RELEASE GATES & CAPABILITY INVARIANTS SATISFIED <<")
        sys.exit(0)
    else:
        print(">> RELEASE GATE FAILURE DETECTED <<")
        sys.exit(1)

if __name__ == "__main__":
    run_suite()
