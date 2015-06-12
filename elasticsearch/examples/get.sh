#!/bin/bash

####################################################################################
### Choose Redhat KB search or VM bugzilla search
####################################################################################

es_url='http://cybertron.eng.vmware.com:9200/bugzilla/text'

bugid=1
curl -XGET $es_url/$bugid?pretty=1
