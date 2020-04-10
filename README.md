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
To simulate the chromatography results, update the `peak_parameters.csv` file (or change the filename in `settings.py`)
 to reflect the details of the experiment you wish to simulate.\
It is important to note that the label names for the peaks do not matter, except their must be a "Main" peak as the peaks are normalised to this.
Here, `t` represents the peak centre (with no tailing), `w` is the width, `s` is the standard deviation, `response` is the peak height and the `tailing factor` is the desired asymmetry calculated at 5% max height.

To run the simulation simply use:\
`python chromatography_simulator.py --filename <filename>`\
where `<filename>` is the desired name of the simulated graph and raw data, which are saved to the output directory.