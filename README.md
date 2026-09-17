# tandem-cli

A tiny command line client for [Tandem](https://tandem.inc) requirements, written at Daily's to drive our robot's requirements from the terminal. One file, standard library only, Python 3.9 or newer.

## Install

```
curl -O https://raw.githubusercontent.com/Shmoazz/tandem-cli/main/tandem
chmod +x tandem && mv tandem /usr/local/bin/
```

## Auth

Create an API key in Tandem under Settings > Integrations > API Keys, then either

```
export TANDEM_API_KEY=...
```

or put it on the first line of `~/.config/tandem/api_key`. On macOS with no key set, the tool falls back to borrowing the session from a logged-in app.tandemai.io tab in Chrome (View > Developer > Allow JavaScript from Apple Events must be on).

## Use

```
tandem programs
tandem -p <program-uuid> tables
tandem -p <program-uuid> ls -t "Motor Requirements"
tandem add -t "Motor Requirements" -n MT-TQ-01 --name "Turntable torque" --statement "The turntable motor delivers 10 Nm at the output." --parent MT-TQ
tandem update MT-TQ-01 --status review --parent none
tandem import reqs.csv -t "Motor Requirements"      # cols: Number,Name,Statement,Status,Owner,Parent
tandem rm MT-TQ-01 -t "Motor Requirements" --reason "duplicate"
```

Set `TANDEM_PROGRAM` to skip `-p`, and `TANDEM_OWNER` to default the owner email on new rows.

## What it learned about the API

Base `https://app.tandemai.io/api/v1`. Requirements live at `/programs/{p}/req-tables/{t}/requirements[/{id}]`: create is POST, list is GET, update is PUT (PATCH returns 405; PUT accepts a partial body and can renumber and re-parent through `number` and `parent_id`), delete is DELETE with `{"deletion_reason": "..."}`. Status values are lowercase (`draft`, `review`, `approved`, `rejected`). The hierarchy is `parent_id`, never inferred from numbering. Linking a verification artifact to a requirement (`/requirements/{id}/artifacts/from-node-artifact`) fails with "Requirement does not belong to this program" because rows come back with a null `program_id`; the web app can make that link, the API cannot, as of August 2026.

## License

MIT.
