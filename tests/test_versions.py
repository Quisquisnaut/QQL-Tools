from qql_tools import (
    QQL_CANONICAL_EXERCISE_MODELS,
    QQL_COURSE_MODEL_VERSION,
    QQL_PACKAGE_FORMAT_VERSION,
)


def test_verified_qql_versions_and_primitives() -> None:
    assert QQL_COURSE_MODEL_VERSION == 11
    assert QQL_PACKAGE_FORMAT_VERSION == 1
    assert QQL_CANONICAL_EXERCISE_MODELS == (
        "select",
        "input",
        "arrange",
        "match",
        "presentation",
    )
