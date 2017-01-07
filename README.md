# iomTracker

Utility Tool for Linux with [Procfs](https://en.wikipedia.org/wiki/Procfs) (Process Filesystem) by [Hiroyuki Matsuo](http://sdl.ist.osaka-u.ac.jp/~h-matsuo/)

Track IO and memory usage of specified process.

## Installation

Just clone this repository.

```bash
$ git clone git@github.com:h-matsuo/memTracker.git
```

## Usage

```txt
Usage: sudo python iomTracker.py <pid> <interval> [<output_path>]

iomTracker は，procfs (process filesystem) を備えた Linux システム上で，
指定したプロセスの IO およびメモリ使用量を監視することができるユーティリティツールです．
Python 2.x 系での動作を確認しています．

<pid>
        監視したいプロセスの ID を指定します．
<interval>
        データを取得する間隔を秒単位で指定します．
<output_path>
        データの出力ファイルを指定できます．
```

## License

MIT License.
