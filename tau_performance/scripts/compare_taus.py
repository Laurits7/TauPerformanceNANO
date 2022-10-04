import hydra
from omegaconf import DictConfig
from tau_performance.tools import decay_mode_reconstruction as dm
from tau_performance.tools.efficiency import Efficiency
from tau_performance.tools import plot_eff_fake as pef
from tau_performance.tools.tau_response import Response
from tau_performance.tools import plot_response as pr
from tau_performance.tools import plot_roc_curve as prc
import os


@hydra.main(config_path='../config', config_name='config')
def main(cfg: DictConfig) -> None:
    os.makedirs(cfg.output_dir, exist_ok=True)
    # dm.decay_mode_reconstruction(cfg, cfg.comparison_tau)
    # dm.decay_mode_reconstruction(cfg, cfg.comparisons.baseline_tau)

    ######### Energy responses ###############
    # base_responses = Response(
    #                 "ggH_htt", cfg.comparisons.baseline_tau, cfg.genTau, cfg)
    # comp_responses = Response(
    #                           "ggH_htt", cfg.comparison_tau, cfg.genTau, cfg)
    # pr.plot_tau_comparison_responses(
    #                           base_responses, comp_responses, "ggH_htt", cfg)

    comp_eff_input_path = '/home/laurits/tmp34/normal/ggH_htt_tauID_eff.root'
    comp_fake_input_path = '/home/laurits/tmp34/normal/QCD_tauID_fake.root'
    eff_tree_path = 'Events'
    comp_eff = Efficiency('ggH_htt', cfg.comparison_tau, comp_eff_input_path, eff_tree_path, cfg.genTau, cfg)
    comp_fake = Efficiency('QCD', cfg.comparison_tau, comp_fake_input_path, eff_tree_path, cfg.fakes.recoJet, cfg)

    base_eff_input_path = '/home/laurits/tmp34/relaxed/ggH_htt_tauID_eff.root'
    base_fake_input_path = '/home/laurits/tmp34/relaxed/QCD_tauID_fake.root'
    base_eff = Efficiency('ggH_htt', cfg.comparisons.baseline_tau, base_eff_input_path, eff_tree_path, cfg.genTau, cfg)
    base_fake = Efficiency('QCD', cfg.comparisons.baseline_tau, base_fake_input_path, eff_tree_path, cfg.fakes.recoJet, cfg)
    ################ ROC curve ################
    output_dir = '/home/laurits/tmp34/normal/'
    prc.compare_rocs(base_eff.total_efficiencies, base_fake.total_efficiencies, "Relaxed", comp_eff.total_efficiencies, comp_fake.total_efficiencies, "Normal", output_dir)


if __name__ == '__main__':
    main()
