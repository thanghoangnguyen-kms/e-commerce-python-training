"""
Unit tests for AuthService.

- Signup: success and duplicate email
- Login: success and invalid credentials
- Get user by ID
- Promote to admin
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository


class TestAuthServiceSignup:
    """Test cases for user signup"""

    @pytest.mark.asyncio
    async def test_signup_success(self, mock_user_factory):
        """Should create user and return token"""
        # Arrange
        new_user = mock_user_factory(email="new@example.com")
        
        # Mock repository
        mock_repo = Mock(spec=UserRepository)
        mock_repo.find_by_email = AsyncMock(return_value=None)
        mock_repo.create = AsyncMock(return_value=new_user)
        
        # Instantiate service with mocked repository
        service = AuthService(user_repository=mock_repo)
        
        # Mock User model constructor
        with patch("app.services.auth_service.User", return_value=new_user):
            # Act
            result = await service.signup_user("new@example.com", "pass123")

        # Assert
        assert result["access_token"] is not None
        assert result["token_type"] == "bearer"
        mock_repo.find_by_email.assert_called_once_with("new@example.com")
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_signup_fails_duplicate_email(self, mock_user_factory):
        """Should raise 400 when email already exists"""
        # Arrange
        existing_user = mock_user_factory()
        
        mock_repo = Mock(spec=UserRepository)
        mock_repo.find_by_email = AsyncMock(return_value=existing_user)
        
        service = AuthService(user_repository=mock_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.signup_user("existing@example.com", "pass")

        assert exc.value.status_code == 400
        assert "already registered" in str(exc.value.detail)


class TestAuthServiceLogin:
    """Test cases for user login"""

    @pytest.mark.asyncio
    async def test_login_success(self, mock_user_factory):
        """Should return token with valid credentials"""
        # Arrange - Create user with proper bcrypt hash
        import bcrypt
        hashed = bcrypt.hashpw("password".encode(), bcrypt.gensalt()).decode()
        user = mock_user_factory(email="user@test.com", hashed_password=hashed)
        
        mock_repo = Mock(spec=UserRepository)
        mock_repo.find_by_email = AsyncMock(return_value=user)
        
        service = AuthService(user_repository=mock_repo)

        # Act
        result = await service.login_user("user@test.com", "password")

        # Assert
        assert result["access_token"] is not None
        assert result["token_type"] == "bearer"
        mock_repo.find_by_email.assert_called_once_with("user@test.com")

    @pytest.mark.asyncio
    async def test_login_fails_invalid_credentials(self):
        """Should raise 401 for wrong email or password"""
        # Arrange - test with no user found
        mock_repo = Mock(spec=UserRepository)
        mock_repo.find_by_email = AsyncMock(return_value=None)
        
        service = AuthService(user_repository=mock_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.login_user("wrong@test.com", "pass")

        assert exc.value.status_code == 401


class TestAuthServiceGetUserById:
    """Test cases for getting user by ID"""

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, mock_user_factory):
        """Should return user when found"""
        # Arrange
        user = mock_user_factory(id="user_123")
        
        mock_repo = Mock(spec=UserRepository)
        mock_repo.get_by_id = AsyncMock(return_value=user)
        
        service = AuthService(user_repository=mock_repo)

        # Act
        result = await service.get_user_by_id("user_123")

        # Assert
        assert result == user
        mock_repo.get_by_id.assert_called_once_with("user_123")

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Should raise 404 when user doesn't exist"""
        # Arrange
        mock_repo = Mock(spec=UserRepository)
        mock_repo.get_by_id = AsyncMock(return_value=None)
        
        service = AuthService(user_repository=mock_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.get_user_by_id("nonexistent")

        assert exc.value.status_code == 404


class TestAuthServicePromoteToAdmin:
    """Test cases for promoting users to admin"""

    @pytest.mark.asyncio
    async def test_promote_to_admin_success(self, mock_user_factory):
        """Should update role and save"""
        # Arrange
        user = mock_user_factory(role="user")
        
        mock_repo = Mock(spec=UserRepository)
        mock_repo.find_by_email = AsyncMock(return_value=user)
        mock_repo.update = AsyncMock(return_value=user)
        
        service = AuthService(user_repository=mock_repo)

        # Act
        result = await service.promote_user_to_admin("user@test.com")

        # Assert
        assert result.role == "admin"
        mock_repo.find_by_email.assert_called_once_with("user@test.com")
        mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_promote_to_admin_already_admin(self, mock_user_factory):
        """Should raise 400 if already admin"""
        # Arrange
        user = mock_user_factory(role="admin")
        
        mock_repo = Mock(spec=UserRepository)
        mock_repo.find_by_email = AsyncMock(return_value=user)
        
        service = AuthService(user_repository=mock_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.promote_user_to_admin("admin@test.com")

        assert exc.value.status_code == 400
