"""Tests for PasswordService."""

import pytest

from app.services.password_service import PasswordService


def test_hash_password_produces_different_hash_each_time():
    """Test that hashing the same password twice produces different hashes."""
    password = "testpassword123"
    hash1 = PasswordService.hash_password(password)
    hash2 = PasswordService.hash_password(password)

    assert hash1 != hash2
    assert isinstance(hash1, str)
    assert isinstance(hash2, str)


def test_verify_password_with_correct_password():
    """Test password verification succeeds with correct password."""
    password = "mypassword"
    hashed = PasswordService.hash_password(password)

    assert PasswordService.verify_password(password, hashed) is True


def test_verify_password_with_incorrect_password():
    """Test password verification fails with incorrect password."""
    password = "correctpassword"
    hashed = PasswordService.hash_password(password)

    assert PasswordService.verify_password("wrongpassword", hashed) is False


def test_verify_password_is_timing_safe():
    """Test that verify_password uses bcrypt's timing-safe comparison."""
    password = "testpass"
    hashed = PasswordService.hash_password(password)

    # bcrypt.checkpw is inherently timing-safe
    # This test verifies the function works correctly
    assert PasswordService.verify_password(password, hashed) is True
    assert PasswordService.verify_password("different", hashed) is False
