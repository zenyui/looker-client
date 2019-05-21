# Looker Client

Scripts for the Looker API

[Looker API Docs](https://docs.looker.com/reference/api-and-integration)

### Quickstart

Generate API client ID and secret ([docs](https://docs.looker.com/reference/api-and-integration/api-auth))

create a folder in this repo called `local` and add environment files that copy the [environment file template](./sample.env.template)

boot the provided docker container
```sh
Make run
```

view available commands
```sh
./cli.py --help
```

### Delete Users

show help

```sh
./cli.py delete-users --help
```

Provide a text file with user ID's on each line that you wish to delete


```sh
./cli.py --env ./local/some-env-file.env delete-users --fp ./local/delete-users-file.txt
```
