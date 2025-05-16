# Kubernetes Environment Variable Printer
## Warning content under development

This is a sample configuration to test conjur kubernetes credential  integration using JWT authentication.

## Prerequisites

1) minikube
2) kubectl
3) jq -> This is just used to parse the json response, when kubectl returns json response
4) install helm using this URL https://helm.sh/docs/intro/install/


## Prepare environment

1. Build the Docker image:
   ```bash
   docker build -t env-printer:latest .

2. command to create a minikube server with project volume service token.
```
minikube start
```

3. get jwks details and issuer. These details will be using when doing conjur configurations.
      1. Build the Docker image:
      ```
      docker build -t env-printer:latest .
      ```
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

## Steps to follow in the conjur instance

1. follow the steps in the link. Replace public keys from jwks.json file and issuer from issuer.txt. https://docs.cyberark.com/conjur-cloud/latest/en/content/integrations/k8s-ocp/k8s-jwt-authn.htm?tocpath=Authenticate%20workloads%7CSecure%20Kubernetes%7C_____2#ConfiguretheJWTauthenticator

2. follow the steps in the below link.https://docs.cyberark.com/conjur-cloud/latest/en/content/integrations/k8s-ocp/cjr-k8s-jwt-sp-ic.htm?tocpath=Authenticate%20workloads%7CSecure%20Kubernetes%7CSet%20up%20applications%7CSecrets%20Provider%20for%20Kubernetes%7C_____1#SetupSecretsProviderasaninitcontainersidecar

3. execute the below command to login to conjur.
```
conjur login
```
4. Execute the below command.
```
conjur policy load -f conjur/1-con-workload.yml -b data
```
5. execute the below command.
```
conjur policy load -f conjur/2-con-app-access.yml -b conjur/authn-jwt/dev-cluster
```
6. execute the below command.
```
conjur policy load -f conjur/3-grant-access.yml -b data
```

## Steps to follow in kubernetes cluster


6. enable metrics-server and kubernetes dashboard. Optional but highly recommended to monitor the pods and get debug information.
```
minikube addons enable metrics-server
minikube dashboard
```
7. Helm install in kubernetes to prepare golden config map
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
8. prepare test app name space.
```
helm install namespace-prep cyberark/conjur-config-namespace-prep \
--create-namespace \
--namespace test-app-namespace \
--set conjurConfigMap.authnMethod="authn-jwt" \
--set authnK8s.goldenConfigMap="conjur-configmap" \
--set authnK8s.namespace="cyberark-conjur-jwt" \
--set authnRoleBinding.create="false"
```
9. Deploy kubernetes manifest for testing.
```
kubectl apply -f manifests/namespace.yaml
kubectl apply -f manifests/sample-secret.yaml
kubectl apply -f manifests/secret.yml 
kubectl apply -f manifests/service-account.yaml 
kubectl apply -f manifests/secret-access.yml
kubectl apply -f manifests/service.yml
```
10. Run deployment in kubernetes secret mode. (Currently it can update fresh secrets. But cannot update the secrets for some reason )
```
kubectl apply -f manifests/deployment-manifest.yml
```
11. Run deploument in push to file mode
```
kubectl apply -f manifests/deployment-file.yaml
```

