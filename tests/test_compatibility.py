from qql_tools.interoperability.compatibility import (
    CompatibilityAssessment,
    CompatibilityResult,
)


def test_compatibility_result_representation() -> None:
    assessment = CompatibilityAssessment(
        feature="Timed response",
        qql_capability="unavailable",
        result=CompatibilityResult.UNSUPPORTED,
        loss="timing behavior",
    )

    assert assessment.result == CompatibilityResult.UNSUPPORTED
    assert assessment.loss == "timing behavior"
