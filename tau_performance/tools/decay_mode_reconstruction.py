import os
import uproot
import awkward
import numpy as np
import mplhep as hep
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from omegaconf import  OmegaConf, DictConfig
from . import general


def extract_dm_info(conf_entry):
    """ Extracts the plot labels and other status index for different decay
    modes

    Args:
        conf_entry : omegaconf.DictConfig

    Returns:
        keys : list(str)
            Plain text name for the decay mode
        values : list(str)
            Decay mode written in LaTeX format
    """
    dict_format = OmegaConf.to_object(conf_entry)
    keys = [key for key in dict_format.keys()]
    values = [value['latex'] for value in dict_format.values()]
    return keys, values


def plot_confusion_matrix(histogram: np.ndarray, cfg: DictConfig) -> None:
    """ The confusion matrix is normalized per GEN decay mode

    Args:
        histogram : np.ndarray
            Gen & RECO tau decaymode confusion matrix
        cfg: omegaconf.DictConfig
            The configuration for plotting

    Returns:
        None
    """
    fig, ax = plt.subplots(figsize=(12,12))
    ax.set_aspect('equal', adjustable='box')
    hep.style.use(hep.style.ROOT)
    hep.cms.label(": %s" %cfg.comparison_tau, data=False)
    cats = cfg.TauDM_reco.dm_categories
    xbins, ybins = np.arange(len(cats) + 1), np.arange(len(cats) + 1)
    names, labels = extract_dm_info(cats)
    labels = [f"${label}$" for label in labels]
    tick_values = np.arange(len(labels)) + 0.5
    hep.hist2dplot(histogram, xbins, ybins, cmap="gray", cbar=True)
    plt.xticks(tick_values, labels, fontsize=14, rotation=0)
    plt.yticks(tick_values + 0.2, labels, fontsize=14, rotation=90)
    plt.ylabel("RECO decay mode", fontdict={'size': 14})
    plt.xlabel("GEN decay mode", fontdict={'size': 14})
    ax.tick_params(axis=u'both', which=u'both',length=0)
    for i in range(len(ybins) - 1):
        for j in range(len(xbins) - 1):
            bin_value = histogram.T[i, j]
            ax.text(xbins[j]+0.5, ybins[i]+0.5, f"{bin_value:.2f}",
                    color="r", ha="center", va="center", fontweight="bold")
    os.makedirs(cfg.output_dir, exist_ok=True)
    output_path = os.path.join(cfg.output_dir, "TauDM_reco.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close('all')


def extract_matched_tau_decay_modes(
        events: awkward.Array,
        cfg: DictConfig) -> tuple[list, list]:
    """ Extracts the decay modes of taus that were matched to gen

    Args:
        events : awkward.Array
            Entries from the gen matched ntuple
        cfg: omegaconf.DictConfig
            The configuration for plotting

    Returns:
        truth_dms : list
            The decay modes of the genTau
        comparison_dms : list
            The decay modes of the comparison tau
    """
    comparison_tau_dms = events[f"{cfg.comparison_tau}_decayMode"].to_numpy()
    truth_tau_dms = events[f"{cfg.variables.genTau}_status"].to_numpy()
    interest_mask = comparison_tau_dms != -999
    truth_dms = list(truth_tau_dms[interest_mask])
    comparison_dms = list(comparison_tau_dms[interest_mask])
    return truth_dms, comparison_dms


def decay_mode_reconstruction(cfg: DictConfig) -> None:
    """ Collects all functions in order to estimate the tau decay mode
    reconstruction

    Args:
        cfg: omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        None
    """
    print("Started loading file")
    input_path = os.path.join(cfg.output_dir, cfg.TauID_eff.data_file.path)
    events = general.load_events(
        input_path, cfg.TauID_eff.data_file.tree_path)
    print("Finished loading file")
    truth_dms, comparison_dms = extract_matched_tau_decay_modes(events, cfg)
    conf_matrix = confusion_matrix(
                                  truth_dms, comparison_dms,
                                  labels=[0,1,2,10,11,15],
                                  normalize='true')
    plot_confusion_matrix(conf_matrix, cfg)
