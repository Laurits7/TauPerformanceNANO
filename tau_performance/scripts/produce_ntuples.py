""" Produces the ntuples that are used as the input for plotting """
import os
import hydra
from omegaconf import DictConfig
from tau_performance.tools import ntuple_production as npro
from tau_performance.tools import general


@hydra.main(config_path='../config', config_name='config')
def main(cfg: DictConfig) -> None:
    os.makedirs(cfg.output_dir, exist_ok=True)
    signal_info = cfg.eff_file
    background_info = cfg.fakes_file
    print(f"Started loading signal ({signal_info.sample_name}) "
        f"events from {signal_info.path}")
    signal_events = general.load_events(
                                file_path=signal_info.path,
                                tree_name=signal_info.tree)
    print("Events loaded, filling ntuples for signal")
    npro.fill_ref_obj_ntuple(
                        signal_events, cfg.genTau, signal_info.sample_name, cfg)
    npro.fill_ref_obj_ntuple(
                signal_events, cfg.fakes.recoJet, signal_info.sample_name, cfg)
    print("Finished filling ntuples for background.")
    print(f"Loading events for fakes ({background_info.sample_name}) "
        f"events from {background_info.path}")
    background_events = general.load_events(
                                file_path=background_info.path,
                                tree_name=background_info.tree)
    print("Events loaded, filling ntuples for fakes")
    npro.fill_ref_obj_ntuple(
                background_events,  cfg.genTau, background_info.sample_name, cfg)
    npro.fill_ref_obj_ntuple(
         background_events, cfg.fakes.recoJet, background_info.sample_name, cfg)
    print("Fakes ntuple filled")


if __name__ == '__main__':
    main()
