
# ------------------------------------------------------------
# Setup Environment
# ------------------------------------------------------------
#!/bin/bash
message=test
echo "$message"
List = ["postgresql", "python3", "python3-pip", "redis-server"]
apt-get install $List