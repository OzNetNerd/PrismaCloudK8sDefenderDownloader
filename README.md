# Prisma Cloud K8s Defender Downloader

Automates the downloading of Prisma Cloud's K8s Defender via Helm Chart and YAML file.

## Instructions

Set the following environment variables: 
* `DOWNLOAD_TYPE` - `YAML` and `HELM` are the accepted options
* `PRISMA_ACCESS_KEY_ID`
* `PRISMA_SECRET_ACCESS_KEY`
* `PRISMA_CONSOLE_URL`

Upon execution, the script will generate either a YAML text file or a Helm binary file.