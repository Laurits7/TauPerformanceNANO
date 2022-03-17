""" Some general tools """
import uproot
import awkward
from omegaconf import DictConfig


def load_events(file_path: str, tree_name: str) -> awkward.Array:
    """ Loads all the events from a given path and a tree name

    Args:
        file_path : str
            Path to the .root file to be read
        tree_name : str
            Path in the .root file where branches of interest are located

    Returns : awkward.Array
        The events found in the inputted .root file
    """
    with uproot.open(file_path) as input_file:
        tree = input_file[tree_name]
        arrays = tree.arrays()
    return arrays


def construct_var_names(cfg: DictConfig) -> list:
    """ Constructs all variable names that are to be loaded from the input
    .root file

    Args:
        cfg: omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        all_vars : list
            Variables that are to be read from the .root file
    """
    all_vars = []
    if cfg.do_eff:
        for var in cfg.allVariables.info:
            all_vars.append(var)
        for var in cfg.allVariables.tau:
            tau_var = "%s_%s" %(cfg.comparison_tau, var)
            all_vars.append(tau_var)
        for var in cfg.allVariables.gen:
            gen_var = "%s_%s" %(cfg.variables.genTau, var)
            all_vars.append(gen_var)
    else:
        raise NotImplementedError
    return all_vars
