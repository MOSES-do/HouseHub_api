- System user for running gunicorn service (user and owner - gunicorn)
sudo adduser --system --group gunicorn
- gunicorn file to run service - service files are created in /etc/systemd/system/user
- working directory and its files now owned by gunicorn
sudo chown -R gunicorn:gunicorn /path/to/your/project



--GUNICORN SETUP--
[Unit]
Description=Gunicorn instance to serve HouseHUB API
After=network.target

[Service]
User=ubuntu
EnvironmentFile=/etc/myfiles/docs.env
WorkingDirectory=/home/ubuntu/HouseHub_api
ExecStart=/home/ubuntu/HouseHub_api/HouseHub_api/bin/gunicorn -w 3 -b 0.0.0.0:5000 api.v1.run:app

[Install]
WantedBy=multi-user.target
