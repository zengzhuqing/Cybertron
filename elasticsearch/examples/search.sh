#!/bin/bash

####################################################################################
### Choose Redhat KB search or VM bugzilla search
####################################################################################

es_url='http://cybertron.eng.vmware.com:9200/redhat_kb/kb/_search?pretty=1'
#es_url='http://cybertron.eng.vmware.com:9200/bugzilla/text/_search?pretty=1'


####################################################################################
### To begin search, change the regexp after "text" as you want
####################################################################################

curl -XGET $es_url -d '
    {"query":
        {"regexp":
            { 
            "text":" *rip.*"
            }
        }
    }'
