import os
import uproot
import awkward
import numpy as np
import mplhep as hep
import matplotlib.pyplot as plt
from omegaconf import DictConfig, OmegaConf


def plot_efficiencies(efficiencies, eff_type, ref_obj, cfg):
    eff_full_name = "Efficiencies" if eff_type == 'eff' else "Fake Rate"
    main_output_dir = os.path.join(cfg.output_dir, eff_full_name)
    for tau_var in cfg[f"TauID_{eff_type}"].variables.genTau:
        var_name = f"{ref_obj}_{tau_var.name}"
        var_output_dir = os.path.join(main_output_dir, var_name)
        os.makedirs(var_output_dir, exist_ok=True)
        if len(efficiencies[var_name][0].keys()) == 1:
            plot_all_id_on_one(
                                efficiencies, var_name, var_output_dir, eff_full_name,
                                tau_var.x_range, cfg, var_output_dir)
        for tau_id_key in efficiencies[var_name]:
            plot_efficiency(
                            efficiencies[var_name][tau_id_key],
                            tau_var.x_range,
                            tau_id_key,
                            var_name,
                            var_output_dir,
                            eff_full_name,
                            cfg)
    for other_var in cfg[f"TauID_{eff_type}"].variables.other:
        var_output_dir = os.path.join(main_output_dir, other_var.name)
        os.makedirs(var_output_dir, exist_ok=True)
        for tau_id_key in efficiencies[other_var.name]:
            plot_efficiency(
                            efficiencies[other_var.name][tau_id_key],
                            other_var.x_range,
                            tau_id_key,
                            other_var.name,
                            var_output_dir,
                            eff_full_name,
                            cfg)


def plot_all_id_on_one(
        efficiencies, var_name, var_output_dir, eff_type, x_range, cfg, output_dir
):
    fig, ax = plt.subplots(figsize=(12,12))
    hep.style.use(hep.style.ROOT)
    hep.cms.label(f": {var_name}", data=False)
    for tau_id_key in efficiencies[var_name]:
        efficiency_histogram = efficiencies[var_name][tau_id_key]["Default"]
        plt.plot(
            efficiency_histogram.bin_centers, efficiency_histogram.binned_data,
            label=tau_id_key, marker="v", markersize=12, lw=3)
    plt.xlabel(var_name, fontdict={'size': 20})
    plt.ylabel(eff_type, fontdict={'size': 20})
    plt.xlim(x_range)
    plt.grid()
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.9))
    output_path = os.path.join(output_dir, f"{var_name}.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close('all')


def plot_eff_reco_histos(efficiencies, eff_type, cfg):
    eff_full_name = "Efficiencies" if eff_type == 'eff' else "Fake Rate"
    main_output_dir = os.path.join(cfg.output_dir, eff_full_name)
    for reco_var in cfg[f"TauID_{eff_type}"].variables.recoTau:
        var_name = f"{cfg.comparison_tau}_{reco_var.name}"
        var_output_dir = os.path.join(main_output_dir, reco_var.name)
        os.makedirs(var_output_dir, exist_ok=True)
        for tau_id_key in efficiencies[var_name]:
            plot_reco_vars(
                            efficiencies[var_name][tau_id_key],
                            reco_var,
                            tau_id_key,
                            var_output_dir,
                            cfg)


def plot_efficiency(
        efficiency_histograms: dict,
        x_range: list,
        iso_tau_id: str,
        var_name: str,
        output_dir: str,
        eff_type: str,
        cfg: DictConfig) -> None:
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

    Returns:
        None
    """
    fig, ax = plt.subplots(figsize=(12,12))
    hep.style.use(hep.style.ROOT)
    hep.cms.label(f": {iso_tau_id}", data=False)
    for wp_key, entry in efficiency_histograms.items():
        plt.plot(
            entry.bin_centers, entry.binned_data,
            label=wp_key, marker="v", markersize=12, lw=3)
    plt.xlabel(var_name, fontdict={'size': 20})
    plt.ylabel(eff_type, fontdict={'size': 20})
    plt.xlim(x_range)
    plt.grid()
    box = ax.get_position()
    if len(efficiency_histograms.keys()) > 1:
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.9))
    output_path = os.path.join(output_dir, f"{var_name}_{iso_tau_id}.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close('all')


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
