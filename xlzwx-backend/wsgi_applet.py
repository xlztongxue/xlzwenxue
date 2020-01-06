'''
    本文件用于wsgi启动
'''
import sys
from configparser import ConfigParser
from applet_app import create_applet_app

cf = ConfigParser()
uwsgi_ini = "conf/uwsgi_applet.ini"
cf.read(uwsgi_ini)
svrtype = cf.get("xx_server", "type")
if svrtype == "dev":
    # print("run with DebugAppletConfig")
    app = create_applet_app("config.DebugAppletConfig")
else:
    # print("run with AppletConfig")
    app = create_applet_app('config.AppletConfig')

if __name__ == '__main__':
    app.run()

