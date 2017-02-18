# dr-boulder
Script(s) for the data rescue -boulder event

## Assumptions
- ***Assumes you have virtualenv installed*** If not, follow the instructions [here](docs/PYTHON_WINDOWS.md)


### Quickstart

- Attempts to find all the download links available on https://edg.epa.gov/data/public and downloads them to the `downloads` folder in you current directory

- Navigate to the dr-boulder folder in terminal/iterm (mac/unix) or Command Line (Windows). Then:

```
virtualenv env
# On Mac/Unix systems
source env/bin/activate
# On Windows
.\env\Scripts\activate
pip install -r requirements.txt
# generate file list
python edg_epa_data_public/find_data_edg_epa.py
# download the files. Before the event - default max files downloaded is 5
python download_data_edg_epa.py --filename=edg_epa_data_public/edg_epa_file_list.txt
```