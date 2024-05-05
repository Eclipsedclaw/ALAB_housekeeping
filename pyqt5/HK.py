#!/usr/bin/env python3
# Author: Jiancheng Zeng(JC)
# Date: May 5th, 2024

from PyQt5.QtWidgets import QApplication
import ALABHK_layout
from PyQt5.QtCore import QTimer

# Required ALABHK_layout.py and ALABHK_query.py
# Suggest put those two files under the same directory
#
# Required database module lazyins by Keita Mizukoshi, install it by
# 
# python -m pip install lazyins
#
# To pip the data into the database, you will need to provide environment variables to access the sql server.
#
# echo 'export LAZYINS_HOST="$YOURHOST.COM"'>>~/.profile
# echo 'export LAZYINS_PORT=$YOURPORT'>>~/.profile
# echo 'export LAZYINS_USER="$YOURUSERNAME"'>>~/.profile
# echo 'export LAZYINS_PASSWD="$YOURPASSWORD"'>>~/.profile

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    gallery = ALABHK_layout.WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())