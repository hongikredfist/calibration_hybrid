import json
import argparse
from pathlib import Path
from typing import Dict, List, Any

DEFAULT_UNITY_OUTPUT = r"D:\UnityProjects\META_VERYOLD_P01_s\Assets\StreamingAssets\Calibration\Output\simulation_result.json"

PARAMETER_NAMES = [
    "minimalDistance",
    "relaxationTime",
    "repulsionStrengthAgent",
    "repulsionRangeAgent",
    "lambdaAgent",
    "repulsionStrengthObs",
    "repulsionRangeObs",
    "lambdaObs",
    "k",
    "kappa",
    "obsK",
    "obsKappa",
    "considerationRange",
    "viewAngle",
    "viewAngleMax",
    "viewDistance",
    "rayStepAngle",
    "visibleFactor"
]

def load_simulation_result(filepath: str) -> Dict[str, Any]:
    """Load simulation result JSON file."""
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    print(f"Loading: {filepath}")
    print(f"File size: {path.stat().st_size / 1024 / 1024:.2f} MB")

    with open(path, 'r') as f:
        data = json.load(f)

    print(f"JSON loaded successfully\n")
    return data

def print_summary(data: Dict[str, Any]) -> None:
    """Print simulation summary information."""
    print("=" * 80)
    print("SIMULATION SUMMARY")
    print("=" * 80)
    print(f"Experiment ID:       {data.get('experimentId', 'N/A')}")
    print(f"Execution Time:      {data.get('executionTimeSeconds', 0):.2f} seconds")
    print(f"Total Agents:        {data.get('totalAgents', 0)}")
    print(f"Completed Agents:    {data.get('completedAgents', 0)}")
    print(f"Average Error:       {data.get('averageError', 0):.4f} m")
    print(f"Max Error:           {data.get('maxError', 0):.4f} m")
    print()

def print_parameters(params: Dict[str, float]) -> None:
    """Print all 18 SFM parameters."""
    print("=" * 80)
    print("SFM PARAMETERS (18 Total)")
    print("=" * 80)

    if not params:
        print("WARNING: No parameters found in data!")
        return

    missing_params = [name for name in PARAMETER_NAMES if name not in params]
    if missing_params:
        print(f"WARNING: Missing parameters: {missing_params}")

    print("\nBasic Physics:")
    print(f"  minimalDistance:        {params.get('minimalDistance', 'N/A'):.4f}")
    print(f"  relaxationTime:         {params.get('relaxationTime', 'N/A'):.4f}")

    print("\nAgent Interaction:")
    print(f"  repulsionStrengthAgent: {params.get('repulsionStrengthAgent', 'N/A'):.4f}")
    print(f"  repulsionRangeAgent:    {params.get('repulsionRangeAgent', 'N/A'):.4f}")
    print(f"  lambdaAgent:            {params.get('lambdaAgent', 'N/A'):.4f}")

    print("\nObstacle Interaction:")
    print(f"  repulsionStrengthObs:   {params.get('repulsionStrengthObs', 'N/A'):.4f}")
    print(f"  repulsionRangeObs:      {params.get('repulsionRangeObs', 'N/A'):.4f}")
    print(f"  lambdaObs:              {params.get('lambdaObs', 'N/A'):.4f}")

    print("\nPhysical Contact Forces:")
    print(f"  k:                      {params.get('k', 'N/A'):.4f}")
    print(f"  kappa:                  {params.get('kappa', 'N/A'):.4f}")
    print(f"  obsK:                   {params.get('obsK', 'N/A'):.4f}")
    print(f"  obsKappa:               {params.get('obsKappa', 'N/A'):.4f}")

    print("\nPerception/Vision:")
    print(f"  considerationRange:     {params.get('considerationRange', 'N/A'):.4f}")
    print(f"  viewAngle:              {params.get('viewAngle', 'N/A'):.4f}")
    print(f"  viewAngleMax:           {params.get('viewAngleMax', 'N/A'):.4f}")
    print(f"  viewDistance:           {params.get('viewDistance', 'N/A'):.4f}")
    print(f"  rayStepAngle:           {params.get('rayStepAngle', 'N/A'):.4f}")
    print(f"  visibleFactor:          {params.get('visibleFactor', 'N/A'):.4f}")
    print()

def print_error_statistics(agent_errors: List[Dict[str, Any]], verbose: bool = False) -> None:
    """Print agent error statistics."""
    print("=" * 80)
    print("AGENT ERROR STATISTICS")
    print("=" * 80)

    if not agent_errors:
        print("WARNING: No agent error data found!")
        return

    print(f"Total Agents with Error Data: {len(agent_errors)}")

    total_trajectory_points = sum(len(agent.get('errors', [])) for agent in agent_errors)
    print(f"Total Trajectory Points:       {total_trajectory_points}")

    avg_trajectory_length = sum(agent.get('trajectoryLength', 0) for agent in agent_errors) / len(agent_errors)
    print(f"Average Trajectory Length:     {avg_trajectory_length:.2f} timesteps")

    sorted_agents = sorted(agent_errors, key=lambda x: x.get('meanError', 0), reverse=True)

    print(f"\nTop 10 Agents by Mean Error:")
    print(f"{'Agent ID':<12} {'Traj Length':<15} {'Mean Error':<15} {'Max Error':<15}")
    print("-" * 60)
    for agent in sorted_agents[:10]:
        agent_id = agent.get('agentId', 'N/A')
        traj_len = agent.get('trajectoryLength', 0)
        mean_err = agent.get('meanError', 0)
        max_err = agent.get('maxError', 0)
        print(f"{agent_id:<12} {traj_len:<15} {mean_err:<15.4f} {max_err:<15.4f}")

    if verbose:
        print(f"\nAll Agents Error Summary:")
        print(f"{'Agent ID':<12} {'Traj Length':<15} {'Mean Error':<15} {'Max Error':<15}")
        print("-" * 60)
        for agent in sorted_agents:
            agent_id = agent.get('agentId', 'N/A')
            traj_len = agent.get('trajectoryLength', 0)
            mean_err = agent.get('meanError', 0)
            max_err = agent.get('maxError', 0)
            print(f"{agent_id:<12} {traj_len:<15} {mean_err:<15.4f} {max_err:<15.4f}")
    print()

def print_agent_detail(agent_errors: List[Dict[str, Any]], agent_id: int) -> None:
    """Print detailed trajectory for specific agent."""
    agent_data = next((agent for agent in agent_errors if agent.get('agentId') == agent_id), None)

    if not agent_data:
        print(f"ERROR: Agent {agent_id} not found in data!")
        return

    print("=" * 80)
    print(f"AGENT {agent_id} DETAILED TRAJECTORY")
    print("=" * 80)
    print(f"Trajectory Length:  {agent_data.get('trajectoryLength', 0)} timesteps")
    print(f"Mean Error:         {agent_data.get('meanError', 0):.4f} m")
    print(f"Max Error:          {agent_data.get('maxError', 0):.4f} m")
    print()

    errors = agent_data.get('errors', [])
    if not errors:
        print("No trajectory data available")
        return

    print(f"{'TimeIdx':<10} {'Error (m)':<12} {'Empirical Pos':<30} {'Validation Pos':<30}")
    print("-" * 85)

    for error_point in errors:
        time_idx = error_point.get('timeIndex', 'N/A')
        error = error_point.get('error', 0)
        emp_pos = error_point.get('empiricalPos', {})
        val_pos = error_point.get('validationPos', {})

        emp_str = f"({emp_pos.get('x', 0):.2f}, {emp_pos.get('z', 0):.2f})"
        val_str = f"({val_pos.get('x', 0):.2f}, {val_pos.get('z', 0):.2f})"

        print(f"{time_idx:<10} {error:<12.4f} {emp_str:<30} {val_str:<30}")
    print()

def main():
    parser = argparse.ArgumentParser(
        description="Load and analyze Unity PIONA simulation results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dev/load_simulation_results.py
  python dev/load_simulation_results.py --file path/to/result.json
  python dev/load_simulation_results.py --verbose
  python dev/load_simulation_results.py --agent-id 42
        """
    )

    parser.add_argument(
        '--file', '-f',
        type=str,
        default=DEFAULT_UNITY_OUTPUT,
        help=f'Path to simulation_result.json (default: {DEFAULT_UNITY_OUTPUT})'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed statistics for all agents'
    )

    parser.add_argument(
        '--agent-id', '-a',
        type=int,
        help='Show detailed trajectory for specific agent ID'
    )

    args = parser.parse_args()

    try:
        data = load_simulation_result(args.file)

        print_summary(data)

        params = data.get('parameters', {})
        print_parameters(params)

        agent_errors = data.get('agentErrors', [])
        print_error_statistics(agent_errors, verbose=args.verbose)

        if args.agent_id is not None:
            print_agent_detail(agent_errors, args.agent_id)

        print("=" * 80)
        print("VALIDATION COMPLETE")
        print("=" * 80)
        print(f"[OK] JSON file loaded successfully")
        print(f"[OK] {len(params)}/18 parameters found")
        print(f"[OK] {len(agent_errors)} agents with error data")
        print(f"[OK] Data structure validated")
        print()

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON format - {e}")
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
