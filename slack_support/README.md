# Introduction of pumping data to slack channels using slackbots
## To use this script
you can run
```bash
python3 main.py
````
under this directory. Right now there are couple of things that work with reading system variables. To take bash system as an example, you will need to put lines below to your .bashrc file. 

```bash
export LAZYINS_HOST="127.0.0.1"
export LAZYINS_PORT="3306"
export LAZYINS_USER="root"
export LAZYINS_PASSWD="$PASSWD"

export SLACK_TOKEN='$TOKEN'
export GRAFANA_URL="http://127.0.0.1:3000/d/adczl9p/pgrams-worldview-march-2026?orgId=1&from=now-6h&to=now&timezone=browser&refresh=auto"
export GRAFANA_USER="osaka_user"
export GRAFANA_PASSWD="pgrams"
```

Some explainations about the varibles above.
- LAZYINS_HOST: mysql database host name, if you are running this script locally to your mysql server then it can be the localhost 127.0.0.1
- LAZYINS_PORT: mysql database port, usually default 3306
- LAZYINS_USER: mysql database username
- LAZYINS_PASSWD: mysql database password
- SLACK_TOKEN: the slack token that you will need for the slack channel you want the bot to post on. [This link https://api.slack.com/apps/](https://api.slack.com/apps/) will give you the steps to move forward. You will need the token OAuth Scope listed below channels:read, chat:write, files:write, groups:read
- GRAFANA_URL: The grafana panel link that you want to share the screenshot
- GRAFANA_USER: the grafana username
- GRAFANA_PASSWD: the grafana password


Some other detailed hardcoded changes you have to be aware. you need to specify the database name and chart name, below is the turbo information
```bash
result = connector.query("SELECT * FROM WV_Mar_2026.Turbo_UPS ORDER BY time DESC LIMIT 1;")
```
pressure information
```bash
result = connector.query("SELECT * FROM WV_Mar_2026.pressure ORDER BY time DESC LIMIT 1;")
```
slack channel name
```bash
channel = "#worldview_slow_control"
```
refrashing time window for text and screenshots
```bash
duration_img = 60 * 60 * 2  # 2 hours
duration_txt = 60 * 60 * 2  # 2 hours
```
