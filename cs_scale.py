#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Adnan Smajlovic
# Modified by Duncan Murray 2013

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
from sys import exit
from time import sleep
import logging

import pyrax
from pyrax import exceptions as e
pyrax.set_setting("identity_type", "rackspace")

# Location of pyrax configuration file
CONFIG_FILE = "~/.rackspace_cloud_credentials"

# Metadata specifying key/value pair to create server with
METADATA = {"MyGroup0": "lsyncd"}

# Default number of servers to build
SERVER_COUNT = 1

# Set the default log file path
LOGPATH = "/var/log"

def main():
    """
    Build a number of Next-Gen Cloud Servers following a similar naming
    convention. (ie. web1, web2, web3) and returns the IP and login
    credentials for each server
    """
    # Variable to determine if build errors were encountered
    ERRORS = False

    # Compile a list of available RAM sizes for use in argument parsing
    # later on. The choices permitted will be made up of this list.
    #    NOTE: Should revisit to make more dynamic for if and when
    #          the list is updated
    FLAVOR_LIST = [512, 1024, 2048, 4096, 8192, 15360, 30720]

    # Define the script parameters (all are optional for the time being)
    parser = argparse.ArgumentParser(description=("Cloud Server provisioning "
                                                  "application"))
    parser.add_argument("-p", "--prefix", action="store", required=False,
                        metavar="SERVER_NAME_PREFIX", type=str,
                        help=("Server name prefix (defaults to 'node-' +"
                              " a random 8 charachter string"
                              "e.g. node-54jg84d9, node-57fhd49h, ...)"),
                        default="node-")
    parser.add_argument("-r", "--region", action="store", required=False,
                        metavar="REGION", type=str,
                        help=("Region where servers should be built (defaults"
                              " to 'LON'"), choices=["ORD", "DFW", "LON"],
                        default="LON")
    parser.add_argument("-i", "--image", action="store", required=True,
                        metavar="SERVER_IMAGE_ID", type=str,
                        help=("Image ID to be used in server build"
                             " There is no default, ID must be supplied"))
    parser.add_argument("-s", "--size", action="store", required=False,
                        metavar="SERVER_RAM_SIZE", type=int,
                        help=("Server RAM size in megabytes (defaults to "
                              "'512')"), choices=FLAVOR_LIST, default=512)
    parser.add_argument("-m", "--meta", action="store", required=False,
                        metavar="METADATA_DICTIONARY", type=str,
                        help=("Metadata to be used in the build request(s) - "
                              '(must be in the format: {"key": "value"'
                              ', "key": "value", ...}) Maximum of 5 '
                              "key/value pairs, default: %s" % (METADATA)),
                        default=METADATA)
    parser.add_argument("-c", "--count", action="store", required=False,
                        metavar="SERVER_COUNT", type=int,
                        help=("Number of servers to build (defaults to "
                              "'%d')" % (SERVER_COUNT)), choices=range(1,51),
                        default=SERVER_COUNT)
    parser.add_argument("-l", "--logpath", action="store", required=False,
                        metavar="DIRECTORY", type=str,
                        help=("The directory to create log files in"),
                        default=LOGPATH)
    parser.add_argument("-v", "--verbose", action="store_true", required=False,
                        help=("Turn on debug verbosity"),
                        default=False)

    # Parse arguments (validate user input)
    args = parser.parse_args()

    # Configure log formatting
    logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    rootLogger = logging.getLogger()
    # Check what level we should log with
    if args.verbose:
        rootLogger.setLevel(logging.DEBUG)
    else:
        rootLogger.setLevel(logging.WARNING)
    # Configure logging to console
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    # Configure logging to file
    try:
        fileHandler = logging.FileHandler("{0}/{1}.log".format(args.logpath, os.path.basename(__file__)))
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)
    except IOError:
        rootLogger.critical("Unable to write to log file directory '%s'" % (args.logpath))
        exit(1)

    # Define the authentication credentials file location and request that
    # pyrax makes use of it. If not found, let the client/user know about it.

    # Use a credential file in the following format:
    # [rackspace_cloud]
    # username = myusername
    # api_key = 01234567890abcdef
    # region = LON

    try:
        creds_file = os.path.expanduser(CONFIG_FILE)
        pyrax.set_credential_file(creds_file, args.region)
    except e.AuthenticationFailed:
        rootLogger.critical("Authentication failed. Please check and confirm"
               "that the API username, key, and region are in place "
               "and correct.")
        exit(2)
    except e.FileNotFound:
        rootLogger.critical("Credentials file '%s' not found" % (creds_file))
        exit(3)

    # Use a shorter Cloud Servers class reference string
    # This simplifies invocation later on (less typing)
    cs = pyrax.cloudservers

    # Locate the image to build from (confirm it exists)
    try:
        image = [i for i in cs.images.list() if args.image in i.id][0]
    except:
        rootLogger.critical("Image ID provided was not found. Please check "
               "and try again")
        exit(4)

    # Grab the flavor ID from the RAM amount selected by the user.
    # The server create request requires the ID rather than RAM amount.
    flavor = [f for f in cs.flavors.list() if args.size == f.ram][0]

    rootLogger.warning("Cloud Server build request initiated")

    # Print the image ID and name selected, as well as server count
    rootLogger.info("Image details, ID: '%s' Name: '%s'" % (image.id, image.name))
    rootLogger.info("Server build details, Size: '%d' MB Count: '%d'" % (args.size, args.count))

    # Server list definition to be used in tracking build status/comletion
    servers = []

    # Iterate through the server count specified, sending the build request
    # for each one in turn (concurrent builds)
    count = 1
    while count <= args.count:
        # Issue the server creation request
        srv = cs.servers.create(args.prefix + pyrax.utils.random_name(8, ascii_only=True), image.id,
                                flavor.id, meta=args.meta)
        # Add server ID from the create request to the tracking list
        servers.append(srv)
        count += 1

    # Check on the status of the server builds. Completed or error/unknown
    # states are removed from the list until nothing remains.
    while servers:
        # Track the element position for easier/efficient removal
        count = 0
        for server in servers:
            # Get the updated server details
            server.get()
            # Should it meet the necessary criteria, provide extended info
            # and remove from the list
            if server.status in ["ACTIVE", "ERROR", "UNKNOWN"]:
                rootLogger.info("Server details: Name: '%s' Status: '%s' Admin password: '%s'" % (server.name, server.status, server.adminPass))
                rootLogger.info("Networks: Public #1: '%s' Public #2: '%s' Private: %s" % (server.networks["public"][0], server.networks["public"][1], server.networks["private"][0]))
                if server.status not in ["ACTIVE"]:
                    ERRORS = True
                    rootLogger.warning("Something went wrong with the build request")
                del servers[count]
            count += 1
        # Reasonable wait period between checks
        sleep(15)

    # All done
    exit_msg = "Build requests completed"
    if ERRORS:
        rootLogger.warning("'%s' - with errors (see above for details)" % (exit_msg))
        exit(5)
    else:
        rootLogger.warning("%s" % (exit_msg))
        exit(0)


if __name__ == '__main__':
    main()

