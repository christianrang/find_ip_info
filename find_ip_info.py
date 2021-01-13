import requests
import argparse
import pprint
from netaddr import IPNetwork
import sys 
import os
import time
"""
    Author:     Christian Rang
    Date:       05/20/20

    Script for finding information on an IP using the http://ip-api.com/ API
"""

# This can be hardcoded to contain list of ips instead of using a dynamic ingest
# ip_list = []

FILE_TYPES=('json','csv')

def get_ip_info(ip, url='http://ip-api.com/', file_type='csv'):
    """
    docs for ip-api.com can be found at https://ip-api.com/docs 
    :param      str ip:     target ip to get info for
    :param      str url:    target address being used to get info
    :return:                ip info / status code
    :raises:    http error
    """
    if not file_type in FILE_TYPES: raise ValueError("Please use one of the available file types: {}".format(FILE_TYPES))
    # Building the url
    fields = '33292287'     # Found at https://ip-api.com/docs/api:json under Returned data - fields it will generate a number for you
    url = url + file_type + '/' + ip + '?' + 'fields=' + fields

    # Allows for retrying of a query if an error is experienced
    while True:

        # Sending request
        response = requests.post(url)

        # Deciding how to handle response based on return code
        try:
            if response.status_code == requests.codes.ok:
                return response.text
            else:
                response.raise_for_status()
                return response.status_code
        except:
            wait(seconds=60)

def wait(seconds=60, verbose=True):
    """
    Waits for the api to become queryable again

    :param      int     seconds:    number of seconds to wait
    :param      bool    verbose:    defines will the user be notified of wait and remaining wait time
    """
    def outloud(remaining):
        sys.stdout.write("\r")
        sys.stdout.write("Sleeping for {:2d} seconds to give the API a break".format(remaining))
        sys.stdout.flush()

    def clean_sysout():
        """
        Cleans sys out before continuing
        """
        sys.stdout.write("\r")
        sys.stdout.write("                                                                               ")
        sys.stdout.write("\r")
        sys.stdout.flush()
    
    for remaining in range(seconds, 0, -1):
        if verbose==True: outloud(remaining)
        time.sleep(1)
        if verbose==True: clean_sysout()

def write(line, file_name):
    with open(file_name, 'a') as file:
        file.write(line)

def output_file_exist_check(file_name):
    overwrite_check = ''
    if os.path.isfile(file_name):
        while overwrite_check.lower() not in ['y', 'n']:
            overwrite_check = input('File "{}" already exists would you like to overwrite it? (y/n): '.format(file_name))
    else:
        return True
    if overwrite_check.lower() == 'y':
        open(file_name, "w")
        return True
    else:
        print('Exiting...')
        exit()

if __name__ == '__main__':
    # Builds arg parser
    parser = argparse.ArgumentParser(description='Find IP info')
    parser.add_argument('-f', '--file', nargs='+', type=str, dest='file', help='file(s) of target ip addresses to be ingested')
    parser.add_argument('-u', '--url',nargs=1, type=str, dest='url')
    parser.add_argument('-ip', type=str, nargs=1, dest='ip', help='target ip address')
    parser.add_argument('-i', '--ignore', dest='ignore', action='store_true', help='run the default ip list hardcoded in the script')
    parser.add_argument('-t', '--output_type', dest='file_type', help='output type of the query. Default=csv', default='csv')
    parser.add_argument('-o', '--output_file', dest='file_name', help='output file name. File type will be decided by -t/--output_type')
    args = parser.parse_args()

    # Stores parameters to be used in get_ip_info()
    get_ip_info_params = {}

    # Ensures a target IP and fills into the ip_list where necessary
    if args.file:
        ip_list=[]
        for file in args.file:
            with open(file) as file:
                lines = file.readlines()
                for line in lines:
                    ip_list.append(line)
    elif args.ip:
        ip_list = [args.ip[0]]
    elif args.ignore:
        pass
    else:
        raise TypeError('No target IP address. Please use {} -h for more info.'.format(parser.prog))

    if args.url:
        get_ip_info_params['url']= args.url[0]

    if args.file_name: output_file_exist_check(args.file_name)

    for ip in ip_list:
        if '/' in ip:
            ip_list.remove(ip)
            print('building ip list based off network... this may take a while...')
            # builds ip list based of CIDR
            for networked_ip in IPNetwork(ip):
                ip_list.append(str(networked_ip))
        # Ensures there are no newlines from when the file was imported
        if '\n' in ip:
            ip = ip.split('\n')[0]

        # adds the ip to the params replacing the current ip if necessary
        get_ip_info_params['ip']= ip
        if args.file_type: get_ip_info_params['file_type']= args.file_type

        output = get_ip_info(**get_ip_info_params)
        if args.file_name: write(output, args.file_name)

        # Prints output
        if args.file_type=='json':
            print(ip,':')
            pretty = pprint.PrettyPrinter(indent=2)
            pretty.pprint(output)

        if args.file_type=='csv':
            print(ip+','+get_ip_info(**get_ip_info_params).strip('\n'))
