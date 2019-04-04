# State file

Currently, `pxl` places a `state.json` file at the root of your bucket. This
format is currently purposefully left undocumented, because we **don't offer
any backwards compatibility guarantees** for this format at this time.

Furthermore, this state file will likely be changed into a SQLite database in
the future. Any automated tools built on top of it **will break** with future
versions of this format.

**However**, `pxl` will provide a migration step for existing users. The `pxl`
authors will need this script to work correctly. Make your own analysis to
wether this means that `pxl` is ready for your real-world use.
