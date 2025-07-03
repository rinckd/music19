#!/usr/bin/env python3
"""
Parallel test runner for unittest-based tests
"""
import sys
import subprocess
import concurrent.futures
from pathlib import Path
import time

def run_test_file(test_file):
    """Run a single test file and return results"""
    start_time = time.time()
    try:
        result = subprocess.run([
            sys.executable, '-m', 'unittest', 
            test_file.replace('/', '.').replace('.py', ''), '-v'
        ], capture_output=True, text=True, timeout=300)
        
        duration = time.time() - start_time
        return {
            'file': test_file,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': duration
        }
    except subprocess.TimeoutExpired:
        return {
            'file': test_file,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Test timed out after 5 minutes',
            'duration': time.time() - start_time
        }

def main():
    test_dir = Path('tests/unit')
    test_files = list(test_dir.glob('test_*.py'))
    
    print(f"Found {len(test_files)} test files")
    print("Running tests in parallel...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(run_test_file, str(f)): f for f in test_files}
        
        passed = 0
        failed = 0
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            
            if result['returncode'] == 0:
                passed += 1
                print(f"✅ {result['file']} ({result['duration']:.2f}s)")
            else:
                failed += 1
                print(f"❌ {result['file']} ({result['duration']:.2f}s)")
                if result['stderr']:
                    print(f"   Error: {result['stderr'][:200]}...")
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed

if __name__ == '__main__':
    sys.exit(main())