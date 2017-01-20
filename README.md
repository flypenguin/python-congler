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
# service-info output, so filtering by tag, etc. is *NOT* possible right now.
```

Have fun!
