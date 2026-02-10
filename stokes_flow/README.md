# Stokes Flow - Cylinder in Cross-Flow

OpenFOAM simulations of flow around a cylinder at 11 different inlet velocities: 0.001, 0.05, 0.1, 0.5, 1, 5, 10, 50, 100, 500, and 1000 m/s.

## Running the Simulation

### Run All Cases

```bash
cd /Users/tim/Desktop/OpenFoamExamples/stokes_flow
python3 Allrun.py
```

This runs all 11 velocity cases sequentially (`velocity_1e-3` through `velocity_1e3`). The `Allrun.py` script:

- Generates and refines the mesh for each case
- Uses the converged solution from the previous case as initial conditions
- Decomposes the domain for parallel computation (8 processors)
- Runs `simpleFoam` (steady cases) or `icoFoam` (unsteady cases)
- Reconstructs the parallel solution for use in the next case

### Run Single Case

```bash
cd velocity_5e2
blockMesh
snappyHexMesh -overwrite
decomposePar -force
mpirun -np 8 icoFoam -parallel
reconstructPar -latestTime
```
