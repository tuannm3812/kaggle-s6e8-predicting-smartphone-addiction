from pathlib import Path

import pandas as pd
import pytest

from scripts.verify_submission import validate_submission


def write_contract_files(tmp_path: Path) -> tuple[Path, Path, Path]:
    test = pd.DataFrame({"id": [10, 11, 12], "feature": [1, 2, 3]})
    sample = pd.DataFrame({"id": [10, 11, 12], "addicted_label": [0.5] * 3})
    submission = pd.DataFrame(
        {"id": [10, 11, 12], "addicted_label": [0.1, 0.7, 0.9]}
    )
    test_path = tmp_path / "test.csv"
    sample_path = tmp_path / "sample_submission.csv"
    submission_path = tmp_path / "submission.csv"
    test.to_csv(test_path, index=False)
    sample.to_csv(sample_path, index=False)
    submission.to_csv(submission_path, index=False)
    return submission_path, test_path, sample_path


def test_valid_submission_passes(tmp_path: Path) -> None:
    submission, test, sample = write_contract_files(tmp_path)
    result = validate_submission(submission, test, sample)
    assert result["rows"] == 3
    assert result["unique_predictions"] == 3


@pytest.mark.parametrize("bad_value", [-0.1, 1.1, float("nan")])
def test_invalid_probability_fails(tmp_path: Path, bad_value: float) -> None:
    submission, test, sample = write_contract_files(tmp_path)
    frame = pd.read_csv(submission)
    frame.loc[0, "addicted_label"] = bad_value
    frame.to_csv(submission, index=False)
    with pytest.raises(ValueError):
        validate_submission(submission, test, sample)


def test_id_order_mismatch_fails(tmp_path: Path) -> None:
    submission, test, sample = write_contract_files(tmp_path)
    frame = pd.read_csv(submission).iloc[::-1]
    frame.to_csv(submission, index=False)
    with pytest.raises(ValueError):
        validate_submission(submission, test, sample)


def test_schema_mismatch_fails(tmp_path: Path) -> None:
    submission, test, sample = write_contract_files(tmp_path)
    frame = pd.read_csv(submission).rename(columns={"addicted_label": "prediction"})
    frame.to_csv(submission, index=False)
    with pytest.raises(ValueError):
        validate_submission(submission, test, sample)


def test_row_count_mismatch_fails(tmp_path: Path) -> None:
    submission, test, sample = write_contract_files(tmp_path)
    frame = pd.read_csv(submission).iloc[:-1]
    frame.to_csv(submission, index=False)
    with pytest.raises(ValueError):
        validate_submission(submission, test, sample)
