Add to Dockerfile

```
apt-get update
apt-get install postgresql postgresql-contrib
pip install click
```

Add to inherit env docker:

```
export TF_VAR_access_key="$AWS_ACCESS_KEY_ID"; export TF_VAR_secret_key="$AWS_SECRET_KEY"

```

Add to README

```
./terraform-aws-client-vpn-endpoint/scripts/gen_acm_cert.sh ./vpn_certs vpn.studioquixote.com
```
