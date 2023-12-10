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
