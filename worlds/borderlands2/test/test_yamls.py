import os
import shutil
import tempfile
import subprocess
import unittest

EXE_PATH = r"C:\ProgramData\Archipelago\ArchipelagoGenerate.exe"
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
YAMLS_DIR = os.path.join(TEST_DIR, "yamls")
PASS_DIR = os.path.join(YAMLS_DIR, "pass")
FAIL_DIR = os.path.join(YAMLS_DIR, "fail")
REPO_ROOT = os.path.abspath(os.path.join(TEST_DIR, "..", "..", ".."))
SAMPLE_YAMLS_DIR = os.path.join(REPO_ROOT, "sample-yamls")

def run_archipelago_generate(yaml_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        target_yaml = os.path.join(temp_dir, os.path.basename(yaml_path))
        shutil.copy(yaml_path, target_yaml)

        cmd = [
            EXE_PATH, 
            "--player_files_path", temp_dir,
            "--skip_output" 
        ]
        
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input="\n")
        
        return process.returncode, stdout, stderr

class TestArchipelagoYamls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(EXE_PATH):
            raise unittest.SkipTest(f"ArchipelagoGenerate.exe not found at {EXE_PATH}")

    def test_passing_yamls(self):
        pass_yamls = []
        
        # Collect from sample-yamls
        if os.path.exists(SAMPLE_YAMLS_DIR):
            for f in os.listdir(SAMPLE_YAMLS_DIR):
                if f.endswith(('.yaml', '.yml')):
                    pass_yamls.append(os.path.join(SAMPLE_YAMLS_DIR, f))
                    
        # Collect from test/yamls/pass
        if os.path.exists(PASS_DIR):
            for f in os.listdir(PASS_DIR):
                if f.endswith(('.yaml', '.yml')):
                    pass_yamls.append(os.path.join(PASS_DIR, f))
                    
        if not pass_yamls:
            self.skipTest("No passing YAMLs found")
            
        for yaml_path in pass_yamls:
            filename = os.path.basename(yaml_path)
            with self.subTest(yaml=filename):
                print(f"Expecting PASS for: {filename}...")
                returncode, stdout, stderr = run_archipelago_generate(yaml_path)
                self.assertEqual(
                    returncode, 0, 
                    f"Expected {filename} to PASS, but it failed with code {returncode}.\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                )

    def test_failing_yamls(self):
        if not os.path.exists(FAIL_DIR):
            self.skipTest(f"Fail directory not found: {FAIL_DIR}")
            
        yamls = [f for f in os.listdir(FAIL_DIR) if f.endswith(('.yaml', '.yml'))]
        if not yamls:
            self.skipTest(f"No YAMLs found in {FAIL_DIR}")
            
        for filename in yamls:
            yaml_path = os.path.join(FAIL_DIR, filename)
            with self.subTest(yaml=filename):
                print(f"Expecting FAIL for: {filename}...")
                returncode, stdout, stderr = run_archipelago_generate(yaml_path)
                self.assertNotEqual(
                    returncode, 0, 
                    f"Expected {filename} to FAIL, but it succeeded.\nSTDOUT:\n{stdout}"
                )

if __name__ == '__main__':
    unittest.main()
