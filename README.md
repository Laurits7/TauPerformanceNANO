# Tau release validation suite for nanoAOD

## Setup

Clone this repository & enter the directory:

```bash
git clone https://github.com/rmanzoni/TauPerformanceNANO.git
cd TauPerformanceNANO
```

Make sure you are using python3 and then create a virtual environment and activate it:
```bash
python -m venv tauID_env
source tauID_env/bin/activate
```

Install the necessary packages and this package itself:

```bash
pip install -r requirements.txt
pip install -e .
```


Now every time you wish to use this package activate the virtual environment:

```bash
source tauID_env/bin/activate
```

## Running

The configuration files are all stored in the tau_preformance/config directory. The config files are read in by [hydra](https://hydra.cc/docs/advanced/override_grammar/basic/). Configuration parameters can be overriden on the command line as shown also in Hydra tutorials.

So when we want to change output directory and the tau that we are evaluating:

```bash
python produce_plots.py output_dir=/home/user/tmp/HPSTau comparison_tau=Tau
```