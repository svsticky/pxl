# Philosophy and goals

`pxl` is a project which manages photos on S3 compatible object stores. This
document provides information about the project philosophy.

## Scope

Photos don't change a lot. Performance matters. Discussions and comments can be
held through other channels. No one likes yet another forum, mailing list or
website to check for discussions within their social graph.

A photo hosting application for our Study Association should provide:

 - Photos for viewing/browsing.
 - Downloading photos.

And not a whole lot else.

## Privacy

GDPR and laws aside, privacy-aware design and systems building is just the
ethical thing to do.

`pxl`:

 - Plays nice with existing authentication systems.
 - Provides a `request takedown` button.
 - Strips unneccessary EXIF metadata from photos.

**N.B.:** This seems to conflict with "download photos for later" from earlier.
And to a certain extend, it does. We need to write documentation on the threat
model.

## Performance, money and mobile

Visiting a single page shouldn't take ages. It also shouldn't consume half your
mobile data plan. This saves both time and money.

`pxl`:

 - Compresses photos (without loads of quality loss)
 - Loads different image sizes as appropriate for the view. Don't download a
   1MB image to display it at 400x300 pixels.

## User experience

Browsing the site should be a nice experience for the user. They should expect
all the standard stuff that browsers have been doing for ages to work. `pxl` is
a list of photo's and does not require a lot of fancyness.

 - Navigation/history works like expected. Links work in the standard manner.
 - Useable without JavaScript enabled.
 - Maximal browser compatibility; graceful degradation.

## Admin experience

Last on the list, and the least of the priorities at the start. `pxl` provides
a CLI application that people can run in their terminal (if they have Python
installed). This enables us to make progress quickly and to get things out of
the door.

We try to write `pxl` using the standard coding practices that help us swap
things out later.
