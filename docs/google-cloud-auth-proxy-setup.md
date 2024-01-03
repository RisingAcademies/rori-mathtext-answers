# Google Cloud Auth Proxy Setup

Google Cloud SQL allows for external connections to the database.  One way to connect via the database is through the Cloud Terminal, which is good for direct manipulation of the database.  For applications in a local environment, though, it is possible to connect directly from the application to Cloud SQL using the correct settings ([link](https://parth-vijay.medium.com/configure-postgresql-database-of-django-app-in-cloud-sql-f56ceec0fb66)).  However, this direct connection relies on whitelisting the IP address in the Cloud SQL instance.  This may be useful for local development, but it is not suitable for production (and can be cumbersome for local development).

Cloud SQL Auth Proxy handles connection to a Cloud SQL instance from the database.  It can make development from a local environment simplier.  The process below covers how to set up Cloud SQL Auth Proxy for local development.

Note: This guide assumed you have already activated Cloud SQL Admin API for your project.


1. Download the Google Cloud Auth Proxy file. (see [Download the CloudSQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy#install) in docs for current version)
```bash
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.1/cloud-sql-proxy.linux.amd64
```

2. Enable the `cloud-sql-proxy` file to be executable.
```bash
chmod +x cloud-sql-proxy
```

3. In Google Cloud's console, create service account for Cloud SQL with `Cloud SQL Instance User` and `Cloud SQL Client`.

Download the JSON key file for the service account.

4. Install Google Cloud CLI ([link](https://cloud.google.com/sdk/docs/install)).

5. Activate the service account through Cloud SQL Auth Proxy.  This will make it so that all gcloud-related services use the key file to log in.
```bash
gcloud auth activate-service-account --key-file="/path/to/key/file.json"
```

6. Start Cloud SQL Auth Proxy.  You may choose any available port number.
```bash
../cloud-sql-proxy --address 0.0.0.0 --port 3000 --auto-iam-authn rori-turn:us-central1:user-model-development-db
```

You should see something like this upon successful activation.
```bash
2023/12/14 19:53:27 Authorizing with Application Default Credentials
2023/12/14 19:53:27 [CLOUD-SQL-INSTANCE] Listening on [::]:3000
2023/12/14 19:53:27 The proxy has started successfully and is ready for new connections!
```

7. In the Django application, you need to match the port that you started Cloud SQL Auth Proxy with.  Also, you need to write the full instance name.

`GOOGLE_CLOUD_SQL_NAME` refers to the specific database within the Cloud SQL instance you are connecting to.

`GOOGLE_CLOUD_SQL_USER`, and `GOOGLE_CLOUD_SQL_PASSWORD` refer to a database user that in the instance of Cloud SQL you are working with.  For the SQL password, it could be useful to store the value in Secrets Manager.

`GOOGLE_CLOUD_SQL_HOST` and `GOOGLE_CLOUD_SQL_PORT` both describe the running Google Cloud SQL Auth Proxy connection you started earlier.

```python
DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.postgresql",
		"NAME": GOOGLE_CLOUD_SQL_NAME, # DB name
		"USER": GOOGLE_CLOUD_SQL_USER, # DB user name
		"PASSWORD": GOOGLE_CLOUD_SQL_PASSWORD, # Password for DB user
		"HOST": GOOGLE_CLOUD_SQL_HOST, # 127.0.0.1 (localhost)
		"PORT": GOOGLE_CLOUD_SQL_PORT, # Port of Cloud SQL Auth Proxy
	},
}
```

## Resources
- [Configure Django Application in Cloud SQL with PostgreSQL](https://parth-vijay.medium.com/configure-postgresql-database-of-django-app-in-cloud-sql-f56ceec0fb66)
- [Connect using Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy)
