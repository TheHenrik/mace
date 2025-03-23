import uuid
from pymace.test.perftest import performance_report


def dummy_to_profile():
    # A simple function to profile.
    sum(x * x for x in range(1000))


def test_performance_report_creates_file(tmp_path):
    # Generate a random file name in the temporary directory.
    file_name = f"profile_{uuid.uuid4().hex}.prof"
    file_path = tmp_path / file_name

    # Ensure the file does not exist before running the test.
    if file_path.exists():
        file_path.unlink()

    # Run the performance_report function.
    ret = performance_report(dummy_to_profile, save_path=str(file_path))
    
    # performance_report should return None.
    assert ret is None

    # Check that the profiling report file was created and is not empty.
    assert file_path.exists()
    assert file_path.stat().st_size > 0

    # Clean up by deleting the file after the test.
    file_path.unlink()