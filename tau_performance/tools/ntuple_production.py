import os
import uproot
import awkward
from omegaconf import DictConfig
from collections import defaultdict
from . import particle_matching as pm
from . import general


def pick_suitable_gen_taus(event: awkward.Array, cfg: DictConfig) -> list:
    """ Picks only those genTaus that pass the quality cuts

    Args:
        events: awkward.Array
            Event with all the branches
        cfg : omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        good_gen_taus : list
            List of gen taus that pass the quality cuts
    """
    good_gen_taus = []
    for tau_idx in range(event[f"n{cfg.variables.genTau}"]):
        if event[f"{cfg.variables.genTau}_pt"][tau_idx] < cfg.quality_cuts.genTau.pt:
            continue
        if abs(event[f"{cfg.variables.genTau}_eta"][tau_idx]) > cfg.quality_cuts.genTau.eta:
            continue
        good_gen_taus.append(tau_idx)
    return good_gen_taus


def fill_eff_ntuple(events: awkward.Array, cfg: DictConfig) -> None:
    """ Fills the tauID efficiency root file with the matched taus and
    gen taus so they are same length. If no tau is matched to genTau a value
    of -999 is assigned.

    Args:
        events : awkward.Array
            All events with all the variables from the input ntuple
        cfg : omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        None
    """
    output_path = os.path.join(cfg.output_dir, cfg.TauID_eff.data_file.path)
    eff_ntuple_file = uproot.recreate(output_path)
    all_vars = general.construct_var_names(cfg)
    fill_entries = []
    for event in events:
        good_gen_taus = pick_suitable_gen_taus(event, cfg)
        matched_gen_taus = pm.match_taus_to_refs(good_gen_taus, event, cfg)
        for gen_tau_idx in good_gen_taus:
            fill_entry = {var: -999 for var in all_vars}
            for info_branch in cfg.allVariables.info:
                fill_entry[info_branch] = event[info_branch]
            for gen_var in cfg.allVariables.gen:
                gen_key = f"{cfg.variables.genTau}_{gen_var}"
                fill_entry[gen_key] = event[gen_key][gen_tau_idx]
            if gen_tau_idx in matched_gen_taus:
                matched_tau_idx = matched_gen_taus[gen_tau_idx]
                for tau_var in cfg.allVariables.tau:
                    tau_key = f"{cfg.comparison_tau}_{tau_var}"
                    fill_entry[tau_key] = event[tau_key][matched_tau_idx]
            fill_entries.append(fill_entry)
    res = {key: [] for key in all_vars}
    {res[key].append(sub[key]) for sub in fill_entries for key in sub}
    eff_ntuple_file[cfg.TauID_eff.data_file.tree_path] = res
    return None
