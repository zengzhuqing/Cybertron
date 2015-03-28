# Install MySQL server
sudo yum install mysql-server -y
# Start the service
sudo /sbin/service mysqld start
# Start when boot
sudo chkconfig mysqld on
# Set root password  
sudo /usr/bin/mysql_secure_installation
# Install phpMyAdmin
sudo yum -y install phpmyadmin
# I have take really long time to configure phpmyadmin, strange problems
# Only when I remove /usr/share/phpMyAdmin dir, remove it, then reinstall it, then success
# Configure Require IP in /etc/httpd/conf.d/phpMyAdmin.conf
vim /etc/httpd/conf.d/phpMyAdmin.conf
# restart httpd service
service httpd restart
