# @ref:test-tasks-board
# Method: @link:docs-index.
# Implementation: @link:script-tasks.
# Related: @link:task-workflow; @link:reference-token-contract.
# @tag:tooling @tag:testing
"""Task-board dependency and shared-checkout commit protections."""
import importlib.util
from pathlib import Path
import shlex
import subprocess

import pytest


@pytest.fixture
def board(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location('task_board', Path(__file__).parents[1] / 'scripts/tasks.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, 'REPO_ROOT', tmp_path)
    monkeypatch.setattr(module, 'BOARD', tmp_path / 'tasks')
    for column in module.COLUMNS:
        (module.BOARD / column).mkdir(parents=True)
    return module


def add_card(board, column, slug, blockers=()):
    card_id = '2026-10-14-' + slug
    directory = board.BOARD / column / card_id
    directory.mkdir()
    (directory / 'card.md').write_text(
        f'---\ntitle: {slug}\narea: engine\npriority: P1\nassignee:\n'
        f'blocked-by: [{", ".join(blockers)}]\n---\n\n- [x] Receipt recorded. [receipt](https://example.invalid/report)\n')
    (directory / 'comments.md').write_text('# comments\n')
    return directory


def test_dependencies_can_point_to_cards_in_later_columns(board):
    add_card(board, 'ready', 'dependent', ['2026-10-14-completed'])
    add_card(board, 'done', 'completed')
    assert not board.validate_board()


def test_missing_dependency_is_rejected(board):
    add_card(board, 'ready', 'dependent', ['2026-10-14-missing'])
    assert any(p.level == 'ERROR' and 'not found' in p.message for p in board.validate_board())


def test_commit_chains_add_and_commit_with_only_named_paths(board, monkeypatch):
    path = 'tasks/ready/2026-10-14-example'
    (board.REPO_ROOT / path).mkdir()
    calls = []
    monkeypatch.setattr(board, '_repo_preflight', lambda: None)
    monkeypatch.setattr(board, '_git', lambda *args: subprocess.CompletedProcess(args, 0, 'abc123' if args[0] == 'rev-parse' else '', ''))

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, '', '')

    monkeypatch.setattr(board.subprocess, 'run', run)
    message = 'chore: literal $(touch should-not-run)'
    assert board._commit_card([path], message) == (0, 'abc123')
    command, kwargs = calls[0]
    add, commit = command.split(' && ')
    assert shlex.split(add)[-2:] == ['--', path]
    assert shlex.split(commit)[-4:] == ['-m', message, '--', path]
    assert '--only' in shlex.split(commit)
    assert kwargs['shell'] is True


def test_claim_commits_the_move_before_editing_metadata(board, monkeypatch):
    source = add_card(board, 'ready', 'example')
    destination = board.BOARD / 'active' / source.name
    commits = []
    monkeypatch.setattr(board, '_repo_preflight', lambda: None)

    def git(*args):
        if args[0] == 'mv':
            (board.REPO_ROOT / args[1]).rename(board.REPO_ROOT / args[2])
        return subprocess.CompletedProcess(args, 0, 'tracked' if args[0] == 'ls-files' else '', '')

    def commit(paths, _message):
        commits.append((paths, (destination / 'card.md').read_text(), (destination / 'comments.md').read_text()))
        return 0, 'abc123'

    monkeypatch.setattr(board, '_git', git)
    monkeypatch.setattr(board, '_commit_card', commit)
    assert board.main(['claim', source.name, '--as', 'test-agent']) == 0
    assert len(commits) == 2
    assert len(commits[0][0]) == 2 and 'assignee:\n' in commits[0][1]
    assert 'claim:' not in commits[0][2]
    assert len(commits[1][0]) == 1 and 'assignee: test-agent' in commits[1][1]
    assert 'claim:' in commits[1][2]


def test_claim_does_not_move_or_commit_a_dirty_card(board, monkeypatch):
    source = add_card(board, 'ready', 'dirty')
    calls = []
    monkeypatch.setattr(board, '_repo_preflight', lambda: None)

    def git(*args):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, ' M card.md' if args[0] == 'status' else 'tracked', '')

    monkeypatch.setattr(board, '_git', git)
    assert board.main(['claim', source.name, '--as', 'test-agent']) == 1
    assert source.is_dir() and not any(args[0] == 'mv' for args in calls)


@pytest.mark.parametrize("column", ["review", "done"])
def test_completed_checklists_require_evidence(board, column):
    card = add_card(board, column, 'completed')
    path = card / 'card.md'
    path.write_text(path.read_text().replace(
        '- [x] Receipt recorded. [receipt](https://example.invalid/report)',
        '- [x] Historical result.'))
    assert any(p.level == 'ERROR' and 'evidence link' in p.message for p in board.validate_board())
    path.write_text(path.read_text().replace(
        'Historical result.', 'Historical result. [tests](../../../tests/test_tasks_board.py)'))
    assert not board.validate_board()


def test_comment_refuses_dirty_card_without_appending(board, monkeypatch):
    card = add_card(board, 'ready', 'dirty-comments')
    before = (card / 'comments.md').read_bytes()
    monkeypatch.setattr(board, '_repo_preflight', lambda: None)
    monkeypatch.setattr(board, '_git', lambda *args: subprocess.CompletedProcess(args, 0, ' M card.md', ''))
    assert board.main(['comment', card.name, '-m', 'Do not commit foreign changes.']) == 1
    assert (card / 'comments.md').read_bytes() == before
