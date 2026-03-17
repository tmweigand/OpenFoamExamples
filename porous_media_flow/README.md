# Porous media workflow (parallel)

1. Generate circles and update `snappyHexMeshDict`
2. Create base mesh:
   - `blockMesh`
3. First decomposition (for parallel snappy):
   - `decomposePar -force`
4. Run snappy in parallel:
   - `mpirun -np 8 snappyHexMesh -parallel -overwrite`
5. Rebuild decomposition from the snapped mesh:
   - `reconstructParMesh -constant`
   - `rm -rf processor*`
   - `decomposePar -force`
6. Run solver:
   - `mpirun -np 8 simpleFoam -parallel`

## Why re-decompose?
`decomposePar` done before snappy does not yet see cylinder patches. Re-decomposing after snappy ensures correct boundary conditions in `processor*/0`.
