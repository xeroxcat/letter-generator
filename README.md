# Very basic framework for writing templated letters
## features
* define fields (optionally a list of values) to be filled in
* enable or disable lines in the template
* run the generator to interactively define a letter instance

## requirements
* python3
* pythondialog [[https://pypi.org/project/pythondialog/]]
* dialog commandline utility [[https://invisible-island.net/dialog/]] 

## platforms 
- Tested on debian 10 (buster), Python 3.7.3, pythondialog 3.5.1, dialog 1.3-20190211
- I can look into windows support if there is demand. Dialog uses ncurses which has poor windows support. Might work with this program as a dialog backend: [[http://andrear.altervista.org/home/cdialog.php]]

## documentation
included examples of `letter_fields.json` and `letter_template.txt` give a basic explanation of different functions
