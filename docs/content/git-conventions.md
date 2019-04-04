# Git conventions

A collection of `git` conventions we follow when developing `pxl`.

## Commit messages

Please stick to the commit message format:

```
<component>: <short imperative summary>

<longer description (optional)>
```

Keep the summary line around 50 characters. The body can have lines up to 72
characters (don't go over please). This makes it pleasant to read the `git log`
in the terminal.

Example (commit `9a1bf15`):

```
cli: Add validation of user input to get_input

This abstracts retries on invalid answers and makes it easier
to guarantee state is valid without having to type the same for
loop a bunch of times.
```

Merge commit format:

```
merge: '<short description>' (#<PR number>)
```

## Merging a PR

Merging a PR has two cases:

 1. Single commit: rebase + fast-forward merge.
 1. Multiple commits: rebase + non-fast-forward merge.

Introducing a separate merge commit for a single patch is wasteful. We never
squash PRs completely, but do ask authors to clean up the git history before a
merge.

Rebasing before merging ensures:

 - Conflicts are resolved in the commits that they first occur in.
 - Any QA checks like tests or type checks are run on the state of the
   repository **after** merging.
 - A linear history in `git log --graph`

Here is how to rebase before a merge:

```
$ git checkout master
$ git pull
$ git checkout <your branch name>
$ git rebase master

# Rewrite history on your own branch. This makes GitHub aware that
# your PR has actually been merged.
$ git push -f origin <your branch name>
```

Merging PRs with a single commit:

```
$ git checkout master
$ git merge --ff-only <your branch name>
$ git push origin master
```

Merging PRs with multiple commits:

```
$ git checkout master
$ git merge --no-ff <your branch name>  # Stick to merge commit format
$ git push origin master
```
