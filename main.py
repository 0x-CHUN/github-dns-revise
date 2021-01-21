import requests
import re
import time
import datetime
from lxml import etree
import pickle
import argparse

urls = ["github.com",
        "user-images.githubusercontent.com",
        "camo.githubusercontent.com",
        "github.githubassets.com",
        "camo.githubusercontent.com",
        "github.map.fastly.net",
        "github.global.ssl.fastly.net",
        "api.github.com",
        "raw.githubusercontent.com",
        "favicons.githubusercontent.com",
        "avatars8.githubusercontent.com",
        "avatars7.githubusercontent.com",
        "avatars6.githubusercontent.com",
        "avatars5.githubusercontent.com",
        "avatars4.githubusercontent.com",
        "avatars3.githubusercontent.com",
        "avatars2.githubusercontent.com",
        "avatars1.githubusercontent.com",
        "avatars0.githubusercontent.com"]


IPADDRESS_PREFIX = ".ipaddress.com"


def getInfo(rawurl):
    url = makeurl(rawurl)
    r = requests.get(url)
    time.sleep(1)
    if r.status_code == 200:
        print("Successfully get the : {}".format(url))
        dnsinfo = getDnsInfo(r.content)
        print("DNS INFO : {}\n".format(dnsinfo))
        return dnsinfo
    else:
        print("Failed to get the : {}".format(url))


def makeurl(rawurl):
    dotnum = rawurl.count('.')
    if dotnum > 1:
        url_list = rawurl.split('.')
        return "https://"+url_list[-2]+"."+url_list[-1]+IPADDRESS_PREFIX+"/"+rawurl
    else:
        return "https://"+rawurl+IPADDRESS_PREFIX


def getDnsInfo(content):
    html = etree.HTML(content)
    dnsinfo = str(etree.tostring(html.xpath("//*[@id='dnsinfo']")[0]))
    result = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", dnsinfo)
    return list(set(result))


def run(host_file):
    timedelta = datetime.timedelta(days=7)
    host_info = {}
    try:
        with open("dnsInfo.txt", 'rb') as f:
            old_host_dict = pickle.load(f)
            print("DNS INFO EXITS.")
            if (datetime.datetime.now() - old_host_dict['time']) < timedelta:
                print("No need to update data.\n")
                host_info = old_host_dict
            else:
                print("Updating.....\n")
                with open("dnsInfo.txt", 'wb') as fw:
                    new_host_dict = {}
                    for url in urls:
                        dnsInfo = getInfo(url)
                        new_host_dict[url] = dnsInfo
                    new_host_dict['time'] = datetime.datetime.now()
                    pickle.dump(new_host_dict, fw)
                host_info = new_host_dict
    except FileNotFoundError:
        print("DNS INFO NOT EXITS.\nCREATING.....\n")
        with open("dnsInfo.txt", 'wb') as f:
            new_host_dict = {}
            for url in urls:
                dnsInfo = getInfo(url)
                new_host_dict[url] = dnsInfo
            new_host_dict['time'] = datetime.datetime.now()
            pickle.dump(new_host_dict, f)
        host_info = new_host_dict
    with open(host_file, 'wb') as f:
        create_time = "# Github Host Start| time:{}\n".format(
            host_info['time']).encode('utf-8')
        f.write(create_time)
        for key in host_info.keys():
            if key != 'time':
                for val in host_info[key]:
                    info = "{} {}\n".format(val, key).encode('utf-8')
                    f.write(info)
        f.write(b'#Github Host End\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Github dns revise')
    parser.add_argument(
        '--f', type=str, default="C:/Windows/System32/drivers/etc/hosts")
    args = parser.parse_args()
    print("Updating : {}".format(args.f))
    run(host_file=args.f)