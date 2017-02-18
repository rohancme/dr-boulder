import os
import requests
from clint.textui import progress
import argparse

valid_formats = ('.xml', '.pdf', '.json', '.zip', '.csv', '.png', '.geojson',
                 '.xlsx', '.kmz')

binary_formats = ('.zip', '.png', '.kmz', '.xlsx', '.pdf')


current_size = 0
total_size = 0

skip_list = []


def handle_download(url, local_path, filename, max_size):
    print "Attempting download of:" + url
    global skip_list
    try:
        req_stream = requests.get(url, stream=True, verify=False)
        req_stream.raise_for_status()
    except requests.exceptions.RequestException as e:
        print "Exception while trying to download: " + str(url)
        print "Exception: " + str(e)
        skip_list = skip_list + [url]
        print "Added to skip list"
        return 0

    # just a catch all to make sure the script doesn't exit for a case
    # I haven't thought of. That would be annoying with so many files!
    try:
        full_path = os.path.join(local_path, filename)
        open_mode = 'wb' if filename.endswith(binary_formats) else 'w'
        total_length = int(req_stream.headers.get('content-length'))
        print "About to download file to: " + str(full_path)
        print "FileSize(bytes): " + str(total_length)
        with open(full_path, open_mode) as f:
            if (current_size >= max_size):
                print "Downloading the next file will hit storage limit. Stopping"
                return
            for chunk in progress.bar(req_stream.iter_content(chunk_size=1024),
                                      expected_size=(total_length / 1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()
        return total_length
    except:
        print "Unexpected error trying to download url:" + str(url)
        print "Adding it to the skip list"
        skip_list = skip_list + [url]
        return 0


def get_data_list(filename):
    # get data into list
    with open(filename) as data_file:
        data_text = data_file.readlines()
    data_list = [x.strip() for x in data_text]
    return data_list


def download_all_files(data_links_filename,
                       downloads_path,
                       max_size):
    # get all the download links
    data_list = get_data_list(data_links_filename)
    current_size = 0

    while(len(data_list) > 0):
        data_path = data_list.pop(0)
        full_url_no_options = data_path.rsplit('?')[0]
        url_without_domain = full_url_no_options.replace("http://", "")
        url_without_domain = url_without_domain.replace("https://", "")
        url_without_domain = url_without_domain.split('/', 1)[1]
        path_and_filename = url_without_domain.rsplit('/', 1)
        data_dir = path_and_filename[0]
        filename = path_and_filename[1]
        full_data_dir = os.path.join(downloads_path, *data_dir.split('/'))
        if (os.path.exists(full_data_dir)):
            print full_data_dir + " already exists"
        else:
            print "Creating dir: " + full_data_dir
            os.makedirs(full_data_dir)
            print full_data_dir + " created"
        if (os.path.isfile(os.path.join(full_data_dir, filename))):
            print "File already exists. Skipping.."
            continue

        current_size = current_size + handle_download(data_path, full_data_dir,
                                                      filename, max_size)
        if (current_size >= max_size):
            break
    global skip_list
    # Add all the urls not downloaded for whatever reason to the skip list
    skip_list = skip_list + data_list


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
    default_max_size = 5000000000
    max_in_gb = default_max_size / 1000000000
    parser = argparse.ArgumentParser(description='Download data listed in a file')
    parser.add_argument('--filename', metavar='F', type=str,
                        required=True,
                        help='The name of the file containing links' +
                             '(one per line).Only direct download links!!')
    parser.add_argument('--max_space', metavar='M', type=float,
                        default=max_in_gb,
                        help='The maximum space you have available (In GB). Default: ' +
                        str(max_in_gb) + 'GB')
    parser.add_argument('--downloads_folder', metavar='D', type=str,
                        default='downloads',
                        help='The name of the downloads folder')

    args = parser.parse_args()

    max_size_in_bytes = args.max_space * 1000000000

    create_downloads_folder(folder_name=args.downloads_folder)
    download_all_files(data_links_filename=args.filename,
                       downloads_path=args.downloads_folder,
                       max_size=max_size_in_bytes)
    with open("skipped_files.txt", "a") as skip_file:
        for data_path in skip_list:
            skip_file.write("%s\n" % data_path)
