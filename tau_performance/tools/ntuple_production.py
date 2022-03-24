import os
import uproot
import awkward
from omegaconf import DictConfig
from collections import defaultdict
from . import particle_matching as pm
from . import general


def check_fake_suitability(
        event: awkward.Array,
        ref_obj: str,
        ref_idx: int,
        ref_type: str,
        cfg: DictConfig) -> list:
    """ Picks only those fake objects that pass the quality cuts

    Args:
        events: awkward.Array
            Event with all the branches
        ref_obj : str
            The object comparison tau to match to.
        ref_idx : int
            The index of reference object
        ref_type : str
            Type of the reference object
        cfg : omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        suitable : bool
            Whether or not the fake reference object satisfies the criteria
    """
    suitable = True
    if ref_type == 'genElectron' or ref_type == 'genMuon':
        ref_pdgid = event[f"{cfg.fakes[ref_type]}_pdgId"][ref_idx]
        if abs(ref_pdgid) != 11 and ref_type == 'genElectron':
            suitable = False
        elif abs(ref_pdgid) != 13 and ref_type == 'genMuon':
            suitable = False
        if not ((ev.GenPart_statusFlags[ijet] >> 0 & 1) or
                (
                    (ev.GenPart_status[ijet] == 1) and
                    (ev.GenPart_statusFlags[ijet] >> 5 & 1)
                )):
            suitable = False
    else:
        for gen_part_idx in range(event['nGenPart']):
            if abs(event['GenPart_pdgId'][gen_part_idx]) not in [11, 13, 15]:
                continue
            if abs(event['GenPart_pt'][gen_part_idx]) < 15:
                continue
            if event['GenPart_status'][gen_part_idx] != 1:
                continue
            select_lep = ( (abs(event['GenPart_pdgId'][gen_part_idx]) in [11, 13]) and
                          ( event['GenPart_statusFlags'][gen_part_idx] >> 0 & 1 ))
            select_tau = ( (abs(event['GenPart_pdgId'][gen_part_idx]) == 15) and
                           (event['GenPart_statusFlags'][gen_part_idx] >> 1 & 1) and
                          ( event['GenPart_statusFlags'][gen_part_idx] >> 0 & 1 ))
            if not (select_lep or select_tau):
                continue
            dR = pm.deltaR(
                            event['GenPart_eta'][gen_part_idx],
                            event['GenPart_phi'][gen_part_idx],
                            event['GenJet_eta'][ref_idx],
                            event['GenJet_phi'][ref_idx])
            if dR < 0.3:
                suitable = False
                break
    return suitable


def pick_suitable_ref_objects(
        event: awkward.Array,
        ref_obj: str,
        ref_type: str,
        cfg: DictConfig) -> list:
    """ Picks only those reference objects that pass the quality cuts

    Args:
        events: awkward.Array
            Event with all the branches
        ref_obj : str
            The object comparison tau to match to.
        ref_type : str
            Type of the reference object
        cfg : omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        good_ref_objects : list
            List of gen taus that pass the quality cuts
    """
    good_ref_objects = []
    for ref_idx in range(event[f"n{ref_obj}"]):
        if event[f"{ref_obj}_pt"][ref_idx] < cfg.quality_cuts.genTau.pt:
            continue
        if abs(event[f"{ref_obj}_eta"][ref_idx]) > cfg.quality_cuts.genTau.eta:
            continue
        if not ref_type == 'genTau':
            suitable = check_fake_suitability(
                                        event, ref_obj, ref_idx, ref_type, cfg)
            if not suitable:
                continue
        good_ref_objects.append(ref_idx)
    return good_ref_objects


def fill_eff_ntuple(events: awkward.Array, sample_type:str, cfg: DictConfig) -> None:
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
    ref_type = 'genTau'
    output_path = os.path.join(
                                cfg.output_dir,
                                cfg.TauID_eff.data_files[sample_type].path)
    eff_ntuple_file = uproot.recreate(output_path)
    all_vars = general.construct_var_names(cfg, ref_type)
    fill_entries = []
    for event in events:
        good_gen_taus = pick_suitable_ref_objects(event, cfg.genTau, ref_type, cfg)
        matched_gen_taus = pm.match_taus_to_refs(
                                good_gen_taus, event, cfg.genTau, cfg)
        for gen_tau_idx in good_gen_taus:
            fill_entry = {var: -999 for var in all_vars}
            for info_branch in cfg.allVariables.info:
                fill_entry[info_branch] = event[info_branch]
            for gen_var in cfg.allVariables.genTau:
                gen_key = f"{cfg.genTau}_{gen_var}"
                fill_entry[gen_key] = event[gen_key][gen_tau_idx]
            if gen_tau_idx in matched_gen_taus:
                matched_tau_idx = matched_gen_taus[gen_tau_idx]
                for tau_var in cfg.allVariables.tau:
                    tau_key = f"{cfg.comparison_tau}_{tau_var}"
                    fill_entry[tau_key] = event[tau_key][matched_tau_idx]
                best_match_jet_idx = event[f"{cfg.comparison_tau}_jetIdx"][matched_tau_idx]
                if best_match_jet_idx >= 0:
                    for jet_var in cfg.allVariables.jet:
                        fill_entry[f"Jet_{jet_var}"] = event[f"Jet_{jet_var}"][best_match_jet_idx]
            fill_entries.append(fill_entry)
    res = {key: [] for key in all_vars}
    {res[key].append(sub[key]) for sub in fill_entries for key in sub}
    eff_ntuple_file[cfg.TauID_eff.data_files[sample_type].tree_path] = res
    return None


def fill_fake_obj_ntuple(
        events: awkward.Array,
        fake_type: str,
        sample_type: str,
        cfg: DictConfig) -> None:
    """ Fills the fake ntuple for a given fake background and for a given
    reference fake object.

    Args:
        events : awkward.Array
            All events with all the variables from the input ntuple
        fake_type : str
            The type of fake to match to.
        cfg : omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        None
    """
    output_path = os.path.join(
                cfg.output_dir, cfg.TauID_fake.data_files[sample_type].path)
    fakes_ntuple_file = uproot.recreate(output_path)
    all_vars = general.construct_var_names(cfg, fake_type)
    fill_entries = []
    for event in events:
        good_gen_taus = pick_suitable_ref_objects(event, cfg.genTau, 'genTau', cfg)
        good_ref_objects = pick_suitable_ref_objects(
                                event, cfg.fakes[fake_type], 'genJet', cfg)
        matched_ref_objects = pm.match_taus_to_refs(
                                    good_ref_objects, event, 'GenJet', cfg)
        matched_gen_taus = pm.match_taus_to_refs(
                                good_gen_taus, event, cfg.genTau, cfg)
        for ref_idx in good_ref_objects:
            fill_entry = {var: -999 for var in all_vars}
            for info_branch in cfg.allVariables.info:
                fill_entry[info_branch] = event[info_branch]
            for obj_var in cfg.allVariables[fake_type]:
                fill_entry[f"{cfg.fakes[fake_type]}_{obj_var}"] = event[f"{cfg.fakes[fake_type]}_{obj_var}"][ref_idx]
            if ref_idx in matched_ref_objects:
                matched_tau_idx = matched_ref_objects[ref_idx]
                for tau_var in cfg.allVariables.tau:
                    fill_entry[f"{cfg.comparison_tau}_{tau_var}"] = event[f"{cfg.comparison_tau}_{tau_var}"][matched_tau_idx]
                if matched_tau_idx in matched_gen_taus.values():
                    gen_tau_idx = list(
                        matched_gen_taus.keys())[list(
                            matched_gen_taus.values()
                        ).index(matched_tau_idx)]
                    for gen_var in cfg.allVariables.genTau:
                        gen_key = f"{cfg.genTau}_{gen_var}"
                        fill_entry[gen_key] = event[gen_key][gen_tau_idx]
            fill_entries.append(fill_entry)
    res = {key: [] for key in all_vars}
    {res[key].append(sub[key]) for sub in fill_entries for key in sub}
    fakes_ntuple_file[cfg.TauID_eff.data_files[sample_type].tree_path] = res
    return None


def fill_all_fake_ntuples(
        events: awkward.Array,
        sample_type: str,
        cfg: DictConfig) -> None:
    """ Fills all the fake ntuples for the objects listed in configuration

    Args:
        events : awkward.Array
            All events with all the variables from the input ntuple
        cfg : omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        None
    """
    # for fake_type in cfg.fakes:
        # fill_fake_obj_ntuple(events, fake_type, cfg)
    fill_fake_obj_ntuple(events, "genJet", sample_type, cfg)
