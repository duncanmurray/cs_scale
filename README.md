cs_scale
=========

A Rackspace Cloud Server provisioning application that is able to spin up a given number of servers from an image and add some metadata.


```
usage: cs_scale.py [-h] [-p SERVER_NAME_PREFIX] [-r REGION] -i SERVER_IMAGE_ID
                   [-s SERVER_RAM_SIZE] [-m METADATA_DICTIONARY]
                   [-c SERVER_COUNT] [-l LOG_DIRECTORY] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -p SERVER_NAME_PREFIX, --prefix SERVER_NAME_PREFIX
                        Server name prefix (defaults to 'node-' +
                        a random 8 charachter string
                        e.g. node-54jg84d9, node-57fhd49h, ...)
  -r REGION, --region REGION
                        Region where servers should be built (defaults to
                        'LON'
  -i SERVER_IMAGE_ID, --image SERVER_IMAGE_ID
                        Image ID to be used in server build There is no
                        default, ID must be supplied
  -s SERVER_RAM_SIZE, --size SERVER_RAM_SIZE
                        Server RAM size in megabytes (defaults to '512')
  -m METADATA_DICTIONARY, --meta METADATA_DICTIONARY
                        Metadata to be used in the build request(s) - (must be
                        in the format: {"key": "value", "key": "value", ...})
                        Maximum of 5 key/value pairs, default: {'MyGroup0_lsyncd': 'lsyncd_slave'}
  -c SERVER_COUNT, --count SERVER_COUNT
                        Number of servers to build (defaults to '1')
  -l LOG_DIRECTORY, --logpath LOG_DIRECTORY
                        The directory to create log files in
  -v, --verbose         Turn on debug verbosity
```

####PREREQUISITS

1. Rackspace Cloud server image created

####INSTALLATION

1. Download cs_scale.py
```
git clone https://github.com/duncanmurray/cs_scale.git \
&& cp cs_scale/cs_scale.py /usr/local/sbin/cs_scale.py
```

2. Download and install pyrax
```
pip install pyrax
```

####OPTIONS EXPLANATION

All options are optional except for -i, --image which must be supplied to build your servers from.

######-h, --help            
Show a help message

######-p <prefix>, --prefix <prefix>
Prefix to build servers with. The default is to use `node- + random 8 charachter string` e.g. node-54jg84d9, node-57fhd49h

######-r <region>, --region <region>
Region where servers should be built The default is `LON`.

######-i <image_id>, --image <image_id>
Image ID to be used in server build There is no default, ID must be supplied. For example `a3a2c42f-575f-4381-9c6d-fcd3b7d07d17`.

######-s <ram_size>, --size <ram_size>
RAM size to build servers with in megabytes. The default is `512`

######-m <dictionary>, --meta <dict>
Metadata to be used in the build request(s). This must be in the format: `{"key": "value", "key": "value", ...}` Maximum of 5 key/value pairs. The default is: `{'MyGroup0_lsyncd': 'lsyncd_slave'}`

######-c <integer>, --count <integer>
Number of servers to build. The default is '1')

######-l <log_directory>, --logpath <log_directory>
The directory to create log files in. The default is `/var/log`

######-v, --verbose         
Turn on `DEBUG` logging level. The default is `WARNING`
