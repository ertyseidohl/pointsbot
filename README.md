# PointsBot

By [Erty](https://erty.me)

## Installation / Development

Download pointsbot using Git.

Run `python3 create_db.py` to create a new database file.

If you want, you can run `python3 create_db.py --drop` to optionally drop any existing database. (Don't run this in prod!)

You'll also need to create a file called `token` and put your Discord OAuth token in there as the only content ([instructions for getting this token](https://discordpy.readthedocs.io/en/stable/discord.html)).

You'll also need to `pip3 install discord` if it's not already installed.

## Running

Run the program with `python3 pointsbot.py`

## Daemon

Put the files in `/opt/pointsbot` (or update the following accordingly!).

`sys`

Write:

```
[Unit]
Description=Pointsbot
After=multi-user.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /opt/pointsbot/pointsbot.py

[Install]
WantedBy=multi-user.target
```

Then `sudo vim /etc/rsyslog.d/pointsbot.conf`

Write:

```
if $programname == 'pointsbot' then /var/log/pointsbot.log
& stop
```
Then `sudo touch /var/log/pointsbot.log`

Then `sudo chown syslog /var/log/pointsbot.log`

Then `sudo systemctl daemon-reload`

Then `sudo systemctl start pointsbot.service`

You can then see logs with `tail -f /var/log/pointsbot.log` (or... maybe not? Not sure where the logs are going).
