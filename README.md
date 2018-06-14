# minerctl frontend

In order to run the app `sqlite` and `virtualenv` have to be installed on the target machine.

For the initial setup execute `make install`. Then you need to edit the `config/initial.config` file according to the instructions in the file.

Run the flask app with `sudo make` (yes as superuser...) as the app needs sufficient rights to be available on port 80 on the interface. This will obviously be adapted for deployment.
By default the webinterface is reachable via your IP address.
