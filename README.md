# Beekeeper Server

The beekeeper server is the administration server for the cyberinfrastructure.
All nodes must register with the beekeeper in order to be added to the ecosystem.

The beekeeper is responsible for the following:
1. front end for provisioning and administrative management of all nodes
2. certificate authority responsible for generating and validating all
communication keys used by the nodes (i.e. services running on them)
3. administrative portal for collecting the general health of all nodes


## start beekeeper

```bash
./create-keys.sh init --nopassword
./create-keys.sh cert untilforever forever
docker-compose up --build
```
Note: Options above like `--nopassword` and `forever` should not be used in production.

# Register a beehive with beekeeper (example)

1) The first step creates a beehive but credentials will be missing.
```bash
kubectl port-forward service/beekeeper-api 5000:5000  # if needed

curl localhost:5000/beehives -d '{"id": "my-beehive", "key-type": "rsa-sha2-256", "rmq-host":"host", "rmq-port": 5, "upload-host":"host", "upload-port": 6}'
```
Verify:
```bash
curl localhost:5000/beehives | jq .
```

2) Create beehive (not beekeeper) CA credentials: [https://github.com/waggle-sensor/waggle-pki-tools](https://github.com/waggle-sensor/waggle-pki-tools)

3) Add credentials for beehive to beekeeper
```bash
cd test-data/beehive_ca
curl -F "tls-key=@tls/cakey.pem" -F "tls-cert=@tls/cacert.pem"  -F "ssh-key=@ssh/ca" -F "ssh-pub=@ssh/ca.pub" -F "ssh-cert=@ssh/ca-cert.pub"  localhost:5000/beehives/my-beehive
```

Verify
```bash
curl localhost:5000/beehives/my-beehive | jq .
```
# assign node to a beehive

The next set of commands will only work once the node has registered.

VSN can be obtained from the node by:
```bash
curl localhost:5000/node/0000000000000001 -d '{"vsn": true}'
```
Getting the VSN can be done before or after the assignment of beehive or deploying the wes services.

The next commands will assign a beehive and deploy the WES services.
```bash
curl localhost:5000/node/0000000000000001 -d '{"assign_beehive": "my-beehive"}'
curl localhost:5000/node/0000000000000001 -d '{"deploy_wes": true}'
```

Check the logs:
```bash
docker logs beekeeper_bk-api_1
```

SSH to the node (via reverse ssh tunnel)
```bash
ssh -i ./beekeeper-keys/nodes-key/nodes.pem -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o IdentitiesOnly=true -o ProxyCommand="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@localhost -p 2201 -i ./beekeeper-keys/admin/admin.pem  netcat -U /home_dirs/node-0000000000000001/rtun.sock" root@foo
```


# Node registration example:


```bash
ssh -o UserKnownHostsFile=./known_hosts  sage_registration@localhost -p 20022 -i id_rsa_sage_registration register 0000000000000001
```


OR within bk-config container
```bash
ssh -o UserKnownHostsFile=./known_hosts  sage_registration@bk-sshd -p 22 -i registration_keys/id_rsa_sage_registration register 0000000000000001
```


`/etc/ssh/ssh_known_hosts` example:
```text
@cert-authority beehive.honeyhouse.one ssh-ed25519 AAAAC.....
```



# example: copy key files into vagrant

```bash
cp known_hosts register.pem register.pem-cert.pub ~/git/waggle-edge-stack/ansible/private/
```

ansible will copy these files if detected

# create Certs for node

Got to the directory that contains your `beekeeper-keys` folder. Copy `create-keys.sh`, then create the certificate file, for example:
```
cp ~/git/beekeeper/create-keys.sh .
./create-keys.sh cert until20220530 +20220530
```



## Unit Testing

Unit-testing is executed via
- `./unit-tests.sh`

Requires running docker-compose enviornment.

## Development

Access MySQL
```bash
docker exec -ti  beekeeper_db_1 mysql -u root -ptesttest -D Beekeeper
```
