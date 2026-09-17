# tandem-cli

A tiny command line client for [Tandem](https://tandem.inc) requirements, written at Daily's to drive a robot program's requirements from the terminal. One file, standard library only, Python 3.9 or newer: `tandem` is the whole program, so installing it is a curl and a chmod.

## Install

```
curl -O https://raw.githubusercontent.com/Shmoazz/tandem-cli/main/tandem
chmod +x tandem && mv tandem /usr/local/bin/
```

## Auth

An API key first, a borrowed browser session second.

Create a key in Tandem under Settings > Integrations > API Keys, then either

```
export TANDEM_API_KEY=...
```

or put it on the first line of `~/.config/tandem/api_key`. It travels as `X-API-Key`.

With no key set, on macOS, the tool borrows the session from a logged-in app.tandemai.io tab in Google Chrome: it reads the Cognito client id and refresh token out of the tab and mints a fresh id token for that run, because the id token sitting in the page expires every hour. Chrome's View > Developer > Allow JavaScript from Apple Events has to be on and the tab has to be logged in. That token goes out as `Authorization: Bearer`.

## Use

```
tandem programs                      programs you can see
tandem tables                        requirement tables in a program
tandem ls [-t TABLE]                 requirements in a table, as a tree
tandem add -t TABLE -n NUMBER --name NAME --statement TEXT
           [--status draft|review|approved|rejected] [--owner EMAIL] [--parent NUMBER]
tandem update NUMBER [-t TABLE] [--name ..] [--statement ..] [--status ..]
           [--owner ..] [--parent NUMBER|none]
tandem import FILE.csv -t TABLE      bulk create from CSV
tandem rm NUMBER -t TABLE --reason "why"
```

`TABLE` is a table name or its UUID, and `-t` can be left off when the program holds one table. `-p` names the program, `TANDEM_PROGRAM` names it once, and with an API key and a single program it is picked for you. `TANDEM_OWNER` defaults the owner email on new rows. An import CSV has the columns `Number,Name,Statement,Status,Owner,Parent`; a row whose number already exists is skipped, so a half-finished import is safe to rerun.

```
tandem programs
tandem -p <program-uuid> tables
tandem -p <program-uuid> ls -t "Motor Requirements"
tandem add -t "Motor Requirements" -n MT-TQ-01 --name "Turntable torque" --statement "The turntable motor delivers 10 Nm at the output." --parent MT-TQ
tandem update MT-TQ-01 --status review --parent none
tandem import reqs.csv -t "Motor Requirements"
tandem rm MT-TQ-01 -t "Motor Requirements" --reason "duplicate"
```

## What it learned about the API

Base `https://app.tandemai.io/api/v1`. Requirements live at `/programs/{p}/req-tables/{t}/requirements[/{id}]`: create is POST, list is GET, update is PUT (PATCH returns 405; PUT accepts a partial body and can renumber and re-parent through `number` and `parent_id`), delete is DELETE with `{"deletion_reason": "..."}`. Status values are lowercase (`draft`, `review`, `approved`, `rejected`). The hierarchy is `parent_id`, never inferred from numbering. Linking a verification artifact to a requirement (`/requirements/{id}/artifacts/from-node-artifact`) fails with "Requirement does not belong to this program" because rows come back with a null `program_id`; the web app can make that link, the API cannot, as of August 2026.

## License

MIT.
