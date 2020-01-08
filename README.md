# Tau release validation suite for nanoAOD

## Setup

Clone this repository:

    git clone https://github.com/rmanzoni/TauPerformanceNANO.git

## Running

First, get the nanoAOD root files zou want to use and copy them to any local directory. The script `CopyToMyEOS.py` may be of help, after you change the path to where the samples should be copied to. The samples are read from DAS.

Next, produce the ntuple. This is done using `ProduceNtuple.py`. Required arguments include:
* `--file`: Directory containing the sample aquired in the previous step
* `--output`: Output root file name
* `--eff`/`--fake`: Specify either if your samples contain either true Taus or fake Taus

Example:

    python ProduceNtuple.py --file ZTT_nanorootfiles --output nano_ztt.root --eff

Now you can make the plots. Just run either `Eff_plot.py` or `Fake_plot.py` and add the ntuple rootfile as an argument. You can compare the efficiencies or fake rate of multiple ntuples by adding all of them as arguments. This will produce plots for each working point.

Example:

    python Eff_plot.py nano_ztt.root
    python Eff_plot.py nano_ztt.root nano_tentau.root

The scripts `Response_plot.py` can be used in the same manner. For `Roc_plot.py`, ntuples for real Taus and fake Taus are needed. Give the ntuple for the efficiency sample first, then for the fake sample. You can also add more ROC curves into the same plots by again adding another efficiency- and fake ntuple.

Example:

    python Roc_plot.py nano_ztt.root nano_ttbar.root
    python Roc_plot.py nano_ztt.root nano_ttbar.root nano_ztt.root nano_qcd.root

