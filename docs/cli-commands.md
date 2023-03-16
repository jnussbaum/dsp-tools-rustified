[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# The CLI commands of DSP-TOOLS

## Before starting: Have in mind the subdomains of a DSP server

DaSCH follows some conventions when setting up DSP servers. 
Most of the commands documented on this page
assume that you know how to address the subdomains of a DSP server.
There are three relevant URLs you should know about:

 - Subdomain `admin` stands for the DSP-APP frontend that you look at in your browser
 - Subdomain `api` stands for the DSP-API (where DSP-TOOLS sends its data to) 
 - Subdomain `iiif` stands for the SIPI server interface (where DSP-TOOLS sends the multimedia files to)

This means that for uploading data to a DSP server 
on the domain `dasch.swiss`, 
you have to type the following:

```bash
dsp-tools xmlupload -s https://api.dasch.swiss -u root@example.com -p 'test' -S https://iiif.dasch.swiss xml_data_file.xml
```



## `create`

This command reads a JSON project definition (containing one or more data models)
and creates it on a DSP server.

```bash
dsp-tools create [options] project_definition.json
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API 
- `-V` | `--validate-only` (optional): validate the JSON file without creating it on the DSP server
- `-l` | `--lists-only` (optional): create only the lists (prerequisite: the project exists on the server)
- `-v` | `--verbose` (optional): print more information about the progress to the console
- `-d` | `--dump` (optional): dump test files for DSP-API requests

The defaults are intended for local testing: 

```bash
dsp-tools create project_definition.json
```

will create the project defined in `project_definition.json` on `localhost` for local viewing.

In order to create the same project
on the DSP server `https://admin.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools create -s https://api.dasch.swiss -u root@example.com -p 'test' project_definition.json
```

The expected JSON format is [documented here](./file-formats/json-project/overview.md).



## `get`

This command retrieves a project with its data model(s) from a DSP server 
and writes it into a JSON file. 
This JSON file can then be used 
to create the same project on another DSP server. 

```bash
dsp-tools get [options] project_definition.json
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API 
- `-P` | `--project` (mandatory): shortcode, shortname or IRI of the project 
- `-v` | `--verbose` (optional): print more information about the progress to the console

The following example shows 
how to get a project from the DSP server `https://admin.dasch.swiss`:

```bash
dsp-tools get -s https://api.dasch.swiss -u root@example.com -p 'test' -P my_project project_definition.json
```

The expected JSON format is [documented here](./file-formats/json-project/overview.md).



## `xmlupload`

This command uploads data defined in an XML file to a DSP server. 

```bash
dsp-tools xmlupload [options] xml_data_file.xml
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server where DSP-TOOLS sends the data to
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `-S` | `--sipi` (optional, default: `http://0.0.0.0:1024`): URL of the SIPI server where DSP-TOOLS sends the multimedia files to 
- `-i` | `--imgdir` (optional, default: `.`): folder from where the paths in the `<bitstream>` tags are evaluated
- `-I` | `--incremental` (optional) : The links in the XML file point to IRIs (on the server) 
                                      instead of IDs (in the same XML file).
- `-V` | `--validate` (optional): validate the XML file without uploading it
- `-v` | `--verbose` (optional): print more information about the progress to the console
- `-m` | `--metrics` (optional): write metrics into a 'metrics' folder

Output:

- A file named `id2iri_mapping_[timestamp].json` is written to the current working directory.
  This file should be kept if data is later added with the [`--incremental` option](./incremental-xmlupload.md)

The defaults are intended for local testing: 

```bash
dsp-tools xmlupload xml_data_file.xml
```

will upload the data defined in `xml_data_file.xml` on `localhost` for local viewing.

In order to upload the same data 
to the DSP server `https://admin.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools xmlupload -s https://api.dasch.swiss -u root@example.com -p 'test' -S https://iiif.dasch.swiss xml_data_file.xml
```

The expected XML format is [documented here](./file-formats/xml-data-file.md).



## `excel2json`

This command creates a JSON project definition file from a nested folder structure with Excel files.

``` 
dsp-tools excel2json excelfolder project_definition.json
```

The expected Excel file format and the folder structure are documented [here](./file-formats/excel2json.md).



### `excel2lists`

This command creates the "lists" section of a JSON project file from Excel files.

```bash
dsp-tools excel2lists [options] excelfolder lists_section.json
```

The following options are available:

- `-v` | `--verbose` (optional): print more information about the progress to the console

The expected Excel file format and the folder structure are documented [here](./file-formats/excel2json.md#lists-section).

| <center>Hint</center>                                                    |
|--------------------------------------------------------------------------|
| The command [`excel2json`](#excel2json) might be more convenient to use. |



### `excel2resources`

This command creates the "resources" section of a JSON project file from an Excel file.

```bash
dsp-tools excel2resources resources.xlsx resources_section.json
```

The expected Excel format is [documented here](./file-formats/excel2json.md#resources-section).

| <center>Hint</center>                                                    |
|--------------------------------------------------------------------------|
| The command [`excel2json`](#excel2json) might be more convenient to use. |



### `excel2properties`

This command creates the "properties" section of a JSON project file from an Excel file.

```bash
dsp-tools excel2properties properties.xlsx properties_section.json
```

The expected Excel format is [documented here](./file-formats/excel2json.md#properties-section).

| <center>Hint</center>                                                    |
|--------------------------------------------------------------------------|
| The command [`excel2json`](#excel2json) might be more convenient to use. |



## `excel2xml`

This command creates an XML file
from an Excel/CSV file that is already structured according to the DSP specifications.
This is mostly used for DaSCH-internal data migration.

```bash
dsp-tools excel2xml data_source.xlsx project_shortcode ontology_name
```

Arguments:

 - data_source.xlsx (mandatory): path to the CSV or XLS(X) file containing the data
 - project_shortcode (mandatory): shortcode of the project that this data belongs to
 - ontology_name (mandatory): name of the ontology that the data belongs to

The expected Excel format is [documented here](./file-formats/excel2xml.md).

If your data source is not yet structured according to the DSP specifications, 
you need a custom Python script for the data transformation. 
For this, you might want to import the module `excel2xml` into your Python script, 
which is described [here](./excel2xml-module.md).



## `id2iri`

This command replaces internal IDs contained in the `<resptr>` tags of an XML file
by IRIs provided in a mapping file.

```bash
dsp-tools id2iri xmlfile.xml mapping.json
```

The following options are available:

- `--outfile` (optional, default: `id2iri_replaced_[timestamp].xml`): path to the output file
- `-v` | `--verbose` (optional): print more information about the progress to the console

This command cannot be used isolated, 
because it is part of a bigger procedure 
that is documented [here](./incremental-xmlupload.md).



## `start-stack`

This command runs a local instance of DSP-API and DSP-APP.

```bash
dsp-tools start-stack
```

dsp-tools will ask you for permission to clean Docker with a `docker system prune`. This will remove all unused 
containers, networks and images. If you don't know what that means, just type `y` ("yes") and then `Enter`.

The following options are available:

- `--max_file_size=int` (optional, default: `250`): max. multimedia file size allowed by SIPI, in MB (max: 100'000)
- `--prune` (optional): execute `docker system prune` without asking
- `--no-prune` (optional): don't execute `docker system prune` (and don't ask)

Example: If you start the stack with `dsp-tools start-stack --max_file_size=1000`, 
it will be possible to upload files that are up to 1 GB big. 
If a file bigger than `max_file_size` is uploaded, 
SIPI will reject it.

More help for this command can be found [here](./start-stack.md).



## `stop-stack`

When your work is done, shut down DSP-API and DSP-APP with

```bash
dsp-tools stop-stack
```

This deletes all Docker volumes, and removes all data that was in the database.