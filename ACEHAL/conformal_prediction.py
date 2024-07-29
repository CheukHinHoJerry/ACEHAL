from julia.api import Julia
jl = Julia(compiled_modules=False)
from julia import Main

"""
setting up a dictionary of quantile by class
perform conformal prediction calibration in julia
can this just become reading txt from saved data and then 
run a simple .jl script to setup everything we want?

1. A UMAP_ for classification
2. a quantile dictionary by class
"""
def do_calibration(cali_ats_path, alpha = 0.25, 
                   epsilon_sigma = 0.05, epsilon_F = 0.5,
                   smoothness_prior = ("guassian", 0.354)
                   ):

    # define some hyper parameters that are usually fixed

    # reading atoms

    # define UMAP we should keep this fixed later on
    
    # get descirptors with prior scaling 

    # train and apply UMAP, kmeans clustering

    # get locF_infos

    # get_si_by_class

    # calculate quantile_by_class
    
    return


def get_cp_uncertainty(ats):
    # compute the descriptor with gamma scaling

    # simply call predict_local_class_from_transformed_desp

    # compute F, Fis, and unwrap Fis by site

    # compuate tildeF by site
    return # a list of uncertainty of size length(ats)

