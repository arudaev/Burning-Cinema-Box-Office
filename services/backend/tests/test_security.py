from burningbackend.app.core.security import get_password_hash, verify_password


def test_password_hash_is_not_plaintext():
    hashed = get_password_hash("hunter2")
    assert hashed != "hunter2"


def test_correct_password_verifies():
    hashed = get_password_hash("hunter2")
    assert verify_password("hunter2", hashed) is True


def test_wrong_password_does_not_verify():
    hashed = get_password_hash("hunter2")
    assert verify_password("wrong", hashed) is False


def test_two_hashes_of_same_password_differ():
    # bcrypt uses a random salt — same input must not produce identical hashes
    a = get_password_hash("same")
    b = get_password_hash("same")
    assert a != b
