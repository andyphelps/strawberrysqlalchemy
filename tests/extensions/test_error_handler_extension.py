from typing import Any
from unittest.mock import Mock

import pytest

from strawchemy.extensions import ErrorHandlerExtension
from strawchemy.extensions.error_handler import StrawchemyError


class TestErrorHandlerExtension:

    def test_when_no_error_raised_then_value_returned(self) -> None:
        mock_execution_context: Mock = Mock(name="ExecutionContextMock")
        error_handler = ErrorHandlerExtension(execution_context=mock_execution_context)

        response = error_handler.resolve(lambda a, b, c, d: 23, None, None, None, None)

        assert response == 23

    def test_when_error_raised_then_generic_message_raised(self) -> None:
        mock_execution_context: Mock = Mock(name="ExecutionContextMock")
        error_handler = ErrorHandlerExtension(execution_context=mock_execution_context)

        def next_func(a: Any, b: Any, c: Any, d: Any) -> Any:
            raise AttributeError("Some message")

        with pytest.raises(StrawchemyError) as se:
            error_handler.resolve(next_func, None, None, None, None)

        assert se.value.args[0] == "An unhandled error occurred"

    def test_when_strawchemy_error_raised_then_specific_message_raised(self) -> None:
        mock_execution_context: Mock = Mock(name="ExecutionContextMock")
        error_handler = ErrorHandlerExtension(execution_context=mock_execution_context)

        def next_func(a: Any, b: Any, c: Any, d: Any) -> Any:
            raise StrawchemyError("Some strawchemy message")

        with pytest.raises(StrawchemyError) as se:
            error_handler.resolve(next_func, None, None, None, None)

        assert se.value.args[0] == "Some strawchemy message"
