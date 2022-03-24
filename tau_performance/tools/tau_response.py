import os
import uproot
import awkward
import numpy as np
from omegaconf import DictConfig, OmegaConf
from . import general
from .masking import Masks


class Response:
    def __init__(self, sample_name, ref_obj, cfg):
        self.sample_name = sample_name
        self.ref_obj = ref_obj
        self.cfg = cfg
        self.eff_type = "eff" if self.ref_obj == cfg.genTau else "fake"
        self._response = {}
        self.input_path = self.infer_input_path()
        self.events = general.load_events(
                self.input_path,
                cfg[f"TauID_{self.eff_type}"].data_files[self.sample_name].tree_path)
        self.numerators = Masks(self.events, "numerators", ref_obj, cfg).masks
        self.denominator = Masks(self.events, "denominators", ref_obj, cfg).masks
        self.calculate_responses()

    def infer_input_path(self):
        file_name = self.cfg[f"TauID_{self.eff_type}"].data_files[self.sample_name].path
        full_path = os.path.join(self.cfg.output_dir, file_name)
        return full_path

    def calculate_responses(self):
        ref_name = f"{self.ref_obj}_pt"
        comparison_name = f"{self.cfg.comparison_tau}_pt"
        self._response = self.calculate_response_per_var(
                                                  ref_name, comparison_name)

    def calculate_response_per_var(self, ref_name, comparison_name):
        id_response = {}
        for tau_id_key in self.numerators:
            full_id_key = f"{self.cfg.comparison_tau}_{tau_id_key}"
            wp_numerators = self.numerators[tau_id_key]
            id_response[tau_id_key] = self.calculate_wp_responses(
                                    ref_name, comparison_name, wp_numerators)
        return id_response

    def calculate_wp_responses(self, ref_name, comparison_name, wp_numerators):
        wp_responses = {}
        all_ref_entries = self.events[ref_name]
        all_comparison_entries = self.events[comparison_name]
        for wp_numerator_key in wp_numerators:
            full_mask = self.denominator & wp_numerators[wp_numerator_key]
            ref_entries = np.array(all_ref_entries[full_mask])
            comparison_entries = np.array(all_comparison_entries[full_mask])
            wp_responses[wp_numerator_key] = comparison_entries/ref_entries
        return wp_responses

    @property
    def energy_response(self):
        return self._response
