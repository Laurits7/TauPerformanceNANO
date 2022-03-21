import os
import uproot
import awkward
import numpy as np
import mplhep as hep
import matplotlib.pyplot as plt
from omegaconf import DictConfig, OmegaConf
from . import general
from .masking import Masks


def create_efficiency_histograms(
        events: awkward.Array,
        denominator: np.array,
        numerators: dict,
        cfg: DictConfig,
        tau_var: DictConfig,
        var_type: str) -> dict:
    """ Calculates the efficiency histograms for all the WPs

    Args:
        events : awkward.Array
            Entries from the gen matched ntuple
        denominator: np.array
            The mask which events to exclude from calculations based on gen
            cuts.
        numerators: dict
            The mask which events to exclude from calculations based on reco
            per WP
        cfg: omegaconf.DictConfig
            The configuration for plotting
        tau_var: str
            The variable of the tau to be plotted
        var_type : str
            Type of the variable to be plotted

    Returns:
        efficiency_histograms : dict
            Efficiency histograms per WP
    """
    efficiency_histograms = {}
    if var_type == 'gen':
        tau_var_name = f"{cfg.genTau}_{tau_var.name}"
    else:
        tau_var_name = tau_var.name
    all_entries = events[tau_var_name].to_numpy()
    tau_entries = all_entries[denominator]
    h_gen, bins = np.histogram(tau_entries, bins=tau_var.bins)
    for wp_numerator_key in numerators:
        full_mask = denominator & numerators[wp_numerator_key]
        cleaned_comparison = all_entries[full_mask]
        h_cleaned = np.histogram(cleaned_comparison, bins=bins)[0]
        h_eff = h_cleaned/h_gen
        h_eff = np.nan_to_num(h_eff, copy=True, nan=0.0, posinf=None, neginf=None)
        efficiency_histograms[wp_numerator_key] = (h_eff, bins)
    return efficiency_histograms


def plot_efficiency_histogram(
        efficiency_histograms: dict,
        tau_var: DictConfig,
        iso_tau_id: str,
        output_dir: str,
        cfg: DictConfig,
        var_type: str) -> None:
    """ Plots the efficiencies given histograms

    Args:
        efficiency_histograms : dict
            Contains histograms under WP keys
        tau_var : DictConfig
            The variable of the tau to be plotted
        iso_tau_id : str
            Name of the tauID
        output_dir : str
            Directory where the plot will be saved
        cfg : omegaconf.DictConfig
            The configuration for plotting
        var_type : str
            Type of the variable to be plotted

    Returns:
        None
    """
    fig, ax = plt.subplots(figsize=(12,12))
    hep.style.use(hep.style.ROOT)
    hep.cms.label(f": {iso_tau_id}", data=False)
    for wp_key, entry in efficiency_histograms.items():
        bins = entry[1]
        plt.plot(
            bins[:-1]+ 0.5*(bins[1:] - bins[:-1]),
            entry[0], label=wp_key, marker="v", markersize=12, lw=3)
    if var_type == 'gen':
        prefix = f"{cfg.genTau}_"
    else:
        prefix = ''
    plt.xlabel(f"{prefix}{tau_var.name}", fontdict={'size': 20})
    plt.ylabel("Efficiency", fontdict={'size': 20})
    plt.xlim(tau_var.x_range)
    plt.grid()
    box = ax.get_position()
    if len(efficiency_histograms.keys()) > 1:
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.9))
    output_path = os.path.join(output_dir, f"{tau_var.name}_{iso_tau_id}.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close('all')



def eval_var_efficiencies(
        events: awkward.Array,
        tau_var: DictConfig,
        numerators: dict,
        denominator: list,
        cfg: DictConfig,
        var_type: str) -> None:
    """ Evaluates and plots the efficiencies for the tau_reconstruction
    given some ID cut

    Args:
        events : awkward.Array
            Entries from the gen matched ntuple
        tau_var : DictConfig
            The variable of the tau to be plotted
        cfg : omegaconf.DictConfig
            The configuration for plotting
        var_type : str
            Type of the variable to be plotted

    Returns:
        None
    """
    for tau_id_key in numerators:
        full_id_key = f"{cfg.comparison_tau}_{tau_id_key}"
        wp_numerators = numerators[tau_id_key]
        efficiency_histograms = create_efficiency_histograms(
                                            events, denominator, wp_numerators,
                                            cfg, tau_var, var_type)
        output_dir = os.path.join(cfg.output_dir, "tauID_eff", tau_var.name)
        os.makedirs(output_dir, exist_ok=True)
        plot_efficiency_histogram(
                    efficiency_histograms, tau_var, tau_id_key,
                    output_dir, cfg, var_type)


def plot_reco_vars(
        histograms: dict,
        tau_var: DictConfig,
        iso_tau_id: str,
        output_dir: str,
        cfg: DictConfig) -> None:
    """ Plots the efficiencies given histograms

    Args:
        histograms : dict
            Contains histograms under WP keys
        tau_var : DictConfig
            The variable of the tau to be plotted
        iso_tau_id : str
            Name of the tauID
        output_dir : str
            Directory where the plot will be saved
        cfg : omegaconf.DictConfig
            The configuration for plotting

    Returns:
        None
    """
    fig, ax = plt.subplots(figsize=(12,12))
    hep.style.use(hep.style.ROOT)
    hep.cms.label(f": {iso_tau_id}", data=False)
    for wp_key, entry in histograms.items():
        hep.histplot(entry, density=True, label=wp_key, histtype='step')
    plt.xlabel(tau_var.name, fontdict={'size': 20})
    plt.ylabel("", fontdict={'size': 20})
    plt.xlim(tau_var.x_range)
    plt.grid()
    box = ax.get_position()
    if len(histograms.keys()) > 1:
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.9))
    output_path = os.path.join(output_dir, f"{tau_var.name}_{iso_tau_id}.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close('all')


def reco_var_plotting(
        events: awkward.Array,
        tau_var: DictConfig,
        numerators: dict,
        denominator: np.array,
        cfg: DictConfig) -> None:
    """ Plots the RECO variables that have a matched genTau

    Args:
        events : awkward.Array
            Entries from the gen matched ntuple
        tau_var : DictConfig
            The variable of the tau to be plotted
        cfg : omegaconf.DictConfig
            The configuration for plotting

    Returns:
        None
    """
    var_full_name = f"{cfg.comparison_tau}_{tau_var.name}"
    output_dir = os.path.join(cfg.output_dir, "tauID_eff", tau_var.name)
    os.makedirs(output_dir, exist_ok=True)
    for tau_id_key in numerators:
        # full_id_key = f"{cfg.comparison_tau}_{iso_tau_id}"
        wp_numerators = numerators[tau_id_key]
        efficiency_histograms = {}
        iso_key = f"{cfg.comparison_tau}_{tau_id_key}"
        for wp_numerator_key in wp_numerators:
            full_mask = denominator & wp_numerators[wp_numerator_key]
            var_entries = events[var_full_name][full_mask]
            histo_full = np.histogram(np.array(var_entries), bins=tau_var.bins)
            efficiency_histograms[wp_numerator_key] = histo_full
        plot_reco_vars(efficiency_histograms, tau_var, tau_id_key, output_dir, cfg)


def plot_tau_id_efficiency(cfg: DictConfig) -> None:
    """ Collects all functions in order to estimate the tau id efficiency

    Args:
        cfg: omegaconf.DictConfig
            The configuration for plotting and file reading

    Returns:
        None
    """
    input_path = os.path.join(cfg.output_dir, cfg.TauID_eff.data_file.path)
    events = general.load_events(input_path, cfg.TauID_eff.data_file.tree_path)
    numerators = Masks(events, "numerators", cfg.genTau, cfg)
    denominators = Masks(events, "denominators", cfg.genTau, cfg)
    for tau_var in cfg.TauID_eff.variables.genTau:
        eval_var_efficiencies(
            events, tau_var, numerators.masks, denominators.masks, cfg, 'gen')
    for other_var in cfg.TauID_eff.variables.other:
        eval_var_efficiencies(
            events, other_var, numerators.masks, denominators.masks, cfg, 'other')
    for reco_var in cfg.TauID_eff.variables.recoTau:
        reco_var_plotting(events, reco_var, numerators.masks, denominators.masks, cfg)
