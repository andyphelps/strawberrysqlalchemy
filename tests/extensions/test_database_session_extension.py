from unittest.mock import Mock, patch

import pytest

from strawchemy.extensions import DatabaseSessionExtension


class TestDatabaseSessionExtension:

    def test_when_initialised_without_sqlalchemy_engine_then_error_raised(self) -> None:
        with pytest.raises(AttributeError):
            mock_execution_context: Mock = Mock()
            mock_execution_context.schema = Mock(spec=[])
            DatabaseSessionExtension(execution_context=mock_execution_context)

    def test_when_initialised_with_none_sqlalchemy_engine_then_error_raised(self) -> None:
        with pytest.raises(AttributeError):
            mock_execution_context: Mock = Mock()
            mock_execution_context.schema = None
            DatabaseSessionExtension(execution_context=mock_execution_context)

    @patch("strawchemy.extensions.database_session.Session")
    def test_when_on_operation_called_context_contains_engine_and_commits(self, mock_session_cls: Mock) -> None:
        mock_engine = Mock(name="EngineMock")
        mock_execution_context: Mock = Mock(name="ExecutionContextMock")
        mock_session: Mock = Mock(name="SessionMock")

        mock_execution_context.context = {}
        mock_session_cls.return_value.__enter__.return_value = mock_session
        mock_session.get_bind.return_value = mock_engine

        mock_execution_context.schema.strawchemy_engine = mock_engine
        db_session_ext = DatabaseSessionExtension(execution_context=mock_execution_context)
        gen = db_session_ext.on_operation()
        next(gen)

        assert mock_execution_context.context["session"] == mock_session
        assert not mock_session.close.called

        next(gen, None)

        mock_session.close.assert_called_once()
