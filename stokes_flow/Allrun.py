#!/usr/bin/env python3
"""
Run a series of OpenFOAM cases with increasing inlet velocities.
Each case uses the converged solution from the previous case as initial condition.
"""

import os
import subprocess
import shutil
import re

# List of velocity cases in order
cases = [
    "velocity_1e-3",
    "velocity_5e-3",
    "velocity_1e-2",
    "velocity_5e-2",
    "velocity_1e-1",
    "velocity_5e-1",
    "velocity_1e0",
    "velocity_5e0",
    "velocity_1e1",
    "velocity_5e1",
    "velocity_1e2",
    "velocity_5e2",
    "velocity_1e3",
]


def extract_inlet_velocity(u_file_path):
    """Extract inlet velocity from 0/U file."""
    try:
        with open(u_file_path, "r") as f:
            content = f.read()

        # Find inlet block
        inlet_pattern = r"inlet\s*\{[^}]*value\s+uniform\s+\(([^)]+)\)"
        match = re.search(inlet_pattern, content, re.DOTALL)

        if match:
            return match.group(1).strip()
        else:
            print(f"Warning: Could not extract inlet velocity from {u_file_path}")
            return None
    except Exception as e:
        print(f"Error reading {u_file_path}: {e}")
        return None


def update_inlet_velocity(u_file_path, velocity_value):
    """Update inlet velocity in 0/U file."""
    try:
        with open(u_file_path, "r") as f:
            content = f.read()

        # Replace inlet boundary value
        inlet_pattern = r"(inlet\s*\{[^}]*value\s+uniform\s+)\([^)]+\)"
        new_value = f"uniform ({velocity_value})"
        new_content = re.sub(
            inlet_pattern, r"\1" + f"({velocity_value})", content, flags=re.DOTALL
        )

        with open(u_file_path, "w") as f:
            f.write(new_content)

        print(f"Updated inlet velocity to: {velocity_value}")
        return True
    except Exception as e:
        print(f"Error updating {u_file_path}: {e}")
        return False


def run_command(cmd, log_file=None):
    """Run a shell command and optionally log output."""
    try:
        if log_file:
            with open(log_file, "w") as f:
                result = subprocess.run(
                    cmd, shell=True, stdout=f, stderr=subprocess.STDOUT
                )
        else:
            result = subprocess.run(cmd, shell=True)

        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def get_latest_time(case_dir):
    """Get the latest time directory from a case."""
    try:
        result = subprocess.run(
            f"foamListTimes -case {case_dir} -latestTime",
            shell=True,
            capture_output=True,
            text=True,
        )
        latest_time = result.stdout.strip()
        if latest_time and latest_time != "0":
            return latest_time
    except Exception as e:
        print(f"Error getting latest time: {e}")

    return None


def main():
    """Main run function."""
    base_dir = os.getcwd()
    prev_case = None

    for case in cases:
        print("")
        print("=" * 50)
        print(f"Running case: {case}")
        print("=" * 50)

        case_dir = os.path.join(base_dir, case)

        if not os.path.isdir(case_dir):
            print(f"Error: Case directory {case_dir} not found")
            continue

        os.chdir(case_dir)

        # Generate background mesh
        print("Running blockMesh...")
        if not run_command("blockMesh", "log.blockMesh"):
            print("blockMesh failed!")

        # Refine mesh around cylinder
        print("Running snappyHexMesh...")
        if not run_command("snappyHexMesh -overwrite", "log.snappyHexMesh"):
            print("snappyHexMesh failed!")

        # Save original 0 directory if not already saved
        orig_dir = os.path.join(case_dir, "0.orig")
        if not os.path.isdir(orig_dir):
            shutil.copytree("0", orig_dir)
            print("Saved original initial conditions to 0.orig/")

        # Use previous solution as initial condition
        if prev_case is not None:
            print(f"Copying solution from {prev_case} as initial condition...")

            prev_case_dir = os.path.join(base_dir, prev_case)
            latest_time = get_latest_time(prev_case_dir)

            if latest_time and latest_time != "0":
                # Extract target velocity from original 0/U
                orig_u_file = os.path.join(orig_dir, "U")
                target_vel = extract_inlet_velocity(orig_u_file)

                if target_vel:
                    # Copy converged solution fields
                    prev_u_file = os.path.join(prev_case_dir, latest_time, "U")
                    prev_p_file = os.path.join(prev_case_dir, latest_time, "p")

                    if os.path.isfile(prev_u_file) and os.path.isfile(prev_p_file):
                        shutil.copy(prev_u_file, "0/U")
                        shutil.copy(prev_p_file, "0/p")

                        # Update inlet velocity
                        if update_inlet_velocity("0/U", target_vel):
                            print(
                                f"Initialized from time {latest_time} of {prev_case} with inlet velocity: {target_vel}"
                            )
                    else:
                        print(
                            f"Warning: Could not find solution files in {prev_case_dir}/{latest_time}"
                        )
                else:
                    print("Warning: Could not extract target velocity")
            else:
                print(f"Warning: No valid time found in {prev_case}")

        # Decompose for parallel run
        print("Running decomposePar...")
        if not run_command("decomposePar -force", "log.decomposePar"):
            print("decomposePar failed!")

        # Run solver in parallel
        if case == "velocity_5e2" or case == "velocity_1e3":
            print("Running icoFoam in parallel with 8 processors...")
            if not run_command("mpirun -np 8 icoFoam -parallel", "log.icoFoam"):
                print("simpleFoam failed!")
        else:
            print("Running simpleFoam in parallel with 8 processors...")
            if not run_command("mpirun -np 8 simpleFoam -parallel", "log.simpleFoam"):
                print("simpleFoam failed!")

        # Reconstruct the parallel solution for next case
        print("Reconstructing solution...")
        if not run_command("reconstructPar -latestTime", "log.reconstructPar"):
            print("reconstructPar failed!")

        print(f"Case {case} completed!")

        prev_case = case
        os.chdir(base_dir)

    print("")
    print("=" * 50)
    print("All cases completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
