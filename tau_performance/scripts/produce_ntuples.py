""" Produces the ntuples that are used as the input for plotting """
import os
import hydra
from omegaconf import DictConfig
from tau_performance.tools import ntuple_production as npro
from tau_performance.tools import general


@hydra.main(config_path='../config', config_name='config')
def main(cfg: DictConfig) -> None:
    os.makedirs(cfg.output_dir, exist_ok=True)
    print("Started loading signal events")
    events = general.load_events(
                                file_path=cfg.eff_file.path,
                                tree_name=cfg.eff_file.tree)
    print("Events loaded, filling ntuples for signal")
    npro.fill_eff_ntuple(events, cfg)
    print("Finished filling ntuples for signal, loading events for fakes")
    events = general.load_events(
                                file_path=cfg.fakes_file.path,
                                tree_name=cfg.fakes_file.tree)
    print("Events loaded, filling ntuples for fakes")
    npro.fill_all_fake_ntuples(events, cfg)
    print("Fakes ntuple filled")


if __name__ == '__main__':
    main()
