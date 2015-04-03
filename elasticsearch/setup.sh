#!/bin/bash
function error()
{
    echo "-->error:$*"
    exit 1
}

work_dir=/cores

STEP=1
echo "STEP:$STEP download elasticsearch package..."
wget -c https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.5.0.noarch.rpm
echo "STEP:$STEP OK"

STEP=`expr $STEP + 1`
echo "STEP:$STEP extract elasticsearch package..."
sudo rpm -iv elasticsearch-1.5.0.noarch.rpm
sudo /sbin/chkconfig --add elasticsearch
sudo mkdir /cores/elasticsearch
sudo chown elasticsearch.elasticsearch /cores/elasticsearch
sudo sed -i 's/^#path.data: \/path\/to\/data$/path.data: \/cores\/elasticsearch/' /etc/elasticsearch/elasticsearch.yml 
sudo /etc/init.d/elasticsearch start
echo "STEP:$STEP OK"

STEP=`expr $STEP + 1`
echo "STEP:$STEP install elasticsearch python client package..."
sudo yum install python-pip.noarch
sudo pip install pbr
sudo pip install elasticsearch 
sudo pip install --upgrade urllib3
echo "STEP:$STEP OK"

