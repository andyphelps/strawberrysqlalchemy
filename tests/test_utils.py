import pytest

from strawchemy.utils import snake_it


class TestUtils:

    @pytest.mark.parametrize(argnames=["value", "expected"],
                             argvalues=[
                                 ("", ""),
                                 ("Word", "word"),
                                 ("ThreeWordValue", "three_word_value"),
                                 ("EndsWithCaP", "ends_with_ca_p"),
                                 ("already_snaked_unaffected", "already_snaked_unaffected"),
                                 ("Capitalised_Snaked_Lowered", "capitalised_snaked_lowered")
                             ],
                             ids=[
                                 "When empty string then empty string",
                                 "When single word then lower cased",
                                 "When three words then snake cased",
                                 "When ends with capital then snake cased correctly",
                                 "Already snake cased then unaffected",
                                 "Capitalised snake cased then lowered only",
                             ])
    def test_snake_it(self, value: str, expected: str) -> None:
        assert snake_it(value) == expected
