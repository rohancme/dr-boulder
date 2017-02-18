# dr-boulder
Script(s) for the data rescue -boulder event

### Quickstart
- Assumes you have virtualenv
- Attempts to find all the download links available on https://edg.epa.gov/data/public and downloads them to the `downloads` folder in you current directory
- Run the following commands
```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
# generate file list
python edg_epa_data_public/find_data_edg_epa.py
# download the files. Before the event - default max files downloaded is 5
python download_data_edg_epa.py --filename=edg_epa_data_public/edg_epa_file_list.txt
```
