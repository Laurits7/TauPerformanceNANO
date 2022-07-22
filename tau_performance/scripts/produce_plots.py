import hydra
from omegaconf import DictConfig
from tau_performance.tools import decay_mode_reconstruction as dm
from tau_performance.tools.efficiency import Efficiency
from tau_performance.tools import plot_eff_fake as pef
from tau_performance.tools.tau_response import Response
from tau_performance.tools import plot_response as pr
from tau_performance.tools import plot_roc_curve as prc
import os


def infer_input_path_and_tree(ref_obj, sample_name, cfg):
    eff_type = "eff" if ref_obj == cfg.genTau else "fake"
    file_name = cfg[f"TauID_{eff_type}"].data_files[sample_name].path
    tree_path = cfg[f"TauID_{eff_type}"].data_files[sample_name].tree_path
    path = os.path.join(cfg.output_dir, file_name)
    return path, tree_path

@hydra.main(config_path='../config', config_name='config')
def main(cfg: DictConfig) -> None:
    os.makedirs(cfg.output_dir, exist_ok=True)

    ################### DM RECONSTRUCTION ###################
    dm.decay_mode_reconstruction(cfg)


    ################### EFFICIENCY ###################
    eff_input_path, eff_tree_path = infer_input_path_and_tree(cfg.genTau, 'ggH_htt', cfg)
    eff = Efficiency(
                    'ggH_htt', cfg.comparison_tau, eff_input_path,
                    eff_tree_path, cfg.genTau, cfg)
    efficiencies = eff.efficiencies
    eff_reco_histos = eff.reco_histos
    eff_obj = cfg.genTau
    pef.plot_efficiencies(efficiencies, 'eff', eff_obj, cfg)
    pef.plot_eff_reco_histos(eff_reco_histos, 'eff', cfg)


    ################### FAKE RATES ###################
    fake_input_path, fake_tree_path = infer_input_path_and_tree(cfg.fakes.recoJet, 'QCD', cfg)
    fake = Efficiency('QCD', cfg.comparison_tau, fake_input_path,
                    fake_tree_path, cfg.fakes.recoJet, cfg)
    fake_rates = fake.efficiencies
    fake_reco_histos = fake.reco_histos
    fake_obj = cfg.fakes.recoJet
    pef.plot_efficiencies(fake_rates, 'fake', fake_obj, cfg)
    pef.plot_eff_reco_histos(fake_reco_histos, 'fake', cfg)


    ################### RESPONSE ###################
    res_eff = Response("ggH_htt", cfg.genTau, cfg)
    pr.plot_all_responses(res_eff.energy_response, cfg.genTau, "ggH_htt", cfg)


    ###################   ROC   ###################
    qcd_total_fakerates = fake.total_efficiencies
    htt_total_eff = eff.total_efficiencies
    prc.plot_roc_curve(htt_total_eff, qcd_total_fakerates, cfg)


if __name__ == '__main__':
    main()
