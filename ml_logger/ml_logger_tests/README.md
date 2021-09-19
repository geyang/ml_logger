# Setting up test

Need to set the following environment parameter

```shell
export ML_LOGGER_TEST_S3_BUCKET=<your-s3-bucket-prefix>
export ML_LOGGER_TEST_GS_BUCKET=<your-gcp-gcs-bucket-prefix>
```

To create a public folder for test, you can run

```Makefile
create_s3_bucket:
    aws s3api create-bucket --acl public-read-write --bucket $$USER-ml-logger-test --region us-east-1
make_s3_public:
    aws s3api put-bucket-acl --acl public-read-write --bucket $$USER-ml-logger-test --region us-east-1
remove_s3_bucket:
    aws s3api delete-bucket --bucket $$USER-ml-logger-test

```

To create a public folder for Google Cloud Storage, you can first run

```Makefile
create_gce_bucket:
	gsutil mb gs://$$USER-ml-logger-test
remove_gce_bucket:
	gsutil rb gs://$$USER-ml-logger-test
```

To make it public you can go to the console page.
