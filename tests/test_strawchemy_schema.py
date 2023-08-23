import pytest
from sqlalchemy import create_engine, Engine, CursorResult, text

from strawberrysqlalchemy.strawchemy import StrawchemySchema
from test_models import SimpleModel, NestedModel


@pytest.fixture
def db() -> Engine:
    engine = create_engine("sqlite://", echo=True)
    yield engine
    engine.dispose()


class TestStrawchemySchema:

    def test_when_missing_queriables_then_type_error_thrown(self, db: Engine) -> None:
        with pytest.raises(TypeError) as err:
            StrawchemySchema(queriable_types=[], engine=db)

        assert err.value.args == ("StrawchemySchema requires at least one model type in the queriable argument",)

    def test_when_valid_queriables_then_can_get_queriables(self, db: Engine) -> None:
        ss = StrawchemySchema(queriable_types=[SimpleModel], engine=db)

        assert {model.name for model in ss.model_types} == {"SimpleModel"}

    def test_when_queriables_list_of_nontypes_then_type_error_raised(self, db: Engine) -> None:
        with pytest.raises(TypeError) as err:
            ss = StrawchemySchema(queriable_types=[1, 2], engine=db)  # noqa

        assert err.value.args == ("StrawchemySchema requires at least one model type in the queriable argument",)

    def test_when_nested_queriables_then_all_types_are_found_and_non_classes_are_ignored(self, db: Engine) -> None:
        ss = StrawchemySchema(queriable_types=[NestedModel, 1, 2], engine=db)

        assert {model.name for model in ss.model_types} == {"NestedModel", "NestedModelA", "NestedModelA1"}

    def test_when_nested_queriables_then_graphql_schema_is_correct(self, db: Engine) -> None:
        schema = StrawchemySchema(queriable_types=[NestedModel], engine=db).as_str()

        assert "type NestedModel {" in schema
        assert "type NestedModelA {" in schema
        assert "type NestedModelA1 {" in schema

    def test_when_simple_model_then_table_created_correctly(self, db: Engine) -> None:
        schema = StrawchemySchema(queriable_types=[SimpleModel], engine=db)

        with schema.engine.connect() as connection:
            result: CursorResult = connection.execute(
                text("pragma table_info(simple_model)")
            )

            assert {row[1:] for row in result.all()} == {
                ('id', 'INTEGER', 1, None, 1),
                ('root_value_1', 'INTEGER', 0, None, 0),
                ('wibble', 'VARCHAR', 0, None, 0)
            }
