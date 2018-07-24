# minerctl frontend

In order to run this app you need `sqlite`, `virtualenv`, `make`, `python3-pip` and `python3` (this was tested on Python 3.6.6). It is also recommended to run this application inside a virtual environment (with a virtualenv folder called `env`).

For the initial setup execute `make install`. Then you need to edit the `config/minerctl.ini` file according to the instructions in the file. If you do not have an appropriate key-pair (both in PEM format! ssh-keygen generates a different format by default) then just execute `./scripts/keygen.sh`.

Run the flask app with `make` 
By default the webinterface is reachable via your IP address on port 8080. If you want to use the file upload you need to configure uwsgi appropriately.

NOTE: If you are using this web interface in production you _might_ have noticed (yeah, you have noticed without a doubt) that the response times are abysmal (2-3 seconds for the root page). Theoretically, the frontend is very fast (as you may notice if you use the mocking controller in the backend) but the limitations of the cheap arduino are the real bottleneck in this situation. I've made a few notes in the backend README regarding optimization approaches and it would probably also be clever to improve the design of the data handling in the frontend to be more flexible and less blocking (injecting high latency responses with ajax, working with promises, ...).

## Legal

I've received explicit permission to release the source code of this project on my personal GitHub repository under my employer's copyright.
