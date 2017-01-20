# python-congler

CLI tool for searching and deleting consul services 


## Quickstart

Some examples:

```bash
$ pip install congler
[...]
$ congler -h

# use a different consul than http://localhost:8500, method 1
$ congler -c http://1.2.3.4:8500 list-services

# use a different consul than http://localhost:8500, method 2
$ export CONSUL_URL=http://1.2.3.4:8500
$ congler list-services

# list service names
$ congler list-services
consul

# list service names and filter by a regex search
# (".su" is used to perform a regex.search against each service name)
$ congler list-services .su
consul

# list service tags. filtering is also possible just as with list-services.
$ congler list-service-tags
mytag

# list full service info
$ congler service-info consul
[{'Address': '127.0.0.1',
  'CreateIndex': 4,
  'ModifyIndex': 5,
  'Node': 'eddie',
  'ServiceAddress': '',
  'ServiceEnableTagOverride': False,
  'ServiceID': 'consul',
  'ServiceName': 'consul',
  'ServicePort': 8300,
  'ServiceTags': [],
  'TaggedAddresses': {'lan': '127.0.0.1', 'wan': '127.0.0.1'}}]

# delete a service by name
$ congler del-by-name SERVICENAME
    
# delete a service with a certain tag
$ congler del-by-tag MYTAG
    
# list services matching a certain criteria
$ congler list-filtered -f "ServiceID=^myservice-.+"
# you can filter using all field names containing STRINGS you see in the 
# service-info output, and all top-level lists. In case of a list your regex
# will be applied against each element, and as soon as one matches the filter
# maches.
# NOTE: you will have multiple outputs per service name for each service, 
# because every service node will generate an output line. if you don't want
# this use list-services (which is much faster anyway).

# filter by tags:
$ congler list-filtered -f "ServiceTags=mytag"
```

Have fun!
