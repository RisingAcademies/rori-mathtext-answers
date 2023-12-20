# Google Cloud SQL - Cloud Run Connection Setup

Applications can connect to Google Cloud SQL through Google Cloud Run.  This enables them to access the cloud database.  This guide covers the basics of what's necessary to connect to Cloud SQL from Cloud Run.  There may be better ways of doing or automating these steps.  This guide assumes that you have running Cloud SQL and Cloud Run instances.  It also assumes that the ORM you are using for your Python application is Django.

Note: This guide assumed you have already activated Cloud SQL Admin API for your project.

## Google Cloud SQL
1. In the Overview tab, look up the "Connection name".  This is what you will use to connect from your application to CloudSQL.

2. To connect to the database, you will need to have a user.  You could use the default postgres user, or you could create a new one (Click Users > Click "ADD USER ACCOUNT" > Fill out the form under "Built-in authentication". > Click "ADD". > Note the password.).

Once the connection between Cloud Run and Cloud SQL is open, the application will use this user account to interact with the database.

## Service Account
3. The service account that manages your Cloud Run application needs the appropriate permissions to interact with Cloud SQL.  To do this, we need to give that service account access with the `Cloud SQL Client` role.  Navigate to the "IAM & Admin" page.

4. Your service account may be in the Service Account tab or the IAM tab.  Assuming it's the IAM tab, click the IAM tab.

5. Click on the Edit icon next to the service account handling your Cloud Run instance.

6. Click "ADD ANOTHER ROLE".

7. Search for and select "Cloud SQL Client".  Click "SAVE".


## Cloud Run
8. Open the Cloud Run application you want to connect to Cloud SQL.  Click "EDIT & DEPLOY NEW REVISION".

9. Update the container image with code supporting the connection between Cloud Run and Cloud SQL.

10. Click "VARIABLES & SECRETS".

11. For a Django application, you need to add the appropriate .env variables to settings.py.  H

`GOOGLE_CLOUD_SQL_NAME` refers to the specific database within the Cloud SQL instance you are connecting to.

`GOOGLE_CLOUD_SQL_USER`, and `GOOGLE_CLOUD_SQL_PASSWORD` refer to a database user that in the instance of Cloud SQL you are working with.  For the SQL password, it could be useful to store the value in Secrets Manager.

`GOOGLE_CLOUD_SQL_HOST` and `GOOGLE_CLOUD_SQL_PORT` both describe the running Cloud Run application you are connecting through.  You will need an unused port for this.
```python
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": GOOGLE_CLOUD_SQL_NAME,# DB name (not Cloud SQL instance name)
            "USER": GOOGLE_CLOUD_SQL_USER, # DB user name
            "PASSWORD": GOOGLE_CLOUD_SQL_PASSWORD, # DB user password
            "HOST": GOOGLE_CLOUD_SQL_HOST, # The Cloud SQL reference
            "PORT": GOOGLE_CLOUD_SQL_PORT, # The port for your Cloud Run application
        },
    }
```

12. Under "Cloud SQL connections", click "ADD CONNECTION".

13. Select the Cloud SQL instance that you want to connect to.

14. Click "DEPLOY".


## Preparing the database
15. If you have not done so already during local development, you would want to run `python manage.py migrate` on the database.  To do so, you can set up a local Cloud SQL Auth Proxy to connect to the same Cloud SQL instance.  This will let you not only perform the migration but also explore the database via other manage.py commands, such as shell or shell_plus.



## Resources

- [How to Deploy Production Django 4 using Google Cloud Run, Cloud SQL, and Cloud Storage](https://dev.to/facepalm/how-to-deploy-production-django-4-using-google-cloud-run-cloud-sql-and-cloud-storage-2i7d)