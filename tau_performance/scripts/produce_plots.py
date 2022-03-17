import hydra
from omegaconf import DictConfig
from tau_performance.tools import decay_mode_reconstruction as dm
from tau_performance.tools
import os


@hydra.main(config_path='../config', config_name='config')
def main(cfg: DictConfig) -> None:
    dm.decay_mode_reconstruction(cfg)



if __name__ == '__main__':
    main()
