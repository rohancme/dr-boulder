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
python find_download_edg_epa.py <maximum number of files you want to download>
```
