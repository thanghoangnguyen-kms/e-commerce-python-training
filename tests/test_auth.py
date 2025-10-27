"""Unit tests for AuthService business logic."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.services.auth_service import AuthService


class TestAuthService:
    """Test suite for AuthService."""

    @pytest.mark.asyncio
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.hash_password')
    @patch('app.services.auth_service.create_token')
    async def test_signup_user_success(self, mock_create_token, mock_hash_password, mock_user_model, mock_user):
        """Test successful user signup."""
        # Setup
        mock_user_model.find_one = AsyncMock(return_value=None)
        mock_hash_password.return_value = "hashed_password"
        mock_create_token.return_value = "test_token"

        mock_user_instance = MagicMock()
        mock_user_instance.id = "507f1f77bcf86cd799439012"
        mock_user_instance.role = "user"
        mock_user_instance.insert = AsyncMock()
        mock_user_model.return_value = mock_user_instance

        # Execute
        result = await AuthService.signup_user("newuser@example.com", "password123")

        # Assert
        assert result["access_token"] == "test_token"
        assert result["token_type"] == "bearer"
        mock_user_model.find_one.assert_called_once()
        mock_hash_password.assert_called_once_with("password123")
        mock_user_instance.insert.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.auth_service.User')
    async def test_signup_user_email_already_exists(self, mock_user_model, mock_user):
        """Test signup with already registered email."""
        # Setup
        mock_user_model.find_one = AsyncMock(return_value=mock_user)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.signup_user("test@example.com", "password123")

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Email already registered"

    @pytest.mark.asyncio
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.verify_password')
    @patch('app.services.auth_service.create_token')
    async def test_login_user_success(self, mock_create_token, mock_verify_password, mock_user_model, mock_user):
        """Test successful user login."""
        # Setup
        mock_user_model.find_one = AsyncMock(return_value=mock_user)
        mock_verify_password.return_value = True
        mock_create_token.return_value = "test_token"
        mock_user.id = "507f1f77bcf86cd799439012"
        mock_user.role = "user"

        # Execute
        result = await AuthService.login_user("test@example.com", "password123")

        # Assert
        assert result["access_token"] == "test_token"
        assert result["token_type"] == "bearer"
        mock_verify_password.assert_called_once_with("password123", mock_user.hashed_password)

    @pytest.mark.asyncio
    @patch('app.services.auth_service.User')
    async def test_login_user_not_found(self, mock_user_model):
        """Test login with non-existent user."""
        # Setup
        mock_user_model.find_one = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.login_user("notfound@example.com", "password123")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid credentials"

    @pytest.mark.asyncio
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.verify_password')
    async def test_login_user_wrong_password(self, mock_verify_password, mock_user_model, mock_user):
        """Test login with incorrect password."""
        # Setup
        mock_user_model.find_one = AsyncMock(return_value=mock_user)
        mock_verify_password.return_value = False

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.login_user("test@example.com", "wrongpassword")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid credentials"

    @pytest.mark.asyncio
    @patch('app.services.auth_service.User')
    async def test_get_user_by_id_success(self, mock_user_model, mock_user):
        """Test successfully retrieving user by ID."""
        # Setup
        mock_user_model.get = AsyncMock(return_value=mock_user)

        # Execute
        result = await AuthService.get_user_by_id("507f1f77bcf86cd799439012")

        # Assert
        assert result == mock_user
        mock_user_model.get.assert_called_once_with("507f1f77bcf86cd799439012")

    @pytest.mark.asyncio
    @patch('app.services.auth_service.User')
    async def test_get_user_by_id_not_found(self, mock_user_model):
        """Test retrieving non-existent user by ID."""
        # Setup
        mock_user_model.get = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.get_user_by_id("507f1f77bcf86cd799439012")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"

    @pytest.mark.asyncio
    @patch('app.services.auth_service.User')
    async def test_promote_user_to_admin_success(self, mock_user_model, mock_user):
        """Test successfully promoting user to admin."""
        # Setup
        mock_user.role = "user"
        mock_user.save = AsyncMock()
        mock_user_model.find_one = AsyncMock(return_value=mock_user)

        # Execute
        result = await AuthService.promote_user_to_admin("test@example.com")

        # Assert
        assert result.role == "admin"
        mock_user.save.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.auth_service.User')
    async def test_promote_user_to_admin_user_not_found(self, mock_user_model):
        """Test promoting non-existent user to admin."""
        # Setup
        mock_user_model.find_one = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.promote_user_to_admin("notfound@example.com")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"

    @pytest.mark.asyncio
    @patch('app.services.auth_service.User')
    async def test_promote_user_to_admin_already_admin(self, mock_user_model, mock_admin):
        """Test promoting user who is already admin."""
        # Setup
        mock_user_model.find_one = AsyncMock(return_value=mock_admin)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.promote_user_to_admin("admin@example.com")

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "User is already an admin"

