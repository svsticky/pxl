# Configuration

Before you can configure `pxl`, you need a few things:

 - A `pxl` installation, see the installation guide [here][docs-install].
 - Credentials to an S3 bucket. You need a Cloud Provider to give these to you.
 - Credentials for deployment. (An SSH user, and a path to upload the generated
   site).

If you've got this; you're ready to move!

## Config file

`pxl` reads config from `~/.config/pxl/config.json`. This is a JSON file with
a top level object from which `pxl` understands the following config keys:

 - `"s3_endpoint"`
 - `"s3_region"`
 - `"s3_bucket"`
 - `"s3_key_id"`
 - `"s3_key_secret"`
 - `"deploy_host"`
 - `"deploy_user"`
 - `"deploy_path"`
 - `"public_image_url"`

You can write this file yourself, or you can use the setup wizard below. In
case `pxl` ever gets new settings, it is probably good to know that this file
exists.

This is an example config file:

```json
{
  "s3_endpoint": "digitaloceanspaces.com",
  "s3_region": "ams3",
  "s3_bucket": "pxl-demo",
  "s3_key_id": "XXXXXXXXXXXXXXXXXXXX",
  "s3_key_secret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "deploy_host": "svsticky.nl",
  "deploy_user": "pxl",
  "deploy_path": "pxl-demo.svsticky.nl",
  "public_image_url": "https://pxl-demo.ams3.cdn.digitaloceanspaces.com"
}
```

## Setup wizard

This is a small convenience to get going with `pxl`. If you don't want to write
the config file by hand, you can let `pxl` generate it.

In your copy of the `pxl` repository, you can run the `pxl init` command. If
you answer the questions like below (just hitting the enter key uses the
default), you'll get the same config file as we showed you before.

```
$ pipenv run pxl init
We need some information. Please answer the prompts.
Defaults are between [brackets].

S3 endpoint [digitaloceanspaces.com]:
S3 region [ams3]:
S3 bucket: pxl-demo
S3 key ID: XXXXXXXXXXXXXXXXXXXX
S3 key secret (not shown):
Deploy host: svsticky.nl
Deploy user: pxl
Deploy path: pxl-demo.svsticky.nl
Public image base URL (optional) []: https://pxl-demo.ams3.cdn.digitaloceanspaces.com
```

 [docs-install]: /installation
