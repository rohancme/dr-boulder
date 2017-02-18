import ftplib
import os
import argparse
from pyftpclient import PyFTPclient
import logging
import sys

skip_list = []


class FTP_file:
    def __init__(self, servername, path_to_file, remote_filename):
        self.servername = servername
        self.path_to_file = path_to_file
        self.remote_filename = remote_filename


def download_ftp_file(servername, path_to_file, remote_filename,
                      local_path, local_filename=None):
    print "Downloading: " + '/'.join([servername, path_to_file, remote_filename])
    if (local_filename is None):
        local_filename = remote_filename

    try:
        ftp_obj = PyFTPclient(servername)
        ftp_obj.DownloadFile('/'.join([path_to_file, remote_filename]),
                             os.path.join(local_path, path_to_file, local_filename))
        print "Success!"
    except Exception as e:
        print "Exception:" + str(e)


def get_FTP_file_from_url(ftp_url):
    if (not ftp_url.startswith("ftp://")):
        print str(ftp_url) + " is not a valid ftp link. Skipping"
        global skip_list
        skip_list = skip_list + [ftp_url]
        return None

    try:
        # Just in case there's a case I didn't handle
        url_without_protocol = ftp_url.replace("ftp://", "")
        servername_and_path = url_without_protocol.split("/", 1)
        if (len(servername_and_path) != 2):
            print "Cannot parse " + str(ftp_url) + " Skipping....."
            global skip_list
            skip_list = skip_list + [ftp_url]
            return None
        servername = servername_and_path[0]
        path_and_filename = servername_and_path[1].rsplit("/", 1)
        if (len(path_and_filename) != 2):
            print "Cannot parse " + str(ftp_url) + " Skipping....."
            global skip_list
            skip_list = skip_list + [ftp_url]
            return None
        remote_path = path_and_filename[0]
        remote_filename = path_and_filename[1]
        return FTP_file(servername, remote_path, remote_filename)
    except:
        print "Cannot parse " + str(ftp_url) + " Skipping....."
        global skip_list
        skip_list = skip_list + [ftp_url]
        return None


def get_list_from_file(filename):
    # get data into list
    with open(filename) as data_file:
        data_text = data_file.readlines()
    data_list = [x.strip() for x in data_text]
    return data_list


def convert_urls_to_objects(data_list):
    obj_list = [get_FTP_file_from_url(x) for x in data_list]
    return [x for x in obj_list if x is not None]

def handle_ftp_download(ftp_obj, local_path):
    server = ftp_obj.servername
    remote_path = ftp_obj.path_to_file
    remote_filename = ftp_obj.remote_filename
    download_ftp_file(servername=server, path_to_file=remote_path,
                      remote_filename=remote_filename,
                      local_path=local_path)


def download_all_files(data_list, download_folder):
    ftp_obj_list = convert_urls_to_objects(data_list)
    for obj in ftp_obj_list:
        print str(obj.servername)
        try:
            handle_ftp_download(obj, download_folder)
        except:
            skipped_url = 'ftp://' + '/'.join([obj.servername,
                                              obj.path_to_file,
                                              obj.remote_filename])
            print "Unexpected error. Skipping url"
            global skip_list
            skip_list = skip_list + [skipped_url]


def create_downloads_folder(folder_name="downloads"):
    base_path = os.path.dirname(os.path.realpath(__file__))
    downloads_path = os.path.join(base_path, folder_name)
    if (os.path.exists(downloads_path)):
        print downloads_path + " already exists..not creating folder"
    else:
        print "Creating folder: " + downloads_path
        os.makedirs(downloads_path)
    print "All downloaded data will be stored in:" + downloads_path


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Download ftp data listed in a file')
    parser.add_argument('--filename', metavar='F', type=str,
                        required=True,
                        help='The name of the file containing ftp links' +
                             '(one per line).Only valid ftp links!!')

    parser.add_argument('--downloads_folder', metavar='D', type=str,
                        default='downloads',
                        help='The name of the downloads folder')

    args = parser.parse_args()

    create_downloads_folder(folder_name=args.downloads_folder)
    data_list = get_list_from_file(args.filename)
    download_all_files(data_list=data_list,
                       download_folder=args.downloads_folder)
