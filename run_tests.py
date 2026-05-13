import os
import subprocess
import sys
import time

def main():
    print("Building and deploying .apworld...")
    # 1. run zip-it.py deployap to build and deploy the apworld
    result = subprocess.run([sys.executable, "zip-it.py", "deployap"])
    if result.returncode != 0:
        print("Failed to build with zip-it.py")
        sys.exit(result.returncode)

    print("\nRunning unit tests...")
    # 2. run the unit tests directly as a script
    test_cmd = [sys.executable, "test/test_yamls.py"]
    result = subprocess.run(test_cmd)
    
    if result.returncode != 0:
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
