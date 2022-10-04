""" Tools for matching particles objects to taus """
import numpy as np
import awkward
from omegaconf import DictConfig
from collections import Counter


def deltaPhi(phi1: float, phi2: float) -> float:
    """ Calculates the difference in azimuthal angle between two particles

    Args:
        phi1 : float
            The azimuthal angle of the first particle
        phi2: float
            The azimuthal angle of the second particle

    Returns:
        dPhi : float
            The difference in azimuthal angle.
    """
    phi = np.abs(phi1 - phi2)
    if phi <= np.pi:
        return phi
    else:
        return 2*np.pi - phi


def deltaR(eta1: float, phi1: float, eta2: float, phi2: float) -> float:
    """ Calculates the angular separation between two particles given the
    pseudorapidities and azimuthal angles of both particles

    Args:
        eta1 : float
            The pseudorapidity of the first particle
        phi1 : float
            The azimuthal angle of the first particle
        eta2 : float
            The pseudorapidity of the second particle
        phi2: float
            The azimuthal angle of the second particle

    Returns:
        deltaR : float
            The angular separation between two particles.
    """
    deta = eta1 - eta2
    dphi = deltaPhi(phi1, phi2)
    return np.hypot(deta, dphi)


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
        ref_obj: str,
        cfg: DictConfig) -> dict:
    """ Calculates the distances of the conflicting objects to the taus

    Args:
        objects_sharing_tau: list[int]
            Objects that share the same tau between themselves
        matched_objects: dict
            The object indices with matching tau index
        event: awkward.Array
            The event entry with all the variables
        ref_obj : str
            The object comparison tau to match to.
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
                event[f"{ref_obj}_eta"][obj_idx],
                event[f"{ref_obj}_phi"][obj_idx]
            )
    return distances


def resolve_matching_conflicts(
        objects_sharing_tau: list[int],
        matched_objects: dict,
        event: awkward.Array,
        ref_obj: str,
        cfg: DictConfig) -> dict:
    """ Resolves the conflicts of objects that share the same tau.

    Args:
        objects_sharing_tau: list[int]
            Objects that share the same tau between themselves
        matched_objects: dict
            The object indices with matching tau index
        event: awkward.Array
            The event entry with all the variables
        ref_obj : str
            The object comparison tau to match to.
        cfg: omegaconf.DictConfig
            The configuration. Branch names are inferred from that.

    Returns:
        matched_objects_ : dict
            The matched taus to the requested objects
"""
    matched_objects_ = matched_objects.copy()
    distances = calculate_conflicting_obj_distances(
                    objects_sharing_tau, matched_objects_, event, ref_obj, cfg)
    for obj_idx in objects_sharing_tau:
        del matched_objects_[obj_idx]
    while distances != {}:
        shortest_distance_key = min(distances, key=distances.get)
        obj_idx = int(shortest_distance_key.split("_")[0])
        tau_idx = int(shortest_distance_key.split("_")[1])
        matched_objects_[obj_idx] = tau_idx
        for_removal = []
        for distance_key in distances.keys():
            obj_part, tau_part = distance_key.split("_")
            if (obj_part == str(obj_idx)) or (tau_part == str(tau_idx)):
                for_removal.append(distance_key)
        for distance_key in for_removal:
            del distances[distance_key]
    return matched_objects_


def match_taus_to_refs(
        reference_obj_idxs: list[int],
        event: awkward.Array,
        ref_obj: str,
        cfg: DictConfig) -> dict:
    """ Matches taus to the reference objects and reports the double count
    after the matching.

    Args:
        reference_obj_idxs : list[int]
            The indices of the reference objects to which to match
        event: awkward.Array
            The event entry with all the variables
        ref_obj : str
            The object comparison tau to match to.
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
                event[f"{ref_obj}_eta"][obj_idx],
                event[f"{ref_obj}_phi"][obj_idx]
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
            objects_sharing_tau, matched_objects, event, ref_obj, cfg)
    return matched_objects
