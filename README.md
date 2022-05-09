## UIUC CS598 Deep Learning for Healthcare Team 39

### Replication and Extension of "Learning Tasks for Multitask Learning"

**Citation to the original paper**

Suresh, Harini, Gong, Jen J, Guttag, John V. Learning Tasks for Multitask Learning: Heterogenous Patient Populations in the ICU. In Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (KDD '18). Association for Computing Machinery, New York, NY, USA, 802–810. https://doi.org/10.1145/3219819.3219930

**Link to the original paper’s repo (if applicable)**

https://github.com/mit-ddig/multitask-patients

**Dependencies**

Dependencies to build dataset files on Mac OS X:

1. Install Homebrew
    ```
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
1. Install make and postgresql. Start postgresql.
    ```
    brew install make postgresql
    postgres -D /usr/local/var/postgres &
    /usr/local/opt/postgres/bin/createuser -s postgres
    ```

Python package dependencies:

```
os
sys
argparse
numpy
pandas
tensorflow
keras
sklearn
pickle
```

**Data download instructions**

1. Go to https://physionet.org/content/mimiciii/1.4/
1. Follow the credentialling instructions and sign up for access
1. Download the 6.2GB zip file containing all the data and unzip to the `data` folder at the top level of this repository


**Preprocessing code + command (if applicable)**

Steps to process the dataset files on Mac OS X:

1. Download the MIMIC_Extract repository from https://github.com/MLforHealth/MIMIC_Extract
1. Build the MIMIC-III postgresql database
    ```
    cd mimic-code/mimic-iii/buildmimic/postgres/ && make create-user mimic-gz datadir="../../../../data/mimic-iii-clinical-database-1.4/"
    ```
1. Export the SAPSII and code_status tables to csv files and save in the `data` folder at the top level of this repository

Preprocessing code can be found in [preprocess.py](./preprocess.py).
It needs to be executed via terminal/command line in the folder where this repository is cloned.
```
python preprocess.py
```

**Training code + command (if applicable)**

Training code can be found in [generate_clusters.py](./generate_clusters.py) and [run_mortality_prediction.py](./run_mortality_prediction.py).

It needs to be executed via terminal/command line in the folder where this repository is cloned.
```
python generate_clusters.py
python run_mortality_prediction.py
```

Relevant run_mortality_prediction.py command line arguments:
    * "--model_type": "One of {'GLOBAL', MULTITASK', 'SEPARATE'}"
    * "--cohort_filepath": "This is the filename containing the cohort membership for each example"
    * "--data_hours": default=24, "The number of hours of data to use in making the prediction."

Relevant generate_clusters.py command line arguments:
    * "--data_hours": default=24, "The number of hours of data to use in making the prediction."

**Evaluation code + command (if applicable)**

Evaluation code is invoked through `run_mortality_prediction.py` (see above)

**Pretrained model (if applicable)**

The model can be run using the code in [run_mortality_prediction.py](./run_mortality_prediction.py).
It needs to be executed via terminal/command line in the folder where this repository is cloned.
```
python run_mortality_prediction.py
```

**Table of results (no need to include additional experiments, but main reproducibility result should be included)**

*Claim 1 Results - Multi-Task Out Performs Global*

|       | Global | Global | Global | Multi-Task |	Multi-Task | Multi-Task |
| ---   | ---    | ---    | ---    |  ---       | ---        | ---        |
|       | Paper	 | Us		  | Diff   |  Paper	    | Us		     | Diff       |
| CCU   | 0.862  | 0.800  | 0.062  |  0.861     | 0.644      | 0.217      |
| CSRU  | 0.849  | 0.857  |-0.008  |  0.867     | 0.724      | 0.143      |
| MICU  | 0.814  | 0.786  | 0.028  |  0.832     | 0.753      | 0.079      |
| SICU  | 0.839  | 0.793  | 0.046  |  0.855     | 0.747      | 0.108      |
| TSICU | 0.846  | 0.827  | 0.019  |  0.869     | 0.778      | 0.091      |
| Macro | 0.842  | 0.828  | 0.014  |  0.857     | 0.736      | 0.121      |
| Micro | 0.852  | 0.842  | 0.01   |  0.866     | 0.789      | 0.077      |

*Claim 2 Results - First 24 Hours of Patient's Stay by Care Unit*

|       | Global | Global | Global | Multi-Task |	Multi-Task | Multi-Task |
| ---   | ---    | ---    | ---    |  ---       | ---        | ---        |
|       | Paper	 | Us		  | Diff   | Paper	    | Us		     | Diff       |
| CCU	  | 0.862	 | 0.800	|-0.06	 | 0.861	    | 0.672	     | -0.19      |
| CSRU	| 0.849	 | 0.857	| 0.01	 | 0.867	    | 0.950	     |  0.08      |
| MICU	| 0.814	 | 0.786	|-0.03	 | 0.832	    | 0.839	     |  0.01      |
| SICU	| 0.839	 | 0.793	|-0.05	 | 0.855	    | 0.860	     |  0.01      |
| TSICU | 0.846	 | 0.827	|-0.02	 | 0.869	    | 0.733	     | -0.14      |
| Macro | 0.842	 | 0.813	|-0.03	 | 0.857	    | 0.811	     | -0.05      |
| Micro | 0.852	 | 0.842	|-0.01	 | 0.866	    | 0.844	     | -0.02      |

*Claim 2 Results - First 48 Hours of Patient's Stay by Care Unit*

|       | Global | Global | Global | Multi-Task |	Multi-Task | Multi-Task |
| ---   | ---    | ---    | ---    |  ---       | ---        | ---        |
|       | Paper	 | US		  | Diff   | Paper	    | US		     | Diff       |
| CCU	  | 0.862	 | 0.818	| 0.02	 | 0.861      | 0.025	     | -0.65      |
| CSRU  | 0.849	 | 0.377	|-0.48	 | 0.867      | 0.741	     | -0.21      |
| MICU  | 0.814	 | 0.809	| 0.02	 | 0.832      | 0.784	     | -0.05      |
| SICU  | 0.839	 | 0.813	| 0.02	 | 0.855      | 0.671	     | -0.19      |
| TSICU | 0.846	 | 0.698	|-0.13	 | 0.869      | 0.725	     | -0.01      |
| Macro | 0.842	 | 0.703	|-0.11	 | 0.857      | 0.589	     | -0.22      |
| Micro | 0.852	 | 0.806	|-0.04	 | 0.866      | 0.777	     | -0.07      |

*Claim 2 Results*

|       | Global | Global | Global | Multi-Task |	Multi-Task | Multi-Task |
| ---   | ---    | ---    | ---    |  ---       | ---        | ---        |
|       | Paper	 | US		  | Diff   | Paper	    | US		     | Diff       |
| 0	    | 0.803	 | 0.893	| 0.090	 | 0.819	    | 0.903	     | 0.010      |
| 1	    | 0.811	 | 0.811	| 0.000	 | 0.829	    | 0.705	     |-0.106      |
| 2	    | 0.814	 | 0.902	| 0.088	 | 0.821	    | 0.841	     |-0.061      |
| mac	  | 0.809	 | 0.869	| 0.060	 | 0.823	    | 0.816	     |-0.053      |
| mic	  | 0.852	 | 0.854	| 0.002	 | 0.858	    | 0.800	     |-0.054      |

*Claim 3 Results (AUC)*
|       | Global | Multi-Task |
| ---   | ---    | ---    |
|       | Paper	 | US		  |
| 0	    | 0.885	 | 0.898	|
| 1	    | 0.774	 | 0.746	|
| 2	    | 0.583	 | 0.862	|
| mac	  | 0.748	 | 0.835	|
| mic	  | 0.802	 | 0.816	|


## Original Paper repository README.md follows:

## Learning Tasks for Multitask Learning

The code in this repository implements the models described in the paper *Learning Tasks for Multitask Learning: Heterogenous Patient Populations in the ICU* (KDD 2018). There are two files:

1. generate_clusters.py, which trains a sequence-to-sequence autoencoder on patient timeseries data to produce a dense representation, and then fits a Gaussian Mixture Model to the samples in this new space.

2. run_mortality_prediction.py, which contains methods to preprocess data, as well as train and run a predictive model to predict in-hospital mortality after a certain point, given patients' physiological timeseries data.

For more information on the arguments required to run each of these files, use the --help flag.

### Data

Without any modification, this code assumes that you have the following files in a 'data/' folder:
1. X.h5: an hdf file containing one row per patient per hour. Each row should include the columns {'subject_id', 'icustay_id', 'hours_in', 'hadm_id'} along with any additional features.
2. static.csv: a CSV file containing one row per patient. Should include {'subject_id', 'hadm_id', 'icustay_id', 'gender', 'age', 'ethnicity', 'first_careunit'}.
3. saps.csv: a CSV file containing one row per patient. Should include {'subject_id', 'hadm_id', 'icustay_id', 'sapsii'}. This data is found in the saps table in MIMIC III.
4. code_status.csv: a CSV file containing one row per patient. Should include {'subject_id', 'hadm_id', 'icustay_id', 'timecmo_chart', 'timecmo_nursingnote'}. This data is found in the code_status table of MIMIC III.
