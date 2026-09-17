# tandem-cli

`tandem` is one executable file that drives Tandem's requirements API (app.tandemai.io) from a terminal.
It was written at Daily's so a robot program's requirements could be authored and reviewed as text rather than clicked into a browser.
README.md is what a user reads; this is what the next model needs.

## The one-file law

The install promise is `curl` plus `chmod +x`, so `tandem` stays ONE file, standard library only, Python 3.9 or newer.
Never split it into modules, never add a dependency, never add a setup.py: structure it internally instead.
Every decision sits in a small pure function above `main()`, and the network lives only in `api`, `mint_token` and `chrome_grab`.
A new command is argparse wiring in `parse_args`, a branch in `main`, one pure function beside the others, and its test.
A pure function that prints or exits with a new sentence is still fine; one that opens a socket is not.

## Check

`./check.sh` is the one command that answers pass or fail: `py_compile tandem`, then `python3 -m unittest -q tandem_test`.
Nothing is done until it is green.
`tandem_test.py` loads the extensionless `tandem` through `SourceFileLoader`, so the two files have to stay in one directory.
When you doubt a test, break the line it covers and watch it fail; that is how all 36 were proven.
Clear `__pycache__` if a mutation seems uncaught: a change that leaves the file the same size within the same second reuses the old `.pyc`.

## Auth

The order is `TANDEM_API_KEY`, then the first line of `~/.config/tandem/api_key`, then a logged-in app.tandemai.io tab in Google Chrome.
An API key travels as `X-API-Key`; a borrowed Chrome session travels as `Authorization: Bearer`.
The Chrome path is macOS only, runs osascript, and needs Chrome's View > Developer > Allow JavaScript from Apple Events turned on.
It reads the Cognito client id and refresh token out of the tab's localStorage and mints a fresh id token from Cognito on every run.
Never go back to reading `idToken` out of localStorage: it expires hourly, and the CLI then dies with a 401 for an hour at a time.
The refresh token is good for weeks, which is the only reason borrowing a session works at all.
Cloudflare answers the default `Python-urllib/3.x` User-Agent with error 1010, so every request carries `USER_AGENT`, and any new request path must too.

## The API

Base is `https://app.tandemai.io/api/v1`, and requirements live at `/programs/{p}/req-tables/{t}/requirements[/{id}]`.
Update is PUT and never PATCH: PATCH returns 405, and PUT accepts a partial body, so it can renumber through `number` and re-parent through `parent_id`.
DELETE needs a body, `{"deletion_reason": "..."}`.
The hierarchy is `parent_id` alone and is never inferred from the numbering; the server returns `level`, which is what `ls` indents by.
Status words are lowercase (`draft`, `review`, `approved`, `rejected`) while the UI says "In Review", which is what `STATUS_WORDS` exists to translate.
Requirement rows come back with a null `program_id`, which is Tandem's bug and not ours.
That null makes `POST /programs/{p}/requirements/{id}/artifacts/from-node-artifact` answer "Requirement does not belong to this program", so the CLI cannot link a CAD artifact to a requirement and the web app has to do it by hand.
That was the state in August 2026; retest it before building anything on verification links.

## Gotchas

`import` skips a row whose number already exists, so a half-finished import is safe to rerun.
A CSV parent that has not been created yet is a warning and a top level row, never a failure, because one stale reference should not strand the rest of the file.
`csv_row_body` returns its warning instead of printing it, which is the only reason it is testable; the import loop prints it.
The exit sentences are the product: a person reads them, the tests assert them, and rewording one is a behaviour change.
`-t` can be left off only when the program holds exactly one table, and `-p` only when the environment or the Chrome tab names the program.
Never an emdash, in code, in copy or in a commit message.
