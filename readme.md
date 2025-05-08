# Kubernetes Environment Variable Printer

This is a sample Kubernetes application that prints all environment variables.

## Steps to Deploy

1. Build the Docker image:
   ```bash
   docker build -t env-printer:latest .

2. command to create a minikube server with project volume service token.
```
minikube start --driver=parallels
```

3. get jwks details and issuer
```
kubectl get --raw /openid/v1/jwks > jwks.json
kubectl get --raw /.well-known/openid-configuration | jq -r '.issuer'
```

4. get conjur url certificate. openssl is required
```
openssl s_client -connect india.cyberark.cloud:443 -showcerts </dev/null 2> /dev/null | awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/ {print $0}' > "conjur.pem"
```
5. Helm install in kubernetes to prepare golden config map
```
helm install "cluster-prep" cyberark/conjur-config-cluster-prep  -n "cyberark-conjur-jwt" \
      --create-namespace \
      --set conjur.account="conjur" \
      --set conjur.applianceUrl="https://india.secretsmgr.cyberark.cloud/api" \
      --set conjur.certificateBase64=$(cat conjur.pem | base64) \
      --set authnK8s.authenticatorID="dev-cluster" \
      --set authnK8s.clusterRole.create=false \
      --set authnK8s.serviceAccount.create=false
``` 
6. prepare test app name space.
```
helm install namespace-prep cyberark/conjur-config-namespace-prep \
--create-namespace \
--namespace test-app-namespace \
--set conjurConfigMap.authnMethod="authn-jwt" \
--set authnK8s.goldenConfigMap="conjur-configmap" \
--set authnK8s.namespace="cyberark-conjur-jwt" \
--set authnRoleBinding.create="false"
```


