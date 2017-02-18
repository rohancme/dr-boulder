from bs4 import BeautifulSoup
import requests
import os
import re
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
output_data_list = []

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

counter = 0

max_size = 2000000000
current_size = 0
total_size = 0

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
    output_data_list = output_data_list + [ip + data_path]

with open("edg_epa_file_list.txt", "w") as data_file:
    for data_path in output_data_list:
        data_file.write("%s\n" % data_path)

with open("edg_epa_ftp_file_list.txt", "w") as ftp_file:
    for data_path in ftp_list:
        ftp_file.write("%s\n" % data_path)

with open("edg_epa_skipped_file_list.txt", "w") as skip_file:
    for data_path in skip_list:
        skip_file.write("%s\n" % data_path)
