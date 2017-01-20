#!/usr/bin/env python

import consul

import urllib.parse
import sys
import re
import os
from pprint import pprint
from argparse import ArgumentParser


VERSION = "0.2.0"

args = None
consul_inst_cache = {}


def _get_consul_for_url(consul_url):
    if consul_url not in consul_inst_cache:
        parsed_url = urllib.parse.urlparse(consul_url)
        if ":" in parsed_url.netloc:  # port specified?
            items = parsed_url.netloc.split(":")  # extract and use
            host, port = (items[0], int(items[1]))
        else:
            host = parsed_url.netloc
            port = 8500
        # create consul instance and put in cache
        consul_inst_cache[consul_url] = \
            consul.Consul(host=host, port=port, scheme=parsed_url.scheme)
    return consul_inst_cache[consul_url]


def _get_consul_for_service(consul_url, consul_svc):
    pu = urllib.parse.urlparse(consul_url)
    consul_port = "" if ":" not in pu.netloc else ":" + pu.netloc.split(":")[1]
    tmp = "{}://{}{}".format(pu.scheme, consul_svc['Address'], consul_port)
    return _get_consul_for_url(tmp)


def _get_all_service_names():
    con = _get_consul_for_url(args.consul_url)
    return [key for key, value in con.catalog.services()[1].items()]


def _get_all_service_tags():
    con = _get_consul_for_url(args.consul_url)
    # gives us: { SVC_NAME: [SVC_TAG,...] }
    svcs = con.catalog.services()[1]
    tags = []
    for svc, svc_tags in svcs.items():
        tags += svc_tags
    return list(set(tags))


def _get_all_services() -> list:
    """
    Returns a list of consul service dicts
    :return: A list like [SVC1, ...]
    """
    # now, get the consul service dict for each service name.
    # catalog.service() returns (INDX, [NODE1, ...]), where NODEx is a dict
    con = _get_consul_for_url(args.consul_url)
    chk_svc_names = _get_all_service_names()
    chk_svcs = []
    for svc_name in chk_svc_names:
        chk_svcs += con.catalog.service(svc_name)[1]
    return chk_svcs


def _unregister(svc):
    """
    Deregisters a service from consul.
    :param service: The service dict of the service to be deregistered.
    :return: True on success, False on failure
    """
    con = _get_consul_for_service(args.consul_url, svc)
    res = con.agent.service.deregister(svc['ServiceID'])
    status = "OK" if res else "FAIL"
    print("DEREGISTER_{:<7} CONSUL {:<40}    ID {}"
          .format(status, con.http.base_uri, svc['ServiceID']))


def _get_filtered_services():
    def match(svc):
        for fname, fex in filter_dict.items():
            if fname not in svc or not fex.search(svc[fname]):
                return False
        return True
    filter_dict = {}
    for fltr in args.filter:
        field, expr = fltr.split("=", maxsplit=1)
        filter_dict[field] = re.compile(expr)
    svcs = _get_all_services()
    tmp = list(filter(match, svcs))
    return tmp


def del_by_id():
    svcs = _get_all_services()
    filtered = filter(lambda x: args.service_id == x['ServiceID'], svcs)
    for svc in filtered:
        _unregister(svc)


def del_by_name():
    svcs = _get_all_services()
    filtered = filter(lambda x: args.service_name == x['ServiceName'], svcs)
    for svc in filtered:
        _unregister(svc)


def del_by_tag():
    svcs = _get_all_services()
    filtered = filter(lambda x: args.tag_name in x['ServiceTags'], svcs)
    for svc in filtered:
        _unregister(svc)


def list_filtered():
    svcs = sorted(_get_filtered_services(), key=lambda x: x['ServiceName'])
    if args.verbose:
        pprint(svcs)
    else:
        for svc in svcs:
            print(svc['ServiceName'])


def del_filtered():
    svcs = sorted(_get_filtered_services(), key=lambda x: x['ServiceName'])
    for svc in svcs:
        _unregister(svc)


def list_services():
    svcs = _get_all_service_names()
    for svc in sorted(svcs):
        print(svc)


def list_tags():
    tags = _get_all_service_tags()
    for tag in sorted(tags):
        print(tag)


def service_info():
    svcs = _get_all_services()
    filtered = filter(lambda x: args.service_name == x['ServiceName'], svcs)
    pprint(list(filtered))


def version():
    print(VERSION)


def run(argv):
    global args
    parser = ArgumentParser()
    parser.add_argument("-c", "--consul-url",
                        default=os.environ.get("CONSUL_URL",
                                               "http://localhost:8500"),
                        help="Specify consul URL to use. "
                             "Default: http://localhost:8500 "
                             "or $CONSUL_URL if set")

    subs = parser.add_subparsers(dest='command')
    subs.required = True

    # no parameters, we don't need to assign them to variables
    subs.add_parser('list-services',
                    help="List all service names. Use 'list-filtered' to "
                         "get full service information.")
    subs.add_parser('list-tags',
                    help="List all tags used in all services.")

    # now we do.
    sub = subs.add_parser('service-info',
                          help="Print full information about a single service.")
    sub.add_argument("service_name",
                     help="Print detailed information about a service")

    sub = subs.add_parser('del-by-name',
                          help="Delete all services with a certain name. The "
                               "name mast match exactly.")
    sub.add_argument("service_name",
                     help="Name of the service to delete")

    sub = subs.add_parser('del-by-id',
                          help="Delete all services with a given ID. The ID "
                               "must match exactly.")
    sub.add_argument("service_id",
                     help="ID of the service to delete")

    sub = subs.add_parser('del-by-tag',
                          help="Delete all services which have a given tag. "
                               "The tag must match exactly.")
    sub.add_argument("tag_name",
                     help="Delete services with this tag")

    sub = subs.add_parser('list-filtered',
                          help="List services based on filter criteria. "
                               "Currently you cannot filter for nested fields "
                               "(e.g. ServiceTags, etc.).")
    sub.add_argument("-f", "--filter",
                     help="Add service filter (-f FIELD=VALUE). "
                          "VALUE can be a regex.",
                     action="append")
    sub.add_argument("-v", "--verbose",
                     help="Output all service details, not only service name",
                     action="store_true")

    sub = subs.add_parser('del-filtered',
                          help="Same as list-filtered, but deletes the "
                               "service. The same restrictions apply, and "
                               "del-filtered requires a filter list to "
                               "prevent accidently deleting all services.")
    sub.add_argument("-f", "--filter",
                     required=True,
                     help="Add service filter (-f FIELD=VALUE). "
                          "VALUE can be a regex.",
                     action="append")

    subs.add_parser('version',
                    help="Print version and exit")

    subs.add_parser('v',
                    help="Alias for version")

    args = parser.parse_args(argv)

    {
        "del-by-id": del_by_id,
        "del-by-name": del_by_name,
        "del-by-tag": del_by_tag,
        "del-filtered": del_filtered,
        "list-filtered": list_filtered,
        "list-services": list_services,
        "list-tags": list_tags,
        "service-info": service_info,
        "version": version,
        "v": version,
    }[args.command]()


def console_entrypoint():
    run(sys.argv[1:])

if __name__ == "__main__":
    run(sys.argv[1:])
