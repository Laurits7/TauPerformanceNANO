import os
import uproot
import awkward
import numpy as np
import mplhep as hep
import matplotlib.pyplot as plt
from omegaconf import DictConfig, OmegaConf


def plot_roc_curve(htt_total_eff, qcd_total_fakerates, cfg):
    output_dir = os.path.join(cfg.output_dir, "ROC")
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12,12))
    labels = ['Loose', 'Medium', 'Tight']
    markers = ["^", "s", "D"]
    hep.style.use(hep.style.ROOT)
    hep.cms.label(": ROC", data=False)
    for tau_id in htt_total_eff:
        if len(htt_total_eff[tau_id]) > 1:
            print(tau_id)
            fakerates = qcd_total_fakerates[tau_id]
            efficiencies = htt_total_eff[tau_id]
            line = ax.plot(fakerates, efficiencies, label=tau_id)[0]
            for i in range(len(efficiencies)):
                ax.scatter(
                            fakerates[i],
                            efficiencies[i],
                            color=line.get_color(),
                            marker=markers[i])
    plt.xlabel("Fake rate", fontdict={'size': 20})
    plt.ylabel("Efficiency", fontdict={'size': 20})
    plt.xscale('log')
    plt.grid(True, which="both")
    box = ax.get_position()
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.9))
    output_path = os.path.join(output_dir, "roc.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close('all')
