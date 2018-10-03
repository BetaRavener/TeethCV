# TeethCV
Incisor Segmentation project. The implementation is using Active Shape Model approach to identify teeth in radiograph image. **More details in [report](https://github.com/BetaRavener/TeethCV/blob/master/report.pdf)**.

### How to run application
(Note: All filepaths are relative to this README file)

1. Start Anaconda environment configured from file `./cfg/condacv.env` in command prompt or shell. The file is just a configuration with dependencies, so the environment first needs to be created. This is done by calling `conda env create -f ./cfg/condacv.env`. Then, the new environment can be activated by calling `activate` script from anaconda package, i.e. `activate CondaCV`. The environment is activated and ready to use.
2. Navigate to this directory (`./`)
3. Run:
  1. `python main.py` command to run GUI.
  2. `python leaveoneout.py` command to perform leave one out cross validation.
