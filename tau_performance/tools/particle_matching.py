""" Tools for matching particles in a nTuple """
import numpy as np
import awkward
from omegaconf import DictConfig
from collections import Counter


def deltaPhi(phi1: float, phi2: float) -> float:
    phi = np.abs(phi1 - phi2)
    if phi <= np.pi:
        return phi
    else:
        return 2*np.pi - phi


def deltaR(eta1: float, phi1: float, eta2: float, phi2: float) -> float:
    """ Calculates the angular distance"""
    deta = eta1 - eta2
    dphi = deltaPhi(phi1, phi2)
    return np.hypot(deta, dphi)


def get_ref_value(
        part_idx: int,
        event: awkward.Array,
        variable: str,
        cfg: DictConfig) -> float:
    """ Gets the reference value of a particle

    Args:
        part_idx : int
            Index of the particle in the event
        event: awkward.Array
            The event entry with all the variables
        variable: str
            Name of the variable the reference value is returned, e.g. "eta"
        cfg: omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        ref_value : float
            The reference value queried
    """
    if cfg.do_eff:
        variable_full_name = f"{cfg.variables.genTau}_{variable}"
    elif cfg.do_fake:
        if cfg.fake_matching.recoJets:
            variable_full_name = f"{cfg.variables.recoJet}_{variable}"
        elif cfg.fake_matching.fakeEle or cfg.fake_matching.fakeMu:
            variable_full_name = f"{cfg.variables.genParticle}_{variable}"
        elif cfg.fake_matching.fakeJet:
            variable_full_name = f"{cfg.variables.genJet}_{variable}"
        else:
            raise ValueError(
                "Fake matching was requested but no fake matching scenario was chosen")
    else:
        raise ValueError("No scenario (efficiency/fake rate) was chosen")
    ref_value = event[variable_full_name][part_idx]
    return ref_value


def check_for_double_count(matched_objects: dict) -> tuple[int, list[int]]:
    """ Counts the number of taus that are represented multiple times and
    returns the objects that share the same tau reference.

    Args:
        matched_objects : dict
            The objects and the taus matched to them. Key is the object index
            and the value is tau index

    Returns:
        double_count : int
            Number of doublecounted taus
        objects_sharing_tau : list[int]
            Indices of the objects that have duplicate taus
    """
    objects_sharing_tau = []
    all_taus_w_duplicates = list(matched_objects.values())
    unique_taus = set(all_taus_w_duplicates)
    duplicate_taus = list(
            (Counter(all_taus_w_duplicates) - Counter(unique_taus)).elements())
    for duplicate_tau in duplicate_taus:
        duplicate_locs = list(np.where(
            np.array(all_taus_w_duplicates) == duplicate_tau)[0])
        for duplicate_loc in duplicate_locs:
            objects_sharing_tau.append(list(matched_objects.keys())[duplicate_loc])
    double_count = len(duplicate_taus)
    return double_count, objects_sharing_tau


def calculate_conflicting_obj_distances(
        objects_sharing_tau: list[int],
        matched_objects: dict,
        event: awkward.Array,
        cfg: DictConfig) -> dict:
    """ Calculates the distances of the conflicting objects to the taus

    Args:
        objects_sharing_tau: list[int]
            Objects that share the same tau between themselves
        matched_objects: dict
            The object indices with matching tau index
        event: awkward.Array
            The event entry with all the variables
        cfg: omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        distances : dict
            Distances between all conflicting taus and objects
    """
    distances = {}
    duplicate_taus = [matched_objects[obj_idx] for obj_idx in objects_sharing_tau]
    for obj_idx in objects_sharing_tau:
        for tau_idx in duplicate_taus:
            distance_key = "_".join([str(obj_idx), str(tau_idx)])
            distances[distance_key] = deltaR(
                event["%s_eta" %cfg.comparison_tau][tau_idx],
                event["%s_phi" %cfg.comparison_tau][tau_idx],
                get_ref_value(obj_idx, event, "eta", cfg),
                get_ref_value(obj_idx, event, "phi", cfg)
            )
    return distances


def resolve_matching_conflicts(
        objects_sharing_tau: list[int],
        matched_objects: dict,
        event: awkward.Array,
        cfg: DictConfig) -> dict:
    """ Resolves the conflicts of objects that share the same tau.

    Args:
        objects_sharing_tau: list[int]
            Objects that share the same tau between themselves
        matched_objects: dict
            The object indices with matching tau index
        event: awkward.Array
            The event entry with all the variables
        cfg: omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        matched_objects : dict
            The matched taus to the requested objects
"""
    distances = calculate_conflicting_obj_distances(
                            objects_sharing_tau, matched_objects, event, cfg)
    for obj_idx in objects_sharing_tau:
        del matched_objects[obj_idx]
    while distances != {}:
        shortest_distance_key = min(distances, key=distances.get)
        obj_idx = int(shortest_distance_key.split("_")[0])
        tau_idx = int(shortest_distance_key.split("_")[1])
        matched_objects[obj_idx] = tau_idx
        for_removal = []
        for distance_key in distances.keys():
            if distance_key.startswith(str(obj_idx)) or distance_key.endswith(str(tau_idx)):
                for_removal.append(distance_key)
        for distance_key in for_removal:
            del distances[distance_key]
    return matched_objects  # Is return correct here? Is the change maybe made "in-place"


def match_taus_to_refs(
        reference_obj_idxs: list[int],
        event: awkward.Array,
        cfg: DictConfig) -> dict:
    """ Matches taus to the reference objects and reports the double count
    after the matching.

    Args:
        reference_obj_idxs : list[int]
            The indices of the reference objects to which to match
        event: awkward.Array
            The event entry with all the variables
        cfg: omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        matched_objects : dict
            The matched taus to the requested objects
    """
    matched_objects = {}
    for obj_idx in reference_obj_idxs:
        best_match_idx = -1
        dR_max = cfg.matching.dR_max
        for tau_idx in range(event[f"n{cfg.comparison_tau}"]):
            dR = deltaR(
                event["%s_eta" %cfg.comparison_tau][tau_idx],
                event["%s_phi" %cfg.comparison_tau][tau_idx],
                get_ref_value(obj_idx, event, "eta", cfg),
                get_ref_value(obj_idx, event, "phi", cfg)
            )
            if dR > dR_max:
                continue
            dR_max = dR
            best_match_idx = tau_idx
        if best_match_idx >= 0:
            matched_objects[obj_idx] = best_match_idx
    double_count, objects_sharing_tau = check_for_double_count(matched_objects)
    if double_count > 0:
        matched_objects = resolve_matching_conflicts(
            objects_sharing_tau, matched_objects, event, cfg)
    return matched_objects
