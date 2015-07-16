Checkout-Python-Mini-Browser
===============

Installation Procedure

1) Install Apache2 in your system.

	Linux based machines: Run command apt-get install apache2

	Windows machines: Install a server such as XAMPP (https://www.apachefriends.org/index.html) and start the Apache server in XAMPP from the XAMPP control panel.


2)Enable mod_python for apache2 

	Linux based machines: https://www.howtoforge.com/embedding-python-in-apache2-with-mod_python-debian-etch

	Windows based machines: http://modpython.org/live/mod_python-2.7.8/doc-html/app-wininst.html


3) Copy the Checkout folder to apache cgi-bin directory

	Linux based machines: Folder location is /usr/lib/cgi-bin

	Windows based machines: Folder location is xampp/cgi-bin


4) Move img,js and CSS directories in repective folders

	Linux based machines: Folder location is /var/www

	Windows based machines: Folder location is xampp/htdocs


5) Copy your API credentials for LIVE/SandBox in paypal_config.ini file based on your choice without quotes.


6) Access url http://{ip-address}/cgi-bin/Checkout/index.py


7) Try to give all the permissions to the Checkout directory if you get any errors.
	(sudo chmod -R 755 Checkout/)
