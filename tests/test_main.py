"""Tests for rhasspy.__main__ CLI dispatcher."""
import sys
from unittest import mock
import pytest
from rhasspy.__main__ import main, _COMMANDS


def test_commands_list_not_empty():
    """Test that the commands list is populated."""
    assert len(_COMMANDS) > 0
    assert "hermes" in _COMMANDS


def test_main_no_arguments(capsys):
    """Test main() with no arguments shows usage."""
    with mock.patch.object(sys, "argv", ["rhasspy"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
    
    captured = capsys.readouterr()
    assert "Usage: rhasspy COMMAND ARGS" in captured.out
    assert "Available commands:" in captured.out


def test_main_unknown_command(capsys):
    """Test main() with unknown command shows error."""
    with mock.patch.object(sys, "argv", ["rhasspy", "unknown-command"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
    
    captured = capsys.readouterr()
    assert "Unknown command:" in captured.out
    assert "Available commands:" in captured.out


def test_main_valid_command_module_not_found():
    """Test main() with valid command that can't be imported."""
    # Use a valid command name but the module won't exist in test environment
    with mock.patch.object(sys, "argv", ["rhasspy", "hermes", "--help"]):
        with pytest.raises((ImportError, ModuleNotFoundError)):
            main()


def test_main_command_passes_arguments():
    """Test that arguments are properly passed to subcommand."""
    # Mock the module import and main function
    mock_module = mock.MagicMock()
    mock_module.main = mock.MagicMock()
    
    with mock.patch.object(sys, "argv", ["rhasspy", "hermes", "--arg1", "value1"]):
        with mock.patch("builtins.__import__", return_value=mock_module):
            # Capture sys.argv during the main() call
            captured_argv = None
            def capture_and_call():
                nonlocal captured_argv
                captured_argv = sys.argv[:]
            mock_module.main.side_effect = capture_and_call
            
            main()
            
            # Verify the submodule's main was called
            mock_module.main.assert_called_once()
            # Verify sys.argv was modified correctly (command name removed)
            assert captured_argv == ["rhasspy", "--arg1", "value1"]


def test_to_python_name_from_setup():
    """Test the module name conversion logic."""
    # Import the function from setup.py logic
    # This tests the naming convention used in the dispatcher
    
    # Test that command names map to expected module names
    test_cases = {
        "hermes": "rhasspyhermes",
        "asr-pocketsphinx": "rhasspyasr_pocketsphinx",
        "nlu-hermes": "rhasspynlu_hermes",
    }
    
    for command, expected_module in test_cases.items():
        # The __main__.py converts "rhasspy-MODULE" to "rhasspyMODULE"
        # It replaces hyphens with underscores
        module_name = "rhasspy" + command.replace("-", "_")
        assert module_name == expected_module


def test_all_commands_are_strings():
    """Test that all commands in _COMMANDS are strings."""
    for command in _COMMANDS:
        assert isinstance(command, str)
        assert len(command) > 0
