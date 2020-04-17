# Chromatography Simulator
The purpose of this package is to simulate chromatography experiments for the purpose of analysing tailing factors.

## Setup
In order to run the package, first you will need to set up a virtual environment running python3.6, which is easily done using `Homebrew`, `pip` and `virtualenv`.
#### Homebrew and Python
Begin by downloading `Homebrew` so that we can get the right version of python:\
`ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

To check Homebrew installed correctly, check using:\
`brew --version`

Hopefully that works and you can then get the most up-to-date version of python by running:\
`brew install python`

Check what version of python you are running using (and remember this for later):\
`python3 --version`


#### Pip
Then get the latest version of `pip`:\
`sudo easy_install pip` \
`sudo pip install --upgrade pip`

This should allow you to download python packages.
One package you will need is virtualenv, which allows you to set up virtual environments, i.e. isolated python instances, which allows you to easily manage package dependencies:\
`pip install virtualenv`

#### VirtualEnv
From here we will create your virtual environment using (where `3.x` is the version of python you are running):\
`virtualenv -p python3.x venv`

To activate your virtualenv:\
`source venv/bin/activate`

From here if you can install the requirements to run the package using:\
`pip install -r requirements.txt`


## Using the package

### Chromatography Simulation
To simulate the chromatography results, update the `peak_parameters.csv` file (or change the filename in `settings.py`)
 to reflect the details of the experiment you wish to simulate.\
It is important to note that the label names for the peaks do not matter, except their must be a "Main" peak as the peaks are normalised to this.
Here, `t` represents the peak centre (with no tailing), `w` is the width, `s` is the standard deviation, `response` is the peak height and the `tailing factor` is the desired asymmetry calculated at 5% max height.

To run the simulation simply use:\
`python chromatography_simulator.py --filename <filename> --parameters <path>`

where `<filename>` is the desired name of the simulated graph and raw data, which are saved to the output directory.
Additionally, the `--parameters <path>` flag can be used to specify the location of the peak parameters .csv to simulate (if omitted, `peak_parameters.csv` is used).
Note: data is plotted normalized to Main peak but data is saved in raw format (i.e. the integrated area of each peak corresponds to the response value).

### Chromatography Fitter
To fit a set of series of data (stored as a two column csv, default at `chromatography_data.csv`, with time and response pairs),
update the `guess_parameters.csv` file with rough estimations for peak centres, standard deviations and responses (peak area).

Then run:\
`python chromatography_fitter.py --filename <filename> --guess_path <path> --data_path <path>`

where `<filename>` corresponds to the desired output of the data plotted with fit overlaid and simulated curves for
individual peaks and the determined peak centres, standard deviations, responses and tailing factors.
Additionally, `--guess_path <path>` and `--data_path <path>` can be used to specify the location of the guessed parameters and chromatography data to fit, respectively (if omitted `guess_parameters.csv` and `chromatography_data.csv` are used).


### Tailing Factor Analysis
To determine at which point the tailing factor has increased such that two adjacent peaks no longer possess a valley between them,
we can simulate the two curves under increasing tailing and calculate the valley height. To do so, update the `resolution_parameters.csv`
(or another filename specified by flag) with the two peaks centres, standard deviations and responses (peak area).

Then run:\
`python resolution_predictor.py --filename <filename> --parameters <path>`

where `<filename>` corresponds to the desired output of the plotted valley heights vs tailing function, as well as the raw data for that graph and individual curves.
Additionally, `--parameters <path>` can be used to specify the location of the peak parameters.