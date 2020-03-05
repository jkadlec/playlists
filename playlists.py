#! /usr/local/bin/python3
from typing import List, Dict, Iterator, Tuple
from collections import Counter
from sys import argv, stdout, stderr
from json import load, dump
from enum import Enum


class Operations(Enum):
    '''List of supported operations, must be in sync with changes.json.'''

    ADD_SONG = 1
    DELETE_PLAYLIST = 2
    ADD_PLAYLIST = 3


def _changes_iterator(changes: dict) -> Iterator[Tuple[str, Dict]]:
    '''Returns iterator that produces the next operation and its parameters.'''

    actions = changes['actions']

    for action in actions:
        operation = action['op']
        action.pop('op')
        yield operation, action


def _load_dict(path: str) -> Dict:
    with open(path) as f:
        return load(f)


def _list_to_lookup(inp: List[Dict]) -> Dict[str, Dict]:
    return {val['id']: val for val in inp}


def _add_playlist(playlists: Dict[str, Dict], songs: Dict[str, Dict],
                  users: Dict[str, Dict], playlist_id: str, user_id: str, song_ids: List[str]) -> None:
    for song_id in song_ids:
        if song_id not in songs:
            raise KeyError('No such song, id={song_id}.')
    if user_id not in users:
        raise KeyError(f'No such user, id={user_id}.')

    playlist = {'id': playlist_id, 'song_ids': song_ids, 'user_id': user_id}
    playlists[playlist_id] = playlist


def _remove_playlist(playlists: Dict[str, Dict], playlist_id: str) -> None:
    if playlist_id not in playlists:
        raise KeyError(f'No such playlist, id={playlist_id}.')
    playlists.pop(playlist_id)


def _add_song(playlists: Dict[str, Dict], songs: Dict[str, Dict], playlist_id: str, song_id: str) -> None:
    if playlist_id not in playlists:
        raise KeyError(f'No such playlist, id={playlist_id}.')
    if song_id not in songs:
        raise KeyError(f'No such song, id={song_id}.')

    playlist = playlists[playlist_id]
    playlist['song_ids'].append(song_id)


def _apply_changes(playlists: Dict[str, Dict],
                   songs: Dict[str, Dict],
                   users: Dict[str, Dict],
                   changes: Dict[str, Dict]) -> Counter:
    # We need to store the maximum seen playlist id in order to be able to add new playlists
    # with consecutive id's.
    max_playlist_id = int(max(playlists.keys(), key=lambda _: int(_)))
    op_counter: Counter = Counter()

    itt = _changes_iterator(changes)
    for operation, parameters in itt:
        op_counter.update([operation])

        if operation == Operations.ADD_SONG.name:
            _add_song(playlists, songs, **parameters)

        elif operation == Operations.ADD_PLAYLIST.name:
            max_playlist_id += 1
            _add_playlist(playlists=playlists, songs=songs, users=users, playlist_id=str(max_playlist_id),
                          **parameters)

        elif operation == Operations.DELETE_PLAYLIST.name:
            _remove_playlist(playlists, parameters['playlist_id'])
        else:
            raise KeyError(f'No such operation {operation}')

    return op_counter


def _main(input_path: str, changes_path: str, output_path: str):
    # Load input data.
    input_dict = _load_dict(input_path)
    changes = _load_dict(changes_path)

    op_counter, output = _create_output_dict(input_dict, changes)

    if output_path != '-':
        with open(output_path, 'w') as f:
            dump(output, f, indent=4, sort_keys=True)
    else:
        dump(output, stdout, indent=4, sort_keys=True)

    print(f'Done. Operations made:\n{op_counter}', file=stderr)


def _create_output_dict(input_dict: Dict, changes: Dict):
    # Turn the input lists into lookup dictionaries.
    playlists_lookup = _list_to_lookup(input_dict['playlists'])
    songs_lookup = _list_to_lookup(input_dict['songs'])
    users_lookup = _list_to_lookup(input_dict['users'])

    # Change the dictionaries in place.
    op_counter = _apply_changes(playlists_lookup,
                                songs_lookup,
                                users_lookup,
                                changes)

    # Create new dictionary with the changed data, discard the id's. Only playlists change.
    output = {'playlists': list(playlists_lookup.values()),
              'users': input_dict['users'],
              'songs': input_dict['songs']}

    return op_counter, output


def _help(name: str) -> str:
    return f'Usage {name}: <path_to_input_file.json> <path_to_changes_path.json> <output_file.json>'


if __name__ == '__main__':
    if len(argv) == 4:
        _main(*argv[1:])
    else:
        print(_help(argv[0]))
