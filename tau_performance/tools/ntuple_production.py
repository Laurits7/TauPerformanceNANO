import os
import uproot
import awkward
from omegaconf import DictConfig
from collections import defaultdict
# from . import particle_matching as pm
# from . import general
from tau_performance.tools import particle_matching as pm
from tau_performance.tools import general

def check_pollution_from_non_jets(
        event: awkward.Array,
        ref_obj: str,
        ref_idx: int,
        cfg: DictConfig) -> list:
    """ Checks pollution from non-jets. Compares to genJet regardless of whether
    RECO or GEN jets are used for tau-matching

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
        print(f"{event.nGenJet} and {event.Jet_genJetIdx[ref_idx]}")
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
        cfg: DictConfig) -> list:
    """ Picks only those reference objects that pass the quality cuts

    Args:
        events: awkward.Array
            Event with all the branches
        ref_obj : str
            The object comparison tau to match to.
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
        # if ref_obj != cfg.genTau:
        #     if (event["Jet_genJetIdx"][ref_idx] < 0) or (event["Jet_genJetIdx"][ref_idx] >= event["nGenJet"]):
        #         continue
        #         print("___________________________---")
        #         print(event["Jet_genJetIdx"][ref_idx])
        #         print(event["nGenJet"])
        #         print("___________________________---")
        #     suitable = check_pollution_from_non_jets(
        #                                 event, ref_obj, ref_idx, cfg)
        #     if not suitable:
        #         continue
        good_ref_objects.append(ref_idx)
    return good_ref_objects



def fill_ref_obj_ntuple(
        events: awkward.Array,
        ref_obj: str,
        sample_name: str,
        cfg: DictConfig) -> None:
    """Foo bar baz baax

    Args:
        events : awkward.Array
            All events with all the variables from the input ntuple
        ref_object : str
            The reference object for the matching
        sample_name : str
            Name of the sample to be ntupelized
        cfg : omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        None
    """
    if ref_obj != cfg.genTau:
        data_file = cfg.TauID_fake.data_files[sample_name].path
        tree_path = cfg.TauID_fake.data_files[sample_name].tree_path
    else:
        data_file = cfg.TauID_eff.data_files[sample_name].path
        tree_path = cfg.TauID_eff.data_files[sample_name].tree_path
    output_path = os.path.join(cfg.output_dir, data_file)
    all_vars = general.construct_var_names(cfg, cfg.genTau)
    opp_obj = cfg.genTau if ref_obj != cfg.genTau else cfg.fakes.recoJet
    fill_entries = []
    for event in events:
        good_ref_objects = pick_suitable_ref_objects(event, ref_obj, cfg)
        good_opp_objects = pick_suitable_ref_objects(event, opp_obj, cfg)
        matched_ref_objects = pm.match_taus_to_refs(
                                        good_ref_objects, event, ref_obj, cfg)
        matched_opp_objects = pm.match_taus_to_refs(
                                        good_opp_objects, event, opp_obj, cfg)
        for ref_idx in good_ref_objects:
            fill_entry = {var: -999 for var in all_vars}
            for info_branch in cfg.allVariables.info:
                fill_entry[info_branch] = event[info_branch]
            for obj_var in cfg.allVariables[ref_obj]:
                obj_key = f"{ref_obj}_{obj_var}"
                fill_entry[obj_key] = event[obj_key][ref_idx]
            if ref_idx in matched_ref_objects:
                matched_tau_idx = matched_ref_objects[ref_idx]
                for tau_var in cfg.allVariables.tau:
                    tau_key = f"{cfg.comparison_tau}_{tau_var}"
                    fill_entry[tau_key] = event[tau_key][matched_tau_idx]
                if matched_tau_idx in matched_opp_objects.values():
                    matched_opp_obj_idx = list(
                           matched_opp_objects.values()).index(matched_tau_idx)
                    opp_obj_idx = list(matched_opp_objects.keys())[matched_opp_obj_idx]
                    for opp_var in cfg.allVariables[opp_obj]:
                        opp_obj_key = f"{opp_obj}_{opp_var}"
                        fill_entry[opp_obj_key] = event[opp_obj_key][matched_opp_obj_idx]
            fill_entries.append(fill_entry)
    res = {key: [] for key in all_vars}
    {res[key].append(sub[key]) for sub in fill_entries for key in sub}
    with uproot.recreate(output_path) as ntuple_file:
        ntuple_file[tree_path] = res
    return None
