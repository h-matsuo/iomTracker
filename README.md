# procTracker

Utility Tool for Linux with [Procfs](https://en.wikipedia.org/wiki/Procfs) (Process Filesystem) by [Hiroyuki Matsuo](http://sdl.ist.osaka-u.ac.jp/~h-matsuo/)

Track disk I/O, memory usage and network communications.

## Installation

Just clone this repository.

```bash
$ git clone git@github.com:h-matsuo/procTracker.git
```

## Usage

```txt
usage: procTracker.py [-h] [-i <interval>] [-o <filename>] [--all] [--io]
                      [--mem] [--net]

track disk I/O, memory usage and network communications

optional arguments:
  -h, --help     show this help message and exit
  -i <interval>  set the tracking interval in [sec]; default = 1.0
  -o <filename>  write output to <filename>

tracking mode:
  --all          track all of the disk I/O, memory usage and network
                 communications; default mode
  --io           track disk I/O; allowed with --mem and --net
  --mem          track memory usage; allowed with --io and --net
  --net          track network communications; allowed with --io and --mem
```

## License

MIT License.
