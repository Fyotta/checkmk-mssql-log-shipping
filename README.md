# Checkmk MSSQL Log Shipping

![build](https://github.com/fyotta/checkmk-mssql-log-shipping/workflows/build/badge.svg)
![flake8](https://github.com/fyotta/checkmk-mssql-log-shipping/workflows/Lint/badge.svg)
![pytest](https://github.com/fyotta/checkmk-mssql-log-shipping/workflows/pytest/badge.svg)

## Description
Checkmk extension - Special agent for monitoring MSSQL Log Shipping Replication

## Development Tips

For the best development experience use [VSCode](https://code.visualstudio.com/) with the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. This maps your workspace into a checkmk docker container giving you access to the python environment and libraries the installed extension has.

### Continuous integration
#### Environment

To build the package hit `Crtl`+`Shift`+`B` to execute the build task in VSCode.

`pytest` can be executed from the terminal or the test ui.

#### Github Workflow

The provided Github Workflows run `pytest` and `flake8` in the same checkmk docker conatiner as vscode.

## License

This code is distributed under the terms of the GNU General Public License, version 3 (GPLv3).
See the LICENSE file for details on the license terms.
