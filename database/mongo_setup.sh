# Install MongoDB server
sudo yum install python-pymongo.x86_64 mongodb.x86_64 mongodb-server.x86_64 -y
# Start the service
sudo /sbin/service mongod start
# Start when boot
sudo chkconfig mongod on
