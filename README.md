# Work in progress PoC

## Pre-requisites

The following tools should be installed and configured.

* [AWS CLI](https://aws.amazon.com/cli/)
* [SAM CLI](https://github.com/awslabs/aws-sam-cli)
* [Python](https://www.python.org/)
* [Docker](https://www.docker.com/products/docker-desktop)

In Mac, running `sam build`, seeing "Cannot find docker" error. Try this

```shell
# https://stackoverflow.com/questions/63065951/aws-sam-build-failed-error-docker-is-unreachable-docker-needs-to-be-running-t
sudo ln -s "$HOME/.docker/run/docker.sock" /var/run/docker.sock
```

### Reference

* [link](https://medium.com/@ramanbazhanau/preparing-fastapi-for-production-a-comprehensive-guide-d167e693aa2b)
* [link](https://aws.amazon.com/blogs/compute/using-response-streaming-with-aws-lambda-web-adapter-to-optimize-performance/)
* [link](https://gist.github.com/liviaerxin/d320e33cbcddcc5df76dd92948e5be3b)
* [link](https://github.com/fastapi/fastapi/discussions/7457)
