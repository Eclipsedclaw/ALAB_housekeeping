# Aramaki Lab grafana scripts

## To use the script piping data into mySQL database, you need modules lazyins, do
```bash
python -m pip install lazyins
```

## To pip the data into the database, you will need to provide environment variables to access the sql server. 
Change **$YOURHOST.COM** to your host ip.
```bash
echo 'export LAZYINS_HOST="$YOURHOST.COM"'>>~/.profile
```
Change **$YOURPORT** to your port(usually 3306). 
```bash
echo 'export LAZYINS_PORT=$YOURPORT'>>~/.profile
```
Change **$YOURUSERNAME** to mysql username.
```bash
echo 'export LAZYINS_USER="$YOURUSERNAME"'>>~/.profile
```
Change **$YOURPASSWORD** to mysql password.
```bash
echo 'export LAZYINS_PASSWD="$YOURPASSWORD"'>>~/.profile
```

## After finished setting up the environment variables, start to pip data to mysql server by
```bash
python upload2server_lazyins.py
```

## Currently Aramaki Lab HK Grafana viewer running at: [http://jianchengjc.com:3000/d/f12ea01c-2b65-43c9-bd97-90bd0ddd0dfb/aramaki-lab-housekeeping?orgId=1&refresh=5s](http://jianchengjc.com:3000/d/f12ea01c-2b65-43c9-bd97-90bd0ddd0dfb/aramaki-lab-housekeeping?orgId=1&refresh=5s)
