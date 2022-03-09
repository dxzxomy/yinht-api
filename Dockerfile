# Dockerfile
# Project: kscrcdn_api
# Author: guangzhen.ming
# Email: mingguangzhen@kingsoft.com
# docker build --no-cache -t kscrcdn_api:latest .
# docker run -p 6660:6660 -v /home/mingguangzhen/kscrcdn_api/log:/kscrcdn_api/log -d --rm --name kscrcdn_api kscrcdn_api:latest

FROM python:3.8-buster
LABEL maintainer="mingguangzhen@kingsoft.com"
COPY . $WORKDIR/kscrcdn_api/
WORKDIR /kscrcdn_api
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo 'Asia/Shanghai' >/etc/timezone && \
    pip install -i https://mirrors.aliyun.com/pypi/simple/ -r $WORKDIR/kscrcdn_api/requirements.txt
CMD [ "/usr/local/bin/gunicorn", "-c", "kscrcdn_api/config/webconfig.py", "kscrcdn_api.wsgi:app" ]
