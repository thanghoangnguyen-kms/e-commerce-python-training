"""
Unit tests for AuthService.

- Signup: success and duplicate email
- Login: success and invalid credentials
- Get user by ID
- Promote to admin
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from app.services.auth_service import AuthService


class TestAuthServiceSignup:
    """Test cases for user signup"""

    @pytest.mark.asyncio
    async def test_signup_success(self, mock_user_factory):
        """Should create user and return token"""
        # Arrange
        new_user = mock_user_factory(email="new@example.com")

        with patch("app.services.auth_service.User") as MockUser, \
             patch("app.services.auth_service.hash_password") as mock_hash, \
             patch("app.services.auth_service.create_token") as mock_token:

            MockUser.find_one = AsyncMock(return_value=None)
            MockUser.return_value = new_user
            mock_hash.return_value = "hashed"
            mock_token.return_value = "token_123"

            # Act
            result = await AuthService.signup_user("new@example.com", "pass123")

            # Assert
            assert result["access_token"] == "token_123"
            assert result["token_type"] == "bearer"
            new_user.insert.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_signup_fails_duplicate_email(self, mock_user_factory):
        """Should raise 400 when email already exists"""
        # Arrange
        with patch("app.services.auth_service.User") as MockUser:
            MockUser.find_one = AsyncMock(return_value=mock_user_factory())

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await AuthService.signup_user("existing@example.com", "pass")

            assert exc.value.status_code == 400


class TestAuthServiceLogin:
    """Test cases for user login"""

    @pytest.mark.asyncio
    async def test_login_success(self, mock_user_factory):
        """Should return token with valid credentials"""
        # Arrange
        user = mock_user_factory(email="user@test.com", hashed_password="hashed")

        with patch("app.services.auth_service.User") as MockUser, \
             patch("app.services.auth_service.verify_password", return_value=True), \
             patch("app.services.auth_service.create_token", return_value="token_456"):

            MockUser.find_one = AsyncMock(return_value=user)

            # Act
            result = await AuthService.login_user("user@test.com", "password")

            # Assert
            assert result["access_token"] == "token_456"
            assert result["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_fails_invalid_credentials(self, mock_user_factory):
        """Should raise 401 for wrong email or password"""
        # Arrange - test with no user found
        with patch("app.services.auth_service.User") as MockUser:
            MockUser.find_one = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await AuthService.login_user("wrong@test.com", "pass")

            assert exc.value.status_code == 401


class TestAuthServiceGetUserById:
    """Test cases for getting user by ID"""

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, mock_user_factory):
        """Should return user when found"""
        # Arrange
        user = mock_user_factory(id="user_123")

        with patch("app.services.auth_service.User") as MockUser:
            MockUser.get = AsyncMock(return_value=user)

            # Act
            result = await AuthService.get_user_by_id("user_123")

            # Assert
            assert result == user

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Should raise 404 when user doesn't exist"""
        # Arrange
        with patch("app.services.auth_service.User") as MockUser:
            MockUser.get = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await AuthService.get_user_by_id("nonexistent")

            assert exc.value.status_code == 404


class TestAuthServicePromoteToAdmin:
    """Test cases for promoting users to admin"""

    @pytest.mark.asyncio
    async def test_promote_to_admin_success(self, mock_user_factory):
        """Should update role and save"""
        # Arrange
        user = mock_user_factory(role="user")

        with patch("app.services.auth_service.User") as MockUser:
            MockUser.find_one = AsyncMock(return_value=user)

            # Act
            result = await AuthService.promote_user_to_admin("user@test.com")

            # Assert
            assert result.role == "admin"
            user.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_promote_to_admin_already_admin(self, mock_user_factory):
        """Should raise 400 if already admin"""
        # Arrange
        user = mock_user_factory(role="admin")

        with patch("app.services.auth_service.User") as MockUser:
            MockUser.find_one = AsyncMock(return_value=user)

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await AuthService.promote_user_to_admin("admin@test.com")

            assert exc.value.status_code == 400

