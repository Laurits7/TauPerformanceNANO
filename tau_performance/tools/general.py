""" Some general tools """
import uproot
import awkward
from omegaconf import DictConfig
import numpy as np


class Histogram:
    def __init__(
            self,
            data: np.array,
            bin_edges: np.array,
            histogram_data_type: str) -> None:
        """ Initializes the histogram"""
        self.data = data
        self.histogram_data_type = histogram_data_type
        self.bin_edges = bin_edges
        self.bin_centers = self.calculate_bin_centers(bin_edges)
        self.binned_data = np.histogram(data, bins=bin_edges)[0]

    def calculate_bin_centers(self, edges: list) -> np.array:
        bin_widths = [edges[i + 1] - edges[i] for i in range(len(edges) - 1)]
        bin_centers = []
        for i in range(len(edges) - 1):
            bin_centers.append(edges[i] + (bin_widths[i] / 2))
        return np.array(bin_centers)

    def __add__(self, other):
        if (other.bin_edges).all() != (self.bin_edges).all():
            raise ArithmeticError(
                "The bins of two histograms do not match, cannot sum them.")
        return self.binned_data + other.binned_data

    def __str__(self):
        return f"{self.histogram_data_type} histogram"

    def __truediv__(self, other):
        if (other.bin_edges).all() != (self.bin_edges).all():
            raise ArithmeticError(
                "The bins of two histograms do not match, cannot divide them.")
        return self.binned_data / other.binned_data

    def __mul__(self, other):
        if (other.bin_edges).all() != (self.bin_edges).all():
            raise ArithmeticError(
                "The bins of two histograms do not match, cannot multiply them.")
        return self.binned_data * other.binned_data


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


def construct_var_names(cfg: DictConfig, obj_type: str) -> list:
    """ Constructs all variable names that are to be loaded from the input
    .root file

    Args:
        cfg : omegaconf.DictConfig
            The configuration. Branch names are inferred from that.
        obj_type : str
            Type of the main truth comparison object

    Returns:
        all_vars : list
            Variables that are to be read from the .root file
    """
    all_vars = []
    for var in cfg.allVariables.info:
        all_vars.append(var)
    for var in cfg.allVariables.tau:
        tau_var = "%s_%s" %(cfg.comparison_tau, var)
        all_vars.append(tau_var)
    for var in cfg.allVariables.GenVisTau: # need to be changed to the approptiate object
        gen_var = "%s_%s" %(cfg.genTau, var)
        all_vars.append(gen_var)
    for var in cfg.allVariables.Jet:
        jet_var = f"Jet_{var}"
        all_vars.append(jet_var)
    # if obj_type != 'genTau':
    #     for var in cfg.allVariables[obj_type]:
    #         fake_var = f"{cfg.fakes[obj_type]}_{var}"
    #         all_vars.append(fake_var)
    return all_vars
