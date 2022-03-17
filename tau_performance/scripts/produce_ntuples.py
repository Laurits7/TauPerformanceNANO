""" Produces the ntuples that are used as the input for plotting """
import os
import hydra
from omegaconf import DictConfig
from tau_performance.tools import ntuple_production as npro
from tau_performance.tools import general


@hydra.main(config_path='../config', config_name='config')
def main(cfg: DictConfig) -> None:
    if cfg.do_eff:
        file_path = cfg.eff_file.path
        tree_name = cfg.eff_file.tree
    elif cfg.do_fake:
        file_path = cfg.fakes_file.path
        tree_name = cfg.fakes_file.tree
    print("Started event loading")
    events = general.load_events(file_path=file_path, tree_name=tree_name)
    print("Events loaded, filling ntuples")
    npro.fill_eff_ntuple(events, cfg)


if __name__ == '__main__':
    main()
