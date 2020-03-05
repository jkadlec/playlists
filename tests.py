import pytest
import playlists

_BASIC_INPUT = {'playlists': [{'id': '1', 'user_id': '1', 'song_ids': ['1']},
                              {'id': '2', 'user_id': '1', 'song_ids': ['2']}],
                'users': [{'id': '1', 'name': 'test name'}],
                'songs': [{'id': '1', 'artist': 'test artist', 'title': 'test title'},
                          {'id': '2', 'artist': 'test artist 2', 'title': 'test title 2'}]}

_BASIC_CHANGES = {'actions': [{'op': 'DELETE_PLAYLIST', 'playlist_id': '2'},
                              {'op': 'ADD_SONG', 'playlist_id': '1', 'song_id': '2'},
                              {'op': 'ADD_PLAYLIST', 'user_id': '1', 'song_ids': ['1', '2']}]}


def _songs_and_users_match(output, check_against=_BASIC_INPUT):
    return output['users'] == check_against['users'] and output['songs'] == check_against['songs']


def test_helpers():
    playlist_list = _BASIC_INPUT['playlists']
    assert playlists._list_to_lookup(playlist_list) == {'1': playlist_list[0], '2': playlist_list[1]}


def test_non_existing():
    with pytest.raises(KeyError):
        playlists._add_playlist('1', {}, {}, {}, '1', [])

    with pytest.raises(KeyError):
        playlists._remove_playlist({}, '1')

    with pytest.raises(KeyError):
        playlists._add_song(playlists={'id': '1'}, songs={'id': '1'}, playlist_id='2', song_id='1')

    with pytest.raises(KeyError):
        playlists._add_song(playlists={'id': '2'}, songs={'id': '1'}, playlist_id='1', song_id='1')


def test_no_changes():
    _, output = playlists._create_output_dict(_BASIC_INPUT, {'actions': []})
    assert output == _BASIC_INPUT


def test_add_song():
    _, output = playlists._create_output_dict(_BASIC_INPUT,
                                              {'actions': [{'op': 'ADD_SONG', 'playlist_id': '1', 'song_id': '2'}]})
    changed_playlist = [pl for pl in output['playlists'] if pl['id'] == '1'][0]
    assert changed_playlist['song_ids'] == ['1', '2']

    assert _songs_and_users_match(output)


def test_add_playlist():
    _, output = playlists._create_output_dict(_BASIC_INPUT,
                                              {'actions': [{'op': 'ADD_PLAYLIST', 'user_id': '1', 'song_ids': ['2']}]})
    assert len(output['playlists']) == 3
    changed_playlist = [pl for pl in output['playlists'] if pl['id'] == '3']
    assert len(changed_playlist) == 1
    changed_playlist = changed_playlist[0]
    assert changed_playlist['user_id'] == '1'
    assert changed_playlist['song_ids'] == ['2']

    assert _songs_and_users_match(output)


def test_remove_playlist():
    _, output = playlists._create_output_dict(_BASIC_INPUT,
                                              {'actions': [{'op': 'DELETE_PLAYLIST', 'playlist_id': '2'}]})
    assert len(output['playlists']) == 1
    assert output['playlists'][0]['id'] == '1'

    assert _songs_and_users_match(output)
