# Overview

`pxl` let's you create **beautiful image galleries** as a static site that you
can host on any webserver. The generated site is fast and works without
JavaScript. Photo's are served from S3-compatible storage.

There is a [**live demo here**][pxl-demo]. Take a look around, see what you
think.

## Project status

The general architecture is finished. The code is usable and gradually
stabilizing. Internals may change at any point, so don't write code against
them.

The CLI is usable, but requires some UNIX knowledge to get working. We don't
offer packages for distributions yet. However, getting started is simple enough
if you have a few tools installed.

## Architecture

TODO: we need a picture.

`pxl` organises your photo library into albums which are stored on
S3-compatible buckets under unique, unguessable paths. It then generates a
static HTML site which you can deploy as you see fit.

Say you have a couple of directories of image files and you want to turn them
into a `pxl` site on `photos.example.com`. There are four steps:

 1. **Configure** `pxl` to be able to write to an S3 bucket.
 1. **Upload** photos to an S3 bucket under public but unguessable paths.
 1. **Generate** a static website based on bucket state.
 1. **Deploy** the static HTML files to `photos.example.com`.

## Requirements

In order to get started with `pxl`, you need:

 - An S3-compatible bucket to hold your photo library.
 - A webserver to host your HTML. You might be able to re-use your bucket for
   this if your cloud provider supports it.
 - A copy of the Python 3.7 programming language and some development tools.

If this sounds within the realm of possibilities, read on for more precise
installation instructions.

 [pxl-demo]: https://pxl-demo.svsticky.nl/
