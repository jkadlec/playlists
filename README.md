Requirements:
 - Python 3.6.3 
 - no dependencies to run the code
 - for tests and checks: pip3 install flake8 mypy pytest

Usage:
 - `./playlists.py: <path_to_input_file.json> <path_to_changes_path.json> <output_file.json>`
 - use '-' to output to stdout
 - example: ./playlists.py test_data/basic/input.json test_data/basic/changes.json output.json

Tests:
 - flake8 and mypy check: `make check`
 - basic unit tests: `make test`

Scaling:
  In Python it's not easy to not read the whole json file into memory, so I would start
  with changing the input format to something that can be read record-by-record.

  For this particular example, we don't need to load users and songs into memory, we just need a way of
  checking they exist - but the output will never change, so we can leverage that by restricting the output.

  After that it would depend on what changes more often, input or 'changes' and what are the size.
  In real life we probably want to load one or the other into memory and stream incoming data
  through (if possible, if not, we'd load the rules into a db a add a caching layer).
  If our set of changes changes we reload the service or we can update it on the fly.

  We should also be able to do load-balancing based on songs and/or users if they can't fit into one db.
