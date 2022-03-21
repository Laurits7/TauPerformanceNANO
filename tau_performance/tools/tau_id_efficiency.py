import os
import uproot
import awkward
import numpy as np
import mplhep as hep
import matplotlib.pyplot as plt
from omegaconf import DictConfig, OmegaConf
from . import general


def create_denominator(events: awkward.Array, cfg: DictConfig) -> np.array:
    """ Creates mask of which events to include for the tau ID efficiency
    calculation

    Args:
        events : awkward.Array
            Entries from the gen matched ntuple
        cfg: omegaconf.DictConfig
            The configuration for plotting

    Returns:
        mask: np.array
            The mask which events to exclude from calculations
    """
    if cfg.TauID_eff.denominators == "":
        mask = np.array([True] * len(events))
    else:
        raise NotImplementedError(
            "Currently only mask to include all gen is implemented")
    return mask


def create_numerators(
        id_key: str,
        events: awkward.Array,
        tau_id_type: str,
        cfg: DictConfig) -> dict:
    """ Creates mask of which events to include for the tau ID efficiency
    calculation

    Args:
        id_key : str
            The branch key on which the cuts will be applied
        events : awkward.Array
            Entries from the gen matched ntuple
        tau_id_type : str
            Either DecayMode tauID or isolation [dm, iso]
        cfg: omegaconf.DictConfig
            The configuration for plotting

    Returns:
        mask: dict
            Contains the mask for each of the WPs
    """
    pt_key = f"{cfg.comparison_tau}_pt"
    eta_key = f"{cfg.comparison_tau}_eta"
    pt_mask = events[pt_key].to_numpy() > cfg.TauID_eff.numerators.tau.pt
    eta_mask = np.abs(events[eta_key].to_numpy()) < cfg.TauID_eff.numerators.tau.eta
    base_mask = pt_mask & eta_mask
    if tau_id_type == 'iso':
        mask = {
            "Loose": (events[id_key] >= cfg.TauID_eff.tau_ids.iso.WPs.Loose) & base_mask,
            "Medium": (events[id_key] >= cfg.TauID_eff.tau_ids.iso.WPs.Medium) & base_mask,
            "Tight": (events[id_key] >= cfg.TauID_eff.tau_ids.iso.WPs.Tight) & base_mask
        }
    elif tau_id_type == 'dm':
        mask = {
            "DM": (events[id_key] == 1) & base_mask
            # "Medium": (events[id_key] >= cfg.TauID_eff.tau_ids.dm.WPs.Medium) & base_mask,
            # "Tight": (events[id_key] >= cfg.TauID_eff.tau_ids.dm.WPs.Tight) & base_mask
        }
    else:
        raise NotImplementedError(f"TauID '{tau_id_type}' is not implemented")
    return mask


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
    elif var_type == 'reco':
        tau_var_name = f"{cfg.comparison_tau}_{tau_var.name}"
    else:
        tau_var_name = tau_var.name
    all_entries = events[tau_var_name].to_numpy()
    tau_entries = all_entries[denominator]
    h_gen, bins = np.histogram(tau_entries, bins=tau_var.bins)
    for wp_numerator_key in numerators.keys():
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
    elif var_type == 'reco':
        prefix = f"{cfg.comparison_tau}_"
    else:
        prefix = ''
    plt.xlabel(f"{prefix}{tau_var.name}", fontdict={'size': 20})
    plt.ylabel("Efficiency", fontdict={'size': 20})
    plt.xlim(tau_var.x_range)
    plt.grid()
    box = ax.get_position()
    if not "DM" in list(efficiency_histograms.keys()):
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.9))
    output_path = os.path.join(output_dir, f"{tau_var.name}_{iso_tau_id}.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close('all')


def plot_var_efficiencies(
        events: awkward.Array,
        denominator: np.array,
        numerators: dict,
        tau_var: DictConfig,
        var_type: str,
        cfg: DictConfig,
        tau_id: str) -> None:
    """ Plots the efficiencies for the tau_reconstruction given some ID cut

    Args:
        events : awkward.Array
            Entries from the gen matched ntuple
        denominator: np.array
            Mask to choose the events.
        numerators : dict
            Masks to choose the events for all the WPs
        tau_var : DictConfig
            The variable of the tau to be plotted
        var_type : str
            Type of the variable to be plotted
        cfg : omegaconf.DictConfig
            The configuration for plotting
        tau_id : str
            Tau ID name

    Returns:
        None
    """
    efficiency_histograms = create_efficiency_histograms(
                                        events, denominator, numerators,
                                        cfg, tau_var, var_type)
    output_dir = os.path.join(cfg.output_dir, "tauID_eff", tau_var.name)
    os.makedirs(output_dir, exist_ok=True)
    plot_efficiency_histogram(
                efficiency_histograms, tau_var, tau_id,
                output_dir, cfg, var_type)


def eval_var_efficiencies(
        events: awkward.Array,
        tau_var: DictConfig,
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
    denominator = create_denominator(events, cfg)
    for iso_tau_id in cfg.TauID_eff.tau_ids.iso.ids:
        iso_key = f"{cfg.comparison_tau}_{iso_tau_id}"
        numerators = create_numerators(iso_key, events, "iso", cfg)
        plot_var_efficiencies(
                                events, denominator, numerators,
                                tau_var, var_type, cfg, iso_tau_id)
    for dm_tau_id in cfg.TauID_eff.tau_ids.dm:
        dm_tau_key = f"{cfg.comparison_tau}_{dm_tau_id}"
        numerators = create_numerators(dm_tau_key, events, "dm", cfg)
        plot_var_efficiencies(
                                events, denominator, numerators,
                                tau_var, var_type, cfg, dm_tau_id)


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
    for tau_var in cfg.TauID_eff.variables.genTau:
        eval_var_efficiencies(events, tau_var, cfg, 'gen')
    for reco_var in cfg.TauID_eff.variables.recoTau:
        eval_var_efficiencies(events, reco_var, cfg, 'reco')
    for other_var in cfg.TauID_eff.variables.other:
        eval_var_efficiencies(events, other_var, cfg, 'other')
