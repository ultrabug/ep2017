# EuroPython 2017 talk

## Leveraging Consistent Hashing in your python applications

This repository features the **source code** I wrote for my talk:
- https://ep2017.europython.eu/conference/talks/leveraging-consistent-hashing-in-your-python-applications

## Example use cases

Those example codes are meant to give a quick idea on how simple it can be to
use consistent hashing on typical applications.

- `db_specialization.py`: quick & easy way to dedicate databases instances to a workload on read/write
- `disk_balancing.py`: split your disk & network I/O (NAS) efficiently
- `log_consistency.py`: make sure a specific and logically linked set of data is processed by the same worker machines
- `memcached_consolidation.py`: enhance & harden your python-memcached multi-server usage easily

## Test and run the game

- First we create a virtualenv, install the python librairies and run the demo server.

```bash

mkvirtualenv -p python3 ep2017
pip install -r requirements.txt

# to run the modulo based server
python modulo_server.py

# to run the consistent hashing based server
python consistent_server.py
```

- Then point your browser to the local server at `http://localhost:8000/`
- The live counter interface is accessible at `http://localhost:8000/live`

## Reference material

Akamai paper:
- https://www.akamai.com/us/en/multimedia/documents/technical-publication/consistent-hashing-and-random-trees-distributed-caching-protocols-for-relieving-hot-spots-on-the-world-wide-web-technical-publication.pdf


The `uhashring` pure python implementation:
- https://github.com/ultrabug/uhashring


Interesting links:
- http://theory.stanford.edu/~tim/s16/l/l1.pdf
- http://www.paperplanes.de/2011/12/9/the-magic-of-consistent-hashing.html
- https://www.youtube.com/watch?v=apHAqUG3Pi8
