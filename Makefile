check:
	mypy playlists.py
	flake8 --max-line-length=120 playlists.py
	flake8 --max-line-length=120 tests.py

test:
	python3 -m pytest tests.py
