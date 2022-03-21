import hydra
from omegaconf import DictConfig
from tau_performance.tools import decay_mode_reconstruction as dm
from tau_performance.tools import tau_id_efficiency as id_eff
import os


@hydra.main(config_path='../config', config_name='config')
def main(cfg: DictConfig) -> None:
    os.makedirs(cfg.output_dir, exist_ok=True)
    dm.decay_mode_reconstruction(cfg)
    id_eff.plot_tau_id_efficiency(cfg)


if __name__ == '__main__':
    main()
