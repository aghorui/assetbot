Assetbot
================================================================================

Assetbot is a Python program that watches for files being created and updated,
and subsequently converts (or exports) them to a destination where it can be
used or accepted by another program. It automates and streamlines the process
of simultaneously saving a development/project file used for developing some
asset as well as exporting it to the correct location of where the asset is
supposed to be used (say, a parent project). In other words, it's a generic
**"hot reloader"** for your assets.

```
    .../dev_files/            .../project/assets/
    |                         |
    +--file1.svg    ----->    +--file1.png
    |                         |
    +--file2.xcf    ----->    +--file2.png
    |                         |
    +--file3.kra    ----->    +--file3.png
    |                         |
    +--file4.aup    ----->    +--file4.ogg
```

Say that you're writing a book in Markdown or TeX that has diagrams or graphics.
GUI applications like Inkscape or GIMP have some amount of latency in the sense
that you have to go through multiple dialogs, then navigate to the desired
folder in a file dialog, and then wait for it to finish. This adds up quickly as
the number of diagrams in the project and the frequency of changes on them
increases.

In addition to that, the propensity of making mistakes while exporting,
forgetting to export something, or leaving out unwanted info or sensitive
metadata increases with the number of 'moving gears' in the project. This
project attempts to automate away this effort.

### Exporters and Workflow

Assetbot works on the concept of having a number of exporters that would convert
the files that have been supplied to them to a specified destination directory.
These exporters are specified by the user when assetbot starts. If a file
matches a pattern from an exporter, assetbot will invoke the exporter and make
it convert or generate the file in the destination folder.

```
                 +------------+      +--------+
         +------>|File watcher├----->|Exporter|---------+
         |       +------------+      +--------+         |
    +----+------+                              +--------v-------+
    |Source File|                              |Destination File|
    +-----------+                              +----------------+
     created or
     modified
```

You can also write your own exporters. Place them in the
`src/assetbot/exporters` directory to use them, and look for files in that
directory as a reference on how to write them.

An option to specify a directory to load exporters form will be added in the
future.

When Assetbot is launched, the program will automatically export all the
matching files in the specified directories, so that everything is knowingly
brought to a synchronised state and none of the files are left unexported. This
can be disabled with a flag if needed (see `assetbot -h`).

## "Caveats"/Points to Note

The exporters that currently shipped by default in this program depend on
external programs/executables which the program runs and are barebones for the
most part. Currently checks have not been added for testing dependency existence
and may be added later if deemed fit.

The reason this program is not "self contained" as you might expect it to be is
because it is meant to act as a sort of an automation "glue" to make your
development workflow quicker and more convenient and not act as another file
conversion program (eg. FFmpeg, ImageMagick, pandoc etc.) Additionally, the
needs of your export routines may be highly specific to the project that your
working on and you might almost always need to write custom extensions yourself
to meet your requirements.


## Installation (Without Package)

Make sure you have Python `3.10.12` or later installed.

Assetbot depends on two python packages: `toml` and `watchdog`. You can install
them by doing the following:

```
python3 -m pip install toml watchdog
```

Then run the following command in the `src/` folder:

```
python3 -m assetbot.assetbot [arguments]
```

There's also a convenience script called `assetbot.sh` that does the same thing.

```
bash assetbot.sh [arguments]
```

## Building and Installing the package

Install the `build` tool:

```
python3 -m pip install --upgrade build
```

Then cd to this project directory, and run the following command to create a
Wheel `.whl` package:

```
python3 -m build
```

The `.whl` package will be put in a newly created `dist/` folder in the project
directory.


The package can then be installed by doing the following:

```
cd dist
pip install <NAME OF PACKAGE>.whl
```

Now, the program will be available with the command `assetbot`. (Note that for
this to work there needs to be a valid writable directory in `PATH`. This would
often require you to have escalated privileges to write in one of the system
folders specified in that environment variable.)


## Basic Usage

The list of available commands and their descriptions can be printed out using
the `--help` flag.

```
assetbot -h
```

For a simple usage example, consider the following command:

```
assetbot --map-path ./source ./destination --allowed_exporters svg krita
```

This will make assetbot listen on the folder `source` for new and updated files,
and of they are `svg` or `krita` files, they will be converted and put into the
same relative path in destination.

Output from the program will look something like this:

```
assetbot version 0.1.2
Working directory: /home/user/documents
Current exporters: svg, krita
Watcher started for the following mappings:
a -> b

2024-01-01 12:13:14 - CREATE a/a.svg
2024-01-01 12:13:14 - EXPORT a.svg -> b
2024-01-01 12:13:17 - DONE   a.svg -> b/a.svg in 2.90 sec
2024-01-01 12:13:17 - UPDATE a/a.svg
2024-01-01 12:13:17 - EXPORT a.svg -> b
2024-01-01 12:13:18 - DONE   a.svg -> b/a.svg in 435.67 ms
```

You can also do the same by adding these settings to a configuration file and
then invoking the program with it. For example, if the configuration file is
`config.toml` then the command would be:

```
assetbot --config config.toml
```

You can dump an example configuration file using the following command:

```
assetbot --dump-default-config
```

## Todo

* **Add support for an extension folder**: Users will be allowed to place custom
  exporters into a particular folder that the program will read from. Most of
  the work for this is already in place. Just needs to be tested.

* **"Plugin" Packages alongside extensions:** Instead of haphazardly copy-pasting
  scripts to a folder, support will be added later to just add a package or
  module and use it as a plugin.

* **Unit Testing**: Add unit testing files to this project.

* **Support normal/verbose Log Levels**: There is currently no distinction
  between normal and verbose logging (but there is between silent and these
  other two). This will be worked on later.

* **Exporter Configuration from Command Line:** Allow exporter config to be
  specifiable from the command line and not just using config files.

* **Enforce parameter validation for exporters:** Currently no validation is
  done automatically for the parameters passed to the exporters. Validation will
  be added later.

* **Manage Match Pattern/Destination Filename conflicts:** Currently no system
  is in place to manage conflicts if in case two exporters match for the same
  pattern or write to the same destination file. This will be managed later.

## Acknowledgements

This program makes direct use of the following Python projects:

```
watchdog     - https://pypi.org/project/watchdog/
toml         - https://pypi.org/project/toml/
platformdirs - https://pypi.org/project/platformdirs/
```

## License

This project is available under the BSD 2-Clause License. See [COPYING][license]
for more details.


[license]: ./COPYING