# pyTLA
Takes python bytecode and generates TLA+ specs from it. You add your own tests for models to run.

## Installation
### Installing TLA
This tool uses command line TLA because the toolkit GUI proved to be too buggy for our purposes.

```
$ git clone https://github.com/pmer/tla-bin.git
$ ./download_or_update_tla.sh
$ sudo ./install.sh
```