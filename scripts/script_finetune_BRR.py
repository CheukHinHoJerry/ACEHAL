from sklearn.linear_model import BayesianRidge
# from ase.calculators.castep import Castep
from ase.io import read

from julia.api import Julia
jl = Julia(compiled_modules=False)
from julia import Pkg
Pkg.activate("/zfs/users/jerryho528/jerryho528/julia_ws/LocalForceUQ/Project.toml")
from ACEHAL.HAL import HAL

from mace.calculators import mace_mp
from mace.calculators import MACECalculator
from ase import build

import os

ft_path = "/zfs/users/jerryho528/jerryho528/julia_ws/LocalForceUQ/cp_al/LiCl-ft_run-3.model"

### read inital database 
fit_configs = read("/zfs/users/jerryho528/jerryho528/julia_ws/LocalForceUQ/data/LiCl/LiCl_train82.xyz", ":")
fit_configs = fit_configs[0:-1:8]
test_configs = read("/zfs/users/jerryho528/jerryho528/julia_ws/LocalForceUQ/data/LiCl/test.xyz", ":")
res_path = "/zfs/users/jerryho528/jerryho528/julia_ws/LocalForceUQ/cp_al/ACEHAL/result/testHAL29June0100_900K_pure/"

if not os.path.exists(res_path):
    os.makedirs(res_path)
    print(f"Directory created at {res_path}.")
else:
    print(f"Directory {res_path} already exists, overwriting")


## keys of the DFT labels in the initial database, to be used in HAL configs too, Fmax excludes large forces from fitting
data_keys = { "E" : "energy", "F" : "forces", "V" : "virial", "Fmax" : 15.0 }

## set up (CASTEP) DFT calculator
model_ft = MACECalculator(model_paths=ft_path, device="cpu", compute_stress = True)
calculator = model_ft

## set isolated atom energies or E0s (possible to use numbers from CASTEP pseudopotential file)
E0s = { "Li" : -0.06062883, "Cl" : -0.07200602000000002 }

## weights, the denominators may be interpreted as GAP sigmas
weights = { "E": 30.0, "F": 10.0, "V": 1.0}

## sklearn BRR solver
solver = BayesianRidge(fit_intercept=True, compute_score=True)

## cor_order, r_cut fixed, whereas maxdeg is optimised
fixed_basis_info = {"elements": list(E0s.keys()), "cor_order" : 3, "r_cut" : 6.7,  "smoothness_prior" : ("gaussian", 0.354), "pure" : True}
optimize_params = {"maxdeg": ("int", (12, 12, 12))}

HAL(fit_configs, # initial fitting database
    fit_configs, # initial starting datbase for HAL (often equal to initial fitting datbase)
    None, # use ACE1x defaults (advised)
    solver, # sklearns solver to be used for fitting 
    fit_kwargs={"E0s": E0s, "data_keys": data_keys, "weights": weights}, # fitting arguments
    n_iters=100, # max HAL iterations 
    traj_len=2000, # max steps during HAL iteration until config is evaluated using QM/DFT
    # == to be modified for cp
    tol=0.3, # relative uncertainty tolerance [0.2-0.4]
    tol_eps=0.2,  # regularising fraction of uncertainty [0.1-0.2]
    # ==
    tau_rel=0.2, # biasing strength [0.1-0.3], e.g. biasing strength relative to regular MD forces
    ref_calc=calculator, # reference QM/DFT calculator
    dt_fs=1.0, # timestep (in fs)
    T_K=900,  # temperature (in K)
    T_timescale_fs=100, # Langevin thermostat length scale (in fs)
    P_GPa=1.0, # Pressure (in GPa)
    swap_step_interval=0, # atom swap MC step interval 
    cell_step_interval=0, # cell shape MC step interval
    basis_optim_kwargs={"n_trials": 2, # max number of basis optimisation iterations
                        "timeout" : 10000, # timeout for a basis optimisation iteration
                        "max_basis_len": 10000, # max basis size 
                        "fixed_basis_info": fixed_basis_info, # fixed basis information (see above)
                        "optimize_params": optimize_params}, # optimisable parameter (see above)
    basis_optim_interval=1, # interval of basis optimisation  
    file_root=res_path, # file root for names
    test_fraction=0.0, # fraction of config sampled for test database
    traj_interval=10,
    test_configs = test_configs) # interval of saving snapshots of trajectory
