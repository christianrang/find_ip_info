import requests
import argparse
import pprint
from netaddr import IPNetwork
"""
    Author:     Christian Rang
    Date:       05/20/20

    Script for finding information on an IP

    requirements.txt
        requests
        argparse
        pprint
        netaddr
"""

# This can be hardcoded to contain list of ips instead of using a dynamic ingest
# ip_list = []

def get_ip_info(ip, url='http://ip-api.com/json'):
    """
    docs for ip-api.com can be found at https://ip-api.com/docs 
    :param      str ip:     target ip to get info for
    :param      str url:    target address being used to get info
    :return:                ip info / status code
    :raises:    http error
    """
    # Building the url
    fields = '33292287'     # Found at https://ip-api.com/docs/api:json under Returned data - fields it will generate a number for you
    url = url + '/' + ip + '?' + 'fields=' + fields

    # Sending request
    response = requests.post(url)

    # Deciding how to handle response based on return code
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        response.raise_for_status()
        return response.status_code

if __name__ == '__main__':
    # Builds arg parser
    parser = argparse.ArgumentParser(description='Find IP info')
    parser.add_argument('-f', '--file', nargs='+', type=str, dest='file', help='file(s) of target ip addresses to be ingested')
    parser.add_argument('-u', '--url',nargs=1, type=str, dest='url')
    parser.add_argument('-ip', type=str, nargs=1, dest='ip', help='target ip address')
    parser.add_argument('-i', '--ignore', dest='ignore', action='store_true', help='run the default ip list hardcoded in the script')
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

        # Prints output
        print(ip,':')
        pretty = pprint.PrettyPrinter(indent=2)
        pretty.pprint(get_ip_info(**get_ip_info_params))
        print()
