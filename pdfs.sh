
if ps -ef | grep -v grep | grep pdfs.py; then
  exit 0
else
    cd /root/apiMEI/
  sudo /usr/bin/python3 pdfs.py
  exit 0
fi