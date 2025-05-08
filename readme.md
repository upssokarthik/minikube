# Kubernetes Environment Variable Printer
## Warning content under development

This is a sample configuration to test conjur kubernetes credential  integration using JWT authentication.

## Prerequisites

1) minikube
2) kubectl
3) jq -> This is just used to parse the json response, when kubectl returns json response

## Steps to Deploy

1. Build the Docker image:
   ```bash
   docker build -t env-printer:latest .

2. command to create a minikube server with project volume service token.
```
minikube start
```

3. get jwks details and issuer
```
kubectl get --raw /openid/v1/jwks > jwks.json
kubectl get --raw /.well-known/openid-configuration | jq -r '.issuer' > issuer.txt
```

4. get conjur url certificate. openssl is required
```
openssl s_client -connect india.cyberark.cloud:443 -showcerts </dev/null 2> /dev/null | awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/ {print $0}' > "conjur.pem"
```
5. enable metrics-server and kubernetes dashboard. Optional but highly recommended to monitor the pods and get debug information.
```
minikube addons metrics-server
minikube dashboard
```
6. Helm install in kubernetes to prepare golden config map
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
7. prepare test app name space.
```
helm install namespace-prep cyberark/conjur-config-namespace-prep \
--create-namespace \
--namespace test-app-namespace \
--set conjurConfigMap.authnMethod="authn-jwt" \
--set authnK8s.goldenConfigMap="conjur-configmap" \
--set authnK8s.namespace="cyberark-conjur-jwt" \
--set authnRoleBinding.create="false"
```
8. Deploy kubernetes manifest for testing.
```
kubectl apply -f manifests/namespace.yaml
kubectl apply -f manifests/sample-secret.yaml
kubectl apply -f manifests/secret.yml 
kubectl apply -f manifests/service-account.yaml 
kubectl apply -f manifests/secret-access.yml
kubectl apply -f manifests/service.yml
kubectl apply -f manifests/deployment-manifest.yml
```

