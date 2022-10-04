import os
import uproot
import awkward
import numpy as np
from omegaconf import DictConfig, OmegaConf
import mplhep as hep
import matplotlib.pyplot as plt


def plot_all_responses(energy_responses, ref_obj, sample_name, cfg):
    main_output_dir = os.path.join(cfg.output_dir, 'energy_response')
    os.makedirs(main_output_dir, exist_ok=True)
    for tau_id_key in energy_responses:
        id_responses = energy_responses[tau_id_key]
        plot_response_per_id(id_responses, tau_id_key, sample_name, main_output_dir, ref_obj)


def plot_response_per_id(id_responses, tau_id_key, sample_name, output_dir, ref_obj):
    fig, ax = plt.subplots(figsize=(12,12))
    hep.style.use(hep.style.ROOT)
    hep.cms.label(f": {tau_id_key}", data=False)
    for wp_key in id_responses:
        n_bins = int(np.sqrt(len(id_responses[wp_key])))
        histogram = np.histogram(id_responses[wp_key], bins=n_bins)
        hep.histplot(
                        histogram, density=True,
                        label=wp_key, histtype='step')
    plt.xlabel(r"$\frac{p_{t}^{Rec}}{p_{t}^{Gen}}$")
    plt.grid()
    ax.text(0.05, 0.95, sample_name, transform=ax.transAxes, fontsize=20,
        verticalalignment='top')
    if len(id_responses) > 1:
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.9))
    output_path = os.path.join(output_dir, f'{ref_obj}_{tau_id_key}.png')
    plt.savefig(output_path, bbox_inches='tight')
    plt.close('all')
