import json
import argparse
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import uuid

DEFAULT_UNITY_INPUT = r"D:\UnityProjects\META_VERYOLD_P01_s\Assets\StreamingAssets\Calibration\Input"

PARAMETER_BOUNDS = {
    "minimalDistance": (0.15, 0.35),
    "relaxationTime": (0.3, 0.8),
    "repulsionStrengthAgent": (0.8, 1.8),
    "repulsionRangeAgent": (3.0, 7.0),
    "lambdaAgent": (0.2, 0.5),
    "repulsionStrengthObs": (0.6, 1.5),
    "repulsionRangeObs": (3.0, 7.0),
    "lambdaObs": (0.2, 0.5),
    "k": (5.0, 12.0),
    "kappa": (3.0, 7.0),
    "obsK": (2.0, 4.5),
    "obsKappa": (0.0, 2.0),
    "considerationRange": (2.0, 4.0),
    "viewAngle": (120.0, 180.0),
    "viewAngleMax": (200.0, 270.0),
    "viewDistance": (3.0, 10.0),
    "rayStepAngle": (15.0, 45.0),
    "visibleFactor": (0.5, 0.9)
}

PARAMETER_NAMES = list(PARAMETER_BOUNDS.keys())

def generate_experiment_id(prefix: str = "exp") -> str:
    """
    Generate unique experiment ID.

    Format: <prefix>_<timestamp>_<short_uuid>
    Example: exp_20250115_143022_a3f7

    Args:
        prefix: Prefix string (default: "exp")

    Returns:
        Unique experiment ID string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{short_uuid}"

def validate_parameters(params: Dict[str, float], strict: bool = True) -> tuple[bool, list[str]]:
    """
    Validate parameters against bounds.

    Args:
        params: Parameter dictionary
        strict: If True, fail on out-of-bounds; if False, only warn

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    # Check all 18 parameters exist
    missing = [name for name in PARAMETER_NAMES if name not in params]
    if missing:
        errors.append(f"Missing parameters: {missing}")

    # Check bounds
    for name, value in params.items():
        if name not in PARAMETER_BOUNDS:
            errors.append(f"Unknown parameter: {name}")
            continue

        min_val, max_val = PARAMETER_BOUNDS[name]
        if value < min_val or value > max_val:
            msg = f"{name} = {value:.4f} out of bounds [{min_val}, {max_val}]"
            if strict:
                errors.append(msg)
            else:
                print(f"WARNING: {msg}")

    is_valid = len(errors) == 0
    return is_valid, errors

def clamp_parameters(params: Dict[str, float]) -> Dict[str, float]:
    """
    Clamp parameters to valid bounds.

    Args:
        params: Parameter dictionary

    Returns:
        Clamped parameter dictionary
    """
    clamped = {}

    for name in PARAMETER_NAMES:
        if name not in params:
            continue

        value = params[name]
        min_val, max_val = PARAMETER_BOUNDS[name]
        clamped[name] = max(min_val, min(max_val, value))

        if clamped[name] != value:
            print(f"Clamped {name}: {value:.4f} -> {clamped[name]:.4f}")

    return clamped

def export_to_unity_json(
    params: Dict[str, float],
    output_path: str,
    experiment_id: str = None,
    clamp: bool = True,
    validate: bool = True
) -> str:
    """
    Export parameters to Unity JSON format.

    Args:
        params: Parameter dictionary (18 SFM parameters)
        output_path: Output file path
        experiment_id: Optional experiment ID (auto-generated if None)
        clamp: Clamp out-of-bounds values
        validate: Validate parameters before export

    Returns:
        Generated experiment ID
    """
    # Generate experiment ID if not provided
    if experiment_id is None:
        experiment_id = generate_experiment_id()

    # Clamp parameters if requested
    if clamp:
        params = clamp_parameters(params)

    # Validate parameters
    if validate:
        is_valid, errors = validate_parameters(params, strict=not clamp)
        if not is_valid:
            raise ValueError(f"Parameter validation failed:\n" + "\n".join(errors))

    # Create Unity JSON structure
    unity_json = {
        "experimentId": experiment_id,
        "timestamp": datetime.now().isoformat(),
        **params
    }

    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write JSON file
    with open(output_path, 'w') as f:
        json.dump(unity_json, f, indent=2)

    return experiment_id

def load_parameters_from_json(filepath: str) -> Dict[str, float]:
    """
    Load parameters from JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Parameter dictionary
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(path, 'r') as f:
        data = json.load(f)

    # Extract only parameter fields (ignore experimentId, timestamp, etc.)
    params = {name: data[name] for name in PARAMETER_NAMES if name in data}

    return params

def print_parameters(params: Dict[str, float]):
    """Print parameters in readable format."""
    print("=" * 80)
    print("PARAMETERS TO EXPORT")
    print("=" * 80)

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

def main():
    parser = argparse.ArgumentParser(
        description="Export Python parameters to Unity JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dev/export_to_unity.py --input params.json --output exp_001.json
  python dev/export_to_unity.py --input params.json --auto-id
  python dev/export_to_unity.py --input params.json --experiment-id baseline
  python dev/export_to_unity.py --input params.json --no-clamp --no-validate
        """
    )

    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Input parameter JSON file'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output Unity JSON file path (default: auto-generated)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default=DEFAULT_UNITY_INPUT,
        help=f'Output directory (default: {DEFAULT_UNITY_INPUT})'
    )

    parser.add_argument(
        '--experiment-id',
        type=str,
        help='Experiment ID (default: auto-generated)'
    )

    parser.add_argument(
        '--auto-id',
        action='store_true',
        help='Auto-generate experiment ID and filename'
    )

    parser.add_argument(
        '--no-clamp',
        action='store_true',
        help='Disable automatic parameter clamping'
    )

    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Disable parameter validation'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed parameter values'
    )

    args = parser.parse_args()

    try:
        # Load input parameters
        print(f"Loading parameters from: {args.input}")
        params = load_parameters_from_json(args.input)
        print(f"Loaded {len(params)} parameters")

        if args.verbose:
            print_parameters(params)

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            # Auto-generate filename
            exp_id = args.experiment_id if args.experiment_id else generate_experiment_id()
            filename = f"{exp_id}_parameters.json"
            output_path = Path(args.output_dir) / filename

        # Export to Unity JSON
        experiment_id = export_to_unity_json(
            params=params,
            output_path=output_path,
            experiment_id=args.experiment_id,
            clamp=not args.no_clamp,
            validate=not args.no_validate
        )

        print("=" * 80)
        print("EXPORT SUCCESSFUL")
        print("=" * 80)
        print(f"Experiment ID:  {experiment_id}")
        print(f"Output file:    {output_path}")
        print(f"File size:      {Path(output_path).stat().st_size} bytes")
        print()
        print("Next steps:")
        print("1. Run Unity simulation with this parameter file")
        print("2. Wait for simulation_result.json to be generated")
        print("3. Evaluate objective: python dev/evaluate_objective.py")
        print()

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    except ValueError as e:
        print(f"ERROR: {e}")
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
