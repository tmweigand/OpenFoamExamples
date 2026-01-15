# Parallel Plates OpenFOAM Simulation

This case simulates 2D laminar flow between parallel plates using OpenFOAM.

## Running the Simulation

### Serial Execution

1. Generate the mesh:

```bash
cd paralllel_plates
blockMesh
```

2. Run the solver:

```bash
icoFoam
```

3. Post-process results:

```bash
paraFoam
```

or create a .foam file and open in Paraview.

### Parallel Execution (8 processors)

1. Generate the mesh:

```bash
cd paralllel_plates
blockMesh
```

2. Decompose the domain:

```bash
decomposePar
```

3. Run the solver in parallel:

```bash
mpirun -np 8 icoFoam -parallel
```

4. Reconstruct the results:

```bash
reconstructPar
```

5. Post-process results:

```bash
paraFoam
```

or create a .foam file and open in Paraview.

## Post-Processing and Analysis

The simulation includes function objects that samples velocity and pressure along the channel height at the outlet and calculates the average pressure at the inlet and the outlet.

## Files Structure

```
paralllel_plates/
├── 0/               # Initial and boundary conditions
│   ├── U            # Velocity field
│   └── p            # Pressure field
├── constant/                # Physical properties and mesh
│   ├── transportProperties  # Physical parameters
│   └── turbulenceProperties # Turbulent closure approximation
├── system/              # Solution control
│   ├── blockMeshDict    # Domain information
│   ├── controlDict      # Includes outlet sampling function
│   ├── decomposeParDict # Parallel decomposition information
│   ├── fvSchemes        # Discretization information
│   └── fvSolution       # Solver Information
└── postProcessing/         # Generated during simulation
    └── outletLine/         # Velocity and pressure samples at outlet
    └── inletPressureAvg/   # Average pressure at the inlet
    └── outletPressureAvg/  # Average pressure at the outlet
```
