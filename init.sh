#!/bin/bash

source db.env

docker network create --gateway 172.24.0.1 --subnet 172.24.0.0/24 nextcloud

docker run --rm --network nextcloud --ip 172.24.0.100 --name nextcloud_docker_cluster_nc-db01_1 -d -it -p 3306:3306 -v /srv/docker/nextcloud_docker_cluster/db01-data:/var/lib/mysql --env-file db.env mariadb \
          --transaction-isolation=READ-COMMITTED \
          --binlog-format=ROW \
          --innodb-large-prefix=true \
          --innodb-file-per-table=1 \
          --wsrep-on=ON \
          --wsrep-provider=/usr/lib/galera/libgalera_smm.so \
          --wsrep-cluster-address="gcomm://172.24.0.100,172.24.0.101" \
          --default-storage-engine=InnoDB \
          --binlog-format=row \
          --innodb-autoinc-lock-mode=2 \
          --innodb-force-primary-key=1 \
          --innodb-doublewrite=1 \
          --wsrep-cluster-name=NextcloudCluster \
          --wsrep-node-name=nc-db01 \
          --wsrep-node-address="172.24.0.100" \
          --innodb-flush-log-at-trx-commit=0 \
          --wsrep-new-cluster

echo "waiting for cluster to initiate"
sleep 8

mysql -h localhost -p$MYSQL_ROOT_PASSWORD --protocol=TCP -e "show databases" > /dev/null

while [ $? != 0 ]; do
sleep 3
mysql -h localhost -p$MYSQL_ROOT_PASSWORD --protocol=TCP -e "show databases" > /dev/null
done

echo "importing tables"

mysql -h localhost -p$MYSQL_ROOT_PASSWORD --protocol=TCP nextcloud < templates/nextcloud.db
if [ $? == 0 ];then
	echo "import successful"
else
	echo "import failed"
fi

echo "start second sql instance"
docker run --rm --network nextcloud --ip 172.24.0.101 --name nextcloud_docker_cluster_nc-db02_1 -it -v /srv/docker/nextcloud_docker_cluster/db02-data:/var/lib/mysql --env-file db.env mariadb \
          --transaction-isolation=READ-COMMITTED \
          --binlog-format=ROW \
          --innodb-large-prefix=true \
          --innodb-file-per-table=1 \
          --wsrep-on=ON \
          --wsrep-provider=/usr/lib/galera/libgalera_smm.so \
          --wsrep-cluster-address="gcomm://172.24.0.100,172.24.0.101" \
          --default-storage-engine=InnoDB \
          --binlog-format=row \
          --innodb-autoinc-lock-mode=2 \
          --innodb-force-primary-key=1 \
          --innodb-doublewrite=1 \
          --wsrep-cluster-name=NextcloudCluster \
          --wsrep-node-name=nc-db02 \
          --wsrep-node-address="172.24.0.101" \
          --innodb-flush-log-at-trx-commit=0

echo "stop container"
sleep 10
docker stop nextcloud_docker_cluster_nc-db01_1

echo "set safe_to_bootstrap for db01"
sed -i 's/safe_to_bootstrap: 0/safe_to_bootstrap: 1/' ./db01-data/grastate.dat

echo "copy default config"
cp -R templates/config nextcloud-persistant/
chown -R www-data nextcloud-persistant/config
touch nextcloud-persistant/config/CAN_INSTALL

echo "You should now run"
echo "cp templates/systemd/nccluster.service /etc/systemd/systemd/"
echo "systemctl enable nccluster"
echo "systemctl start nccluster"
echo ""
echo "When the webservice is available via https run the postinst script."

