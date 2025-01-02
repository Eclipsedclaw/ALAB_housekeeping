# Author: Jiancheng Zeng(JC)
# Date: Dec 8th, 2023

# Before run this script, please make sure you have setup the proper environmental variables
# echo 'export LAZYINS_HOST="$YOURHOST.COM"'>>~/.profile
# echo 'export LAZYINS_PORT=3306'>>~/.profile
# echo 'export LAZYINS_USER="$YOURUSERNAME"'>>~/.profile
# echo 'export LAZYINS_PASSWD="$YOURPASSWORD"'>>~/.profile

from time import sleep
import ALABSQL


if __name__ == '__main__':
    # For time separation of HK datataking
    sleep_sec = 1
    while True:
        ALABSQL.get_pressure()
        #ALABSQL.get_compressor()
        #ALABSQL.get_rtd()
        sleep(sleep_sec)


