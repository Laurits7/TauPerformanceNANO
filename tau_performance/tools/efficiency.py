import os
import uproot
import awkward
import numpy as np
from omegaconf import DictConfig, OmegaConf
from tau_performance.tools import general
from tau_performance.tools.masking import Masks


class Efficiency:
    """ Class for calculating either the fake rate or efficiency given the
    correct parameters """
    def __init__(self, sample_name, comparison_tau, input_path, input_tree, ref_obj, cfg):
        self.sample_name = sample_name
        self.ref_obj = ref_obj
        self.cfg = cfg
        self.comparison_tau = comparison_tau
        self._efficiencies = {}
        self._reco_eff = {}
        self._total_effs = {}
        self.eff_type = "eff" if self.ref_obj == cfg.genTau else "fake"
        self.events = general.load_events(input_path, input_tree)
        self.numerators = Masks(self.events, "numerators", ref_obj, cfg).masks
        self.denominator = Masks(self.events, "denominators", ref_obj, cfg).masks
        self.calculate_var_efficiencies()

    def infer_input_path(self):
        file_name = self.cfg[f"TauID_{self.eff_type}"].data_files[self.sample_name].path
        full_path = os.path.join(self.cfg.output_dir, file_name)
        return full_path

    def calculate_var_efficiencies(self):
        for tau_var in self.cfg[f"TauID_{self.eff_type}"].variables.genTau:
            var_name = f"{self.ref_obj}_{tau_var.name}"
            self._efficiencies[var_name] = self.calculate_id_efficiencies(
                                                        var_name, tau_var.bins)
        for other_var in self.cfg[f"TauID_{self.eff_type}"].variables.other:
            self._efficiencies[other_var.name] = self.calculate_id_efficiencies(
                                                other_var.name, other_var.bins)
        for reco_var in self.cfg[f"TauID_{self.eff_type}"].variables.recoTau:
            var_name = f"{self.comparison_tau}_{reco_var.name}"
            self._reco_eff[var_name] = {}
            self.calculate_reco_efficiencies(var_name, reco_var.bins)

    def calculate_id_efficiencies(self, var_name, bins):
        id_eff = {}
        for tau_id_key in self.numerators:
            full_id_key = f"{self.comparison_tau}_{tau_id_key}"
            wp_numerators = self.numerators[tau_id_key]
            id_eff[tau_id_key], total_eff = self.calculate_wp_efficiencies(
                                                var_name, bins, wp_numerators)
            self._total_effs[tau_id_key] = total_eff
        return id_eff

    def calculate_wp_efficiencies(self, var_name, bins, wp_numerators):
        efficiency_histograms = {}
        total_efficiency = []
        all_entries = self.events[var_name].to_numpy()
        tau_entries = all_entries[self.denominator]
        h_gen = np.histogram(tau_entries, bins=bins)[0]
        for wp_numerator_key in wp_numerators:
            full_mask = self.denominator & wp_numerators[wp_numerator_key]
            cleaned_comparison = all_entries[full_mask]
            total_efficiency.append(len(cleaned_comparison)/len(tau_entries))
            h_cleaned = np.histogram(cleaned_comparison, bins=bins)[0]
            h_eff = h_cleaned/h_gen
            h_eff = np.nan_to_num(
                            h_eff, copy=True, nan=0.0, posinf=None, neginf=None)
            efficiency_histograms[wp_numerator_key] = (h_eff, bins)
        return efficiency_histograms, total_efficiency

    def calculate_reco_efficiencies(self, var_name, bins):
        for tau_id_key in self.numerators:
            wp_numerators = self.numerators[tau_id_key]
            efficiency_histograms = {}
            iso_key = f"{self.comparison_tau}_{tau_id_key}"
            for wp_numerator_key in wp_numerators:
                full_mask = self.denominator & wp_numerators[wp_numerator_key]
                var_entries = self.events[var_name][full_mask]
                histo_full = np.histogram(np.array(var_entries), bins=bins)
                efficiency_histograms[wp_numerator_key] = histo_full
            self._reco_eff[var_name][tau_id_key] = efficiency_histograms

    @property
    def efficiencies(self):
        return self._efficiencies

    @property
    def reco_histos(self):
        return self._reco_eff

    @property
    def total_efficiencies(self):
        return self._total_effs
