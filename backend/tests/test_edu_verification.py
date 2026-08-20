from app.edu_verification import is_edu_email, extract_domain


def test_accepts_edu_domain():
    assert is_edu_email("paul@williams.edu") is True


def test_rejects_non_edu_domain():
    assert is_edu_email("paul@gmail.com") is False


def test_is_case_insensitive():
    assert is_edu_email("Paul@Williams.EDU") is True


def test_rejects_edu_lookalike():
    assert is_edu_email("paul@williams.edu.fake.com") is False


def test_extract_domain_strips_and_lowercases():
    assert extract_domain("  Paul@Williams.EDU  ") == "williams.edu"
