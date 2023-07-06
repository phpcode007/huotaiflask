#!/bin/bash

killall -9 gunicorn

#export FLASK_APP=main
#
#export FLASK_ENV=development
## 2.3版本会有下面的报警
##'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
#export FLASK_DEBUG=true
##flask run --host=0.0.0.0
#flask run

#3个CPU的最大工作数是(2x3)+1=7。工人*线程不应该超过这个数字。

#将日志重写向,方便收集
gunicorn -D --workers=2 --threads=2 -b 0.0.0.0:5000 --log-level info --error-logfile e.log --reload --capture-output main:app