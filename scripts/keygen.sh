# original author: @ygotthilf
ssh-keygen -t rsa -b 4096 -f config/jwtRS256.key -N ""
openssl rsa -in config/jwtRS256.key -pubout -outform PEM -out config/jwtRS256.key.pub
