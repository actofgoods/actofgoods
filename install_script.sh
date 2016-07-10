
# ------------------------------------------------------------
# Setup Environment
# ------------------------------------------------------------
#!/bin/bash
message=test
echo "$message"
list = [postgresql python3 python3-pip redis-server]
echo "$list"
apt-get install $list