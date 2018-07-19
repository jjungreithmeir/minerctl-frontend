# minerctl frontend

In order to run this app you need `sqlite` and `virtualenv`.

For the initial setup execute `make install`. Then you need to edit the `config/initial.config` file according to the instructions in the file. If you do not have an appropriate key-pair (both in PEM format! ssh-keygen generates a different format by default) then just execute `./scripts/keygen.sh`.

Run the flask app with `sudo make` (yes as superuser...) as the app needs sufficient rights to be available on port 80 on the interface. This will obviously be adapted for deployment.
By default the webinterface is reachable via your IP address.

NOTE: If you are using this web interface in production you _might_ have noticed (yeah, you have noticed without a doubt) that the response times are abysmal (2-3 seconds for the root page). Theoretically, the frontend is very fast (as you may notice if you use the mocking controller in the backend) but the limitations of the cheap arduino are the real bottleneck in this situation. I've made a few notes in the backend README regarding optimization approaches and it would probably also be clever to improve the design of the data handling in the frontend to be more flexible and less blocking (injecting high latency responses with ajax, working with promises, ...).
