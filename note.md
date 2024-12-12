- System user for running gunicorn service (user and owner - gunicorn)
sudo adduser --system --group gunicorn
- gunicorn file to run service - service files are created in /etc/systemd/system/user
- working directory and its files now owned by gunicorn
sudo chown -R gunicorn:gunicorn /path/to/your/project

