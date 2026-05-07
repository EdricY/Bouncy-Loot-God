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

    # 2. give the Archipelago launcher a few seconds to install the apworld
    time.sleep(5)

    print("\nRunning unit tests...")
    # 3. run the unit tests directly as a script
    test_cmd = [sys.executable, "worlds/borderlands2/test/test_yamls.py"]
    result = subprocess.run(test_cmd)
    
    if result.returncode != 0:
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
