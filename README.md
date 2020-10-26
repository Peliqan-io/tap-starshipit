# tap-starshipit

This is a [Singer](https://singer.io) tap that produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from [StarShipIt's API](https://developers.starshipit.com/)
- Extracts Shipped & Unshipped Orders & Get Order [resources](https://developers.starshipit.com/docs/services/58e5bb041164fe12c0b94ff1/operations/Shipped-Orders)
- Outputs the schema for each resource

Data is incrementally extracted based on the last

Get Order is fetched from the data retrieved by Shipped and Unshipped orders. 

The catalog is dynamic created if not defined on the command line to use an static file.

## Configuration

Take a look at the [example config](example.config.json) as a starting point for creating your own.

The tap requires the developer Subscription Key which needs to be registered (https://developers.starshipit.com/api-key) and the account API KEY.

Config properties:

| Property | Example | Description |
|-------- | -------- | ------- |
| `subscription_key` |"64d*******a94" | the Developer Subscription Key |
| `api_key` | "8pp*******z99" | StarShipIt API Key |
| `start_date` | "2010-01-01T00:00:00Z" | The default start date to use. |


## Usage

First read through Singer's [Running and Developing Singer Taps and Targets](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#running-and-developing-singer-taps-and-targets) for getting started with running a tap and target.

For basic usage, run `tap-starshipit` with the configuration file.

Discovery:

```sh
tap-starshipit -c my-config.json --discover
```

Sync:

```sh
tap-starshipit -c my-config.json --catalog my-catalog.json
```

Sync using Dynamic Catalog discovery:

```sh
tap-starshipit -c my-config.json --state state.json
```

Short cuts for development purposes
```
export PYTHONPATH=$PYTHONPATH:$(pwd)
python tap_starshipit/__init__.py -c config.json
```
