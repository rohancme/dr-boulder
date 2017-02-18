"""Almost entirely from http://stackoverflow.com/a/1854932."""
import ftplib
import os
import time
import sys
import argparse
file_list = []


def traverse(ftp, path_so_far, depth=0):
    """
    Return a recursive listing of an ftp server contents.
    (startingfrom the current directory)

    listing is returned as a recursive dictionary, where each key
    contains a contents of the subdirectory or None if it corresponds
    to a file.

    @param ftp: ftplib.FTP object
    """
    if depth > 10:
        return ['depth > 10']
    retries = 5
    while (retries > 0):
        try:
            path_list = ftp.nlst()
            for entry in (path for path in path_list if path not in ('.', '..')):
                try:
                    ftp.cwd(entry)
                    path_so_far = '/'.join([path_so_far, entry])
                    traverse(ftp, path_so_far, depth + 1)
                    path_so_far = path_so_far.rsplit("/", 1)[0]
                    ftp.cwd('..')
                except ftplib.error_perm:
                    full_path = '/'.join([path_so_far, entry])
                    global file_list
                    file_list = file_list + [full_path]
                    print full_path
            break
        except:
            e = sys.exc_info()[0]
            print "Exception:" + str(e)
            print "Retrying in 3s.. Attempts left: " + str(retries)
            time.sleep(3)
            ftp.connect()
            ftp.login()
            ftp.set_pasv(True)
            ftp.cwd(path_so_far)
            retries = retries - 1


def main(server, output_file_name):
    ftp = ftplib.FTP(server)
    ftp.connect()
    ftp.login()
    ftp.set_pasv(True)
    traverse(ftp, "")
    ftp.quit()
    global file_list
    full_urls = ['ftp://' + str(server) + x for x in file_list]
    with open(output_file_name, "w") as data_file:
        for url in full_urls:
            data_file.write("%s\n" % url)
    print "List of FTP files stored in " + str(output_file_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get a list of all the available files on an ftp server')
    parser.add_argument('--server', metavar='S', type=str,
                        required=True,
                        help='The name of the file containing ftp links' +
                             '(one per line).Only valid ftp links!!')
    parser.add_argument('--output_file', metavar='F', type=str,
                        required=False, default="ftp_files.txt",
                        help='The name of the output file')
    args = parser.parse_args()
    servername = args.server
    if (servername.startswith("ftp://")):
        servername = servername.replace("ftp://", "")
    output_file = args.output_file
    main(servername, output_file)
