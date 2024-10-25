### Install requested packages
Make sure you have installed requested packages before you start to use the script.
```bash
pip install pymysql --break-system-packages
pip install lazyins --break-system-packages
```

### Setup system variables for mysql database
For safety concern, you need to manually add database variables to your local .bashrc files

Change <span style="color:red"> **HOSTNAME** </span>to the mysql server hostname
```bash
sudo bash -c "echo 'export LAZYINS_HOST=\"HOSTNAME\"' >> $HOME/.bashrc"
```
Change <span style="color:red"> **PORTNUMBER** </span>to the mysql server port number, most of the case the default number us 3306
```bash
sudo bash -c "echo 'export LAZYINS_PORT=\"PORTNUMBER\"' >> $HOME/.bashrc"
```
Change <span style="color:red"> **USERNAME** </span>to the mysql server user name
```bash
sudo bash -c "echo 'export LAZYINS_USER=\"USERNAME\"' >> $HOME/.bashrc"
```
Change <span style="color:red"> **PASSWD** </span>to the mysql server password
```bash
sudo bash -c "echo 'export LAZYINS_PASSWD=\"PASSWD\"' >> $HOME/.bashrc"
```
