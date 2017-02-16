from bs4 import BeautifulSoup
import requests
import os
import re
from clint.textui import progress
import sys

ip = 'http://134.67.99.116'
path = '/data/public'

textData = requests.get(ip + path, verify=False).text

soup = BeautifulSoup(textData, 'html.parser')

data_list = []
ftp_list = []
skip_list = []
crawl_list = []
crawled = []

counter = 0

valid_formats = ('.xml', '.pdf', '.json', '.zip', '.csv', '.png', '.geojson',
                 '.xlsx', '.kmz')

binary_formats = ('.zip', '.png', '.kmz', '.xlsx', '.pdf')


def get_all_web_links(soup):
    global crawl_list
    global crawled
    global data_list
    for link in soup.find_all('span'):
        url = link.get('href')
        if(url is not None):
            full_path = ip + url
            if (full_path not in crawl_list and full_path not in crawled):
                crawl_list = crawl_list + [full_path]
                crawled = crawled + [full_path]
    for link in soup.find_all('a'):
        data_src = link.get('href')
        if (data_src is not None):
            if (data_src.endswith(valid_formats)):
                if(data_src not in data_list):
                    data_list = data_list + [data_src]


get_all_web_links(soup)

print "Recursively building URL and file list. This might take a while...."

while (len(crawl_list) != 0):
    url = crawl_list.pop(0)
    htmlText = requests.get(url, verify=False).text
    soup = BeautifulSoup(htmlText, 'html.parser')
    counter = counter + 1
    if (counter % 10 == 0):
        print "Length of url list:" + str(len(crawl_list))
        print "Length of file list:" + str(len(data_list)) + "\n"
    get_all_web_links(soup)

base_path = os.path.dirname(os.path.realpath(__file__))
downloads_path = os.path.join(base_path, 'downloads')
if (os.path.exists(downloads_path)):
    print downloads_path + " already exists..not creating folder"
else:
    print "Creating folder: " + downloads_path
    os.makedirs(downloads_path)
print "All downloaded data will be stored in:" + downloads_path

counter = 0


def handle_download(url, local_path, filename):
    print "Attempting download of:" + url
    try:
        req_stream = requests.get(url, stream=True, verify=False)
        req_stream.raise_for_status()
    except requests.exceptions.RequestException as e:
        print "Exception while trying to download: " + url
        print "Exception: " + str(e)
        global skip_list
        skip_list = skip_list + [url]
        print "Added to skip list"
        return
    full_path = os.path.join(local_path, filename)
    open_mode = 'wb' if filename.endswith(binary_formats) else 'w'
    with open(full_path, open_mode) as f:
        total_length = int(req_stream.headers.get('content-length'))
        for chunk in progress.bar(req_stream.iter_content(chunk_size=1024),
                                  expected_size=(total_length / 1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()

# default to a max of 5 downloaded files
max_downloaded_files = int(sys.argv[1]) if (len(sys.argv) > 1) else 5

for data_path in data_list:
    if (data_path.startswith('ftp:')):
        print "Found an ftp link. Skipping..."
        if (data_path not in ftp_list):
            ftp_list = ftp_list + [data_path]
        continue
    if (re.match("^(http|https)://", data_path)):
        # This is probably an external link. Let's skip for now and log it
        print "Skipping possible external link:" + data_path
        if (data_path not in skip_list):
            skip_list = skip_list + [data_path]
        continue
    url_and_filename = data_path.rsplit('/', 1)
    data_dir = url_and_filename[0]
    filename = url_and_filename[1]
    full_data_dir = os.path.join(downloads_path, *data_dir.split('/'))
    if (os.path.exists(full_data_dir)):
        print full_data_dir + "already exists"
    else:
        print "Creating dir: " + full_data_dir
        os.makedirs(full_data_dir)
        print full_data_dir + " created"

    handle_download(ip + data_path, full_data_dir, filename)
    counter = counter + 1
    if (counter == max_downloaded_files):
        break
