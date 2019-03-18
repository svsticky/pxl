# Philosophy and goals

Photos don't change a lot. Performance matters. Discussions and comments can be
held through other channels. No one likes yet another forum, mailing list or
website to check for discussions within their social graph.

## Scope

An image gallery application for our Study Association should provide:

 - Photos for viewing/browsing.
 - Downloading photos.

And not a whole lot else. There may be orthogonal concerns, but `pxl` will
generally choose to defer their implementation to other tools.

## Privacy

GDPR and laws aside, privacy-aware design and systems building is just the
ethical thing to do. We want `pxl` to:

 - Play nice with existing authentication systems.
 - Provide a "request takedown" button.
 - Strip unneccessary EXIF metadata from photos.

**N.B.:** This seems to conflict with "download photos for later" from earlier.
And to a certain extend, it does. However, once you've given someone a piece of
information, you cannot take it back. This is true for everything though.

## Performance and mobile

Visiting a single page shouldn't take ages. It also shouldn't consume half your
mobile data plan. This saves both time and money. We want `pxl` to:

 - Compress photos (without loads of quality loss)
 - Load different image sizes as appropriate for the view. Don't download a
   1MB image to display it at 400x300 pixels.

## User experience

Browsing image galleries should be a nice experience for the user. Users
rightfully expect all the standard stuff that browsers have been doing for ages
to work. In particular:

 - Navigation/history works like expected.
 - Links work in the standard manner.
 - Image galleries should be useable without JavaScript enabled. JavaScript may
   be used for progressive enhancement when appropriate.

## Admin experience

Last on the list, and the least of the priorities at the start. `pxl` provides
a CLI application that people can run in their terminal (if they have Python
installed). This enables us to make progress quickly and to get things out of
the door.

Maybe we'll eventually provide a way to make it easier for non-technical users
to manage photo libraries. It is last on the list of goals at the moment,
though.
