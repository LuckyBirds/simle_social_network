For centos 8 you need install this packages:\
dnf install  mysql  mysql-client mysql-server python3-pip mysql-libs python3-PyMySQL mysql-devel gcc python36-devel.x86_64\
\ 

After you need to install python requirements:  pip3 install -r req.txt\

Fist run program:\
export  FLASK_APP=main.py\
flask run -h 0.0.0.0

