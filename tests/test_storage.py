'''Tests for storage functions'''

import os
import os.path
import goto
import pytest
import shutil
try:
  from pathlib import Path
except ImportError:
  from pathlib2 import Path

import test_util

@test_util.custom_home
def test_get_home_config():
    '''Test that GetHomeConfig returns a valid directory structure.'''
    home_directory = goto.storage.get_config_home()
    assert isinstance(home_directory, str)

@test_util.custom_home
def test_touch_directory_structure():
    '''Test that touch directory can create a directory.'''
    target_directory = goto.storage.get_config_home()
    assert isinstance(target_directory, str)
    goto.storage.touch_directory(target_directory)
    assert os.path.isdir(target_directory)


@test_util.custom_home
def test_get_default_profile_with_nothing():
    data = goto.storage.get_default_profile()
    assert data == dict()


@test_util.custom_home
def test_get_updated_profile():
    pre_data = goto.storage.get_default_profile()
    goto.storage.update_default_profile({ 'test': 'abcd' })
    post_data = goto.storage.get_default_profile()
    assert pre_data != post_data
    assert post_data == { 'test': 'abcd' }

@test_util.custom_home
def test_no_such_file():
    data = goto.storage.get_named_profile('nosuchprofile')
    assert data == dict()
    does_exist = Path(os.environ['XDG_CONFIG_HOME'], 'goto-cd', 'nosuchprofile.toml').exists()
    assert does_exist

@test_util.custom_home
def test_private_files():
    with pytest.raises(goto.storage.StorageException):
        goto.storage.get_named_profile('_notokay', public_file=True)


@test_util.custom_home
def test_add_profiles():
    profiles = goto.storage.list_profiles()
    assert profiles == ['default']
    goto.storage.add_profile('abcd')
    profiles = goto.storage.list_profiles()
    assert set(profiles) == set(['default', 'abcd'])


@test_util.custom_home
def test_add_profiles_throws():
    with pytest.raises(goto.storage.StorageException):
        goto.storage.add_profile('_notallowed')
    goto.storage.add_profile('somerandomprofile')
    with pytest.raises(goto.storage.StorageException):
        goto.storage.add_profile('somerandomprofile')
    with pytest.raises(goto.storage.StorageException):
        goto.storage.add_profile('default')


@test_util.custom_home
def test_remove_profile():
    goto.storage.add_profile('abcd')
    profiles = goto.storage.list_profiles()
    assert set(profiles) == set(['default', 'abcd'])
    goto.storage.remove_profile('abcd')
    profiles = goto.storage.list_profiles()
    assert set(profiles) == set(['default'])


@test_util.custom_home
def test_remove_profile_throws():
    with pytest.raises(goto.storage.StorageException):
        goto.storage.remove_profile('nonexistant')

@test_util.custom_home
def test_remove_default_profile_throws():
    with pytest.raises(goto.storage.StorageException):
        goto.storage.remove_profile('default')

@test_util.custom_home
def test_get_active_profile():
    assert goto.storage.get_active_profile_name() == 'default'
    goto.storage.add_profile('abcd')
    goto.storage.set_active_profile('abcd')
    assert goto.storage.get_active_profile_name() == 'abcd'


@test_util.custom_home
def test_set_active_profile_throws():
    with pytest.raises(goto.storage.StorageException):
        goto.storage.set_active_profile('nonexistant')


@test_util.custom_home
def test_set_teleport():
    assert goto.storage.list_teleports() == []
    actual_directory = './'
    goto.storage.set_teleport('thisdir', actual_directory)
    assert goto.storage.list_teleports() == ['thisdir']

@test_util.custom_home
def test_remove_teleport():
    actual_directory = './'
    goto.storage.set_teleport('thisdir', actual_directory)
    assert goto.storage.list_teleports() == ['thisdir']
    goto.storage.remove_teleport('thisdir')
    assert goto.storage.list_teleports() == []

@test_util.custom_home
def test_get_matching_teleports():
    added_teleports = [
        ('a', test_util.home_path('./a')),
        ('abcd', test_util.home_path('./abcd')),
        ('b', test_util.home_path('./b'))
    ]
    try:
        for name, target in added_teleports:
            os.mkdir(target)
            goto.storage.set_teleport(name, target)
        assert set(goto.storage.list_teleports()) == set(['a', 'abcd', 'b'])
        assert set(goto.storage.get_matching_teleports('a')) == set(['a', 'abcd'])
        assert set(goto.storage.get_matching_teleports('b')) == set(['b'])
    except:
        for _, target in added_teleports:
            try:
                shutil.rmtree(target)
            except:
                pass

@test_util.custom_home
def test_set_teleport_throws():
    with pytest.raises(goto.storage.StorageException):
        goto.storage.set_teleport('abcd', './notanexistantdirectory')
    with pytest.raises(goto.storage.StorageException):
        goto.storage.set_teleport('', './')

@test_util.custom_home
def test_remove_teleport_throws():
    with pytest.raises(goto.storage.StorageException):
        goto.storage.remove_teleport('abcd')

@test_util.custom_home
def test_get_teleport_target():
  abspath = os.path.abspath('./')
  goto.storage.set_teleport('abcd', './')
  assert goto.storage.get_teleport_target('abcd') == abspath

@test_util.custom_home
def test_get_teleport_target_throws():
    with pytest.raises(goto.storage.StorageException):
      goto.storage.get_teleport_target('abcd')
