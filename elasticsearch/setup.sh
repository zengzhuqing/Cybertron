#!/bin/bash
function error()
{
    echo "-->error:$*"
    exit 1
}

a()
{
STEP=1
echo "STEP:$STEP download elasticsearch package..."
curl -L -O http://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.20.5.tar.gz
echo "STEP:$STEP OK"

STEP=`expr $STEP + 1`
echo "STEP:$STEP extract elasticsearch package..."
tar xmf *.tar.gz || error "tar error"
mv elasticsearch-0.20.5 elasticsearch
echo "STEP:$STEP OK"
}

STEP=`expr $STEP + 1`
echo "STEP:$STEP download elasticsearch python client..."
curl -L -O https://pypi.python.org/packages/source/e/elasticsearch/elasticsearch-1.4.0.tar.gz
echo "STEP:$STEP OK"
