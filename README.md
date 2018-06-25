# minerctl frontend

In order to run this app you need `sqlite` and `virtualenv`.

For the initial setup execute `make install`. Then you need to edit the `config/initial.config` file according to the instructions in the file. If you do not have an appropriate key-pair (both in PEM format! ssh-keygen generates a different format by default) then just execute `./scripts/keygen.sh`.

Run the flask app with `sudo make` (yes as superuser...) as the app needs sufficient rights to be available on port 80 on the interface. This will obviously be adapted for deployment.
By default the webinterface is reachable via your IP address.
