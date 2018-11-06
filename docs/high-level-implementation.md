# High-level Implementation

Please read [Philsophy and goals](./philosophy.md) for background first.

We'd also like to link to an Architecture document about why things are this
way, but it needs to be written first.

## Upload

 1. Download the current state file from S3.
 1. Load a directory of JPEG files.
 1. Create thumbnails of all required sizes.
 1. Compress these thumbnails (not the original).
 1. Strip metadata.
 1. Generate a UUID, put it in the (local copy of the) state file.
 1. Upload thumbnails to S3, record in state file.
 1. Upload the new state file to S3.

## Generate and deploy

 1. Download the state file from S3.
 1. Generate an index page with every album.
 1. Generate an album page with every image from that album.
 1. Generate an image page for every image in the album.
 1. Put these in a directory.
 1. Upload this directory to a webserver.
 1. Call a deploy hook.
