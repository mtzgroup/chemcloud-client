# Keywords

## terachem_pbs

- `molden`: Optional, True/False
    - If set to `True` and `imd_orbital_type` set to `whole_c` the `AtomicResult.extras['molden']` field will contain a string of the molden file.
- `imd_orbital_type`: Optional, One of: ["no_orbital", "alpha_orbital", "beta_orbital", "alpha_density", "beta_density", "whole_c"], Default: "no_orbital".
