"""
Unity Editor simulator for automated parameter calibration.

Handles:
- Unity Editor process management
- Parameter export to Unity JSON format
- Simulation result polling
- Timeout and error handling
"""

import os
import sys
import time
import subprocess
import glob
from pathlib import Path
from typing import Optional
import numpy as np

# Import from existing scripts
sys.path.append(str(Path(__file__).parent.parent))
from export_to_unity import export_to_unity_json, generate_experiment_id
from core.parameter_utils import params_array_to_dict


class UnitySimulator:
    """
    Unity Editor automation for running calibration simulations.

    This class encapsulates all Unity-related operations:
    - Finding Unity Editor executable
    - Launching Unity with automation method
    - Polling for simulation results
    - Process cleanup and timeout handling

    Example:
        simulator = UnitySimulator()
        result_path = simulator.run_simulation(params, "exp_001")
        # Result file created at result_path
    """

    def __init__(
        self,
        unity_editor_path: Optional[str] = None,
        project_path: Optional[str] = None,
        timeout: int = 600
    ):
        """
        Initialize Unity simulator.

        Args:
            unity_editor_path: Path to Unity.exe (None = auto-detect)
            project_path: Path to Unity project (None = use default)
            timeout: Timeout in seconds for simulation completion (default: 600 = 10min)
        """
        self.unity_path = unity_editor_path or self._find_unity_editor()
        self.project_path = project_path or r"D:\UnityProjects\META_VERYOLD_P01_s"
        self.timeout = timeout

        # Paths
        self.input_dir = Path(self.project_path) / "Assets/StreamingAssets/Calibration/Input"
        self.output_dir = Path(self.project_path) / "Assets/StreamingAssets/Calibration/Output"
        self.result_file = self.output_dir / "simulation_result.json"

        # Ensure directories exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"[UnitySimulator] Initialized")
        print(f"  Unity Editor: {self.unity_path}")
        print(f"  Project:      {self.project_path}")
        print(f"  Timeout:      {self.timeout}s")

    def _find_unity_editor(self) -> str:
        """
        Find Unity Editor executable automatically.

        Search order:
        1. Environment variable UNITY_EDITOR_PATH
        2. Common Unity Hub installation paths
        3. User input

        Returns:
            Path to Unity.exe

        Raises:
            FileNotFoundError: If Unity Editor not found
        """
        # Check environment variable
        env_path = os.environ.get("UNITY_EDITOR_PATH")
        if env_path and os.path.exists(env_path):
            print(f"[UnitySimulator] Found Unity from environment: {env_path}")
            return env_path

        # Search common Unity Hub paths
        search_patterns = [
            r"C:\Program Files\Unity\Hub\Editor\*\Editor\Unity.exe",
            r"C:\Program Files (x86)\Unity\Hub\Editor\*\Editor\Unity.exe",
        ]

        for pattern in search_patterns:
            matches = glob.glob(pattern)
            if matches:
                # Use latest version (lexicographically)
                latest = sorted(matches)[-1]
                print(f"[UnitySimulator] Found Unity: {latest}")
                return latest

        # Not found - ask user
        print("[UnitySimulator] Unity Editor not found automatically")
        print("Please enter path to Unity.exe manually:")
        print("Example: C:\\Program Files\\Unity\\Hub\\Editor\\2021.3.0f1\\Editor\\Unity.exe")
        user_path = input("Unity.exe path: ").strip().strip('"')

        if os.path.exists(user_path):
            return user_path

        raise FileNotFoundError(
            "Unity Editor not found. Set UNITY_EDITOR_PATH environment variable or install Unity Hub."
        )

    def run_simulation(
        self,
        params: np.ndarray,
        experiment_id: Optional[str] = None
    ) -> str:
        """
        Run Unity simulation with given parameters.

        Workflow:
        1. Export parameters to Unity JSON
        2. Delete old result file
        3. Launch Unity Editor
        4. Poll for result file creation
        5. Terminate Unity process
        6. Return result file path

        Args:
            params: Parameter array (18 values)
            experiment_id: Experiment ID (None = auto-generate)

        Returns:
            Path to simulation_result.json

        Raises:
            TimeoutError: If simulation doesn't complete within timeout
            RuntimeError: If Unity crashes or produces invalid results
        """
        # Generate experiment ID if not provided
        if experiment_id is None:
            experiment_id = generate_experiment_id(prefix="auto")

        print(f"\n{'='*80}")
        print(f"[UnitySimulator] Starting simulation: {experiment_id}")
        print(f"{'='*80}")

        # Step 1: Export parameters to Unity JSON
        param_dict = params_array_to_dict(params)
        input_file = self.input_dir / f"{experiment_id}_parameters.json"

        export_to_unity_json(
            params=param_dict,
            output_path=str(input_file),
            experiment_id=experiment_id
        )
        print(f"[UnitySimulator] Parameters exported: {input_file.name}")

        # Step 2: Delete old result file
        if self.result_file.exists():
            self.result_file.unlink()
            print(f"[UnitySimulator] Deleted old result file")

        # Step 3: Launch Unity Editor
        process = self._launch_unity()

        # Step 4: Poll for result file
        try:
            self._wait_for_result(process)
        except (TimeoutError, RuntimeError) as e:
            # Kill Unity if still running
            if process.poll() is None:
                print(f"[UnitySimulator] Terminating Unity process...")
                process.kill()
                process.wait(timeout=10)
            raise e

        # Step 5: Terminate Unity process
        if process.poll() is None:
            print(f"[UnitySimulator] Terminating Unity process...")
            process.terminate()
            process.wait(timeout=30)

        print(f"[UnitySimulator] Simulation complete: {experiment_id}")
        print(f"{'='*80}\n")

        return str(self.result_file)

    def _launch_unity(self) -> subprocess.Popen:
        """
        Launch Unity Editor with automation method.

        Returns:
            subprocess.Popen object
        """
        cmd = [
            self.unity_path,
            "-projectPath", self.project_path,
            "-executeMethod", "Calibration_hybrid_AutomationController.RunCalibrationSimulation",
            "-logFile", "-"  # Log to stdout (captured by Popen)
        ]

        print(f"[UnitySimulator] Launching Unity Editor...")
        print(f"[UnitySimulator] Method: Calibration_hybrid_AutomationController.RunCalibrationSimulation")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"[UnitySimulator] Unity process started (PID: {process.pid})")
        return process

    def _wait_for_result(self, process: subprocess.Popen):
        """
        Poll for simulation result file creation.

        Args:
            process: Unity process to monitor

        Raises:
            TimeoutError: If result file not created within timeout
            RuntimeError: If Unity process exits with error
        """
        print(f"[UnitySimulator] Waiting for result file...")
        print(f"[UnitySimulator] Polling: {self.result_file}")
        print(f"[UnitySimulator] Timeout: {self.timeout}s")

        start_time = time.time()
        check_interval = 2  # seconds

        while True:
            # Check if result file created
            if self.result_file.exists():
                elapsed = time.time() - start_time
                print(f"[UnitySimulator] Result file created after {elapsed:.1f}s")
                return

            # Check if Unity process crashed
            if process.poll() is not None:
                exit_code = process.returncode
                print(f"[UnitySimulator] ERROR: Unity process exited (code: {exit_code})")

                # Try to read stderr
                stderr = process.stderr.read() if process.stderr else ""
                if stderr:
                    print(f"[UnitySimulator] Unity stderr:\n{stderr}")

                raise RuntimeError(
                    f"Unity process exited unexpectedly with code {exit_code}"
                )

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > self.timeout:
                raise TimeoutError(
                    f"Simulation timeout after {self.timeout}s. "
                    f"Result file not created: {self.result_file}"
                )

            # Print progress
            if int(elapsed) % 30 == 0 and int(elapsed) > 0:
                print(f"[UnitySimulator] Still waiting... ({elapsed:.0f}s elapsed)")

            # Wait before next check
            time.sleep(check_interval)

    def cleanup(self):
        """
        Cleanup resources (if needed).

        Currently no persistent resources to clean up.
        """
        pass


def test_unity_simulator():
    """
    Test Unity simulator with baseline parameters.

    Run this to verify Unity automation works before using in optimization.
    """
    print("="*80)
    print("UNITY SIMULATOR TEST")
    print("="*80)

    # Import baseline parameters
    from core.parameter_utils import get_baseline_parameters, params_dict_to_array

    baseline = get_baseline_parameters()
    params = params_dict_to_array(baseline)

    print(f"Testing with baseline parameters")
    print(f"Parameters: {list(baseline.keys())[:3]}... ({len(baseline)} total)")

    # Create simulator
    simulator = UnitySimulator(timeout=600)

    # Run simulation
    try:
        result_path = simulator.run_simulation(params, experiment_id="test_simulator")
        print(f"\n[TEST] SUCCESS!")
        print(f"[TEST] Result file: {result_path}")

        # Verify result file
        import json
        with open(result_path) as f:
            result = json.load(f)

        print(f"[TEST] Experiment ID: {result.get('experimentId')}")
        print(f"[TEST] Successful: {result.get('successful')}")
        print(f"[TEST] Total Agents: {result.get('totalAgents')}")

    except Exception as e:
        print(f"\n[TEST] FAILED: {e}")
        raise

    finally:
        simulator.cleanup()


if __name__ == '__main__':
    # Run test
    test_unity_simulator()
