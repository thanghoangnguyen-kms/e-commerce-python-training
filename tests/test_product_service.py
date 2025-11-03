"""
Unit tests for ProductService.

- List products (basic, with search)
- Get by slug/ID
- Create product with validations
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository


class TestProductService:
    """Test cases for product operations"""

    @pytest.mark.asyncio
    async def test_list_products_basic(self, mock_product_factory):
        """Should return list of products as Product model objects"""
        # Arrange
        products = [mock_product_factory(name="Product 1"), mock_product_factory(name="Product 2")]

        mock_repo = Mock(spec=ProductRepository)
        mock_repo.search_products = AsyncMock(return_value=products)

        service = ProductService(product_repository=mock_repo)

        # Act
        result = await service.list_products()

        # Assert
        assert len(result) == 2
        assert isinstance(result, list)
        assert result[0].name == "Product 1"
        assert hasattr(result[0], 'id')  # MongoDB id field is included
        mock_repo.search_products.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_products_with_search(self, mock_product_factory):
        """Should filter by search query and return Product model objects"""
        # Arrange
        products = [mock_product_factory(category="Electronics")]
        
        mock_repo = Mock(spec=ProductRepository)
        mock_repo.search_products = AsyncMock(return_value=products)
        
        service = ProductService(product_repository=mock_repo)

        # Act
        result = await service.list_products(search_query="electronics")

        # Assert
        assert len(result) == 1
        assert result[0].category == "Electronics"
        assert hasattr(result[0], 'id')  # MongoDB id field is included
        mock_repo.search_products.assert_called_once_with("electronics", 0, 20)

    @pytest.mark.asyncio
    async def test_get_product_by_slug_success(self, mock_product_factory):
        """Should return product as Product model object by slug"""
        # Arrange
        product = mock_product_factory(slug="test-product", is_active=True)
        
        mock_repo = Mock(spec=ProductRepository)
        mock_repo.find_by_slug = AsyncMock(return_value=product)
        
        service = ProductService(product_repository=mock_repo)

        # Act
        result = await service.get_product_by_slug("test-product")

        # Assert
        assert result.slug == "test-product"
        assert hasattr(result, 'id')  # MongoDB id field is included
        mock_repo.find_by_slug.assert_called_once_with("test-product", active_only=True)

    @pytest.mark.asyncio
    async def test_get_product_by_slug_not_found(self):
        """Should raise 404 when slug not found"""
        # Arrange
        mock_repo = Mock(spec=ProductRepository)
        mock_repo.find_by_slug = AsyncMock(return_value=None)
        
        service = ProductService(product_repository=mock_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.get_product_by_slug("nonexistent")

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_product_by_id_success(self, mock_product_factory):
        """Should return product by ID"""
        # Arrange
        product = mock_product_factory(id="prod_123")
        
        mock_repo = Mock(spec=ProductRepository)
        mock_repo.get_by_id = AsyncMock(return_value=product)
        
        service = ProductService(product_repository=mock_repo)

        # Act
        result = await service.get_product_by_id("prod_123")

        # Assert
        assert result == product
        mock_repo.get_by_id.assert_called_once_with("prod_123")

    @pytest.mark.asyncio
    async def test_create_product_success(self, mock_product_factory):
        """Should create new product"""
        # Arrange
        new_product = mock_product_factory(slug="new-product")
        
        mock_repo = Mock(spec=ProductRepository)
        mock_repo.find_by_slug = AsyncMock(return_value=None)
        mock_repo.find_by_product_id = AsyncMock(return_value=None)
        mock_repo.create = AsyncMock(return_value=new_product)
        
        service = ProductService(product_repository=mock_repo)

        # Mock Product model constructor
        with patch("app.services.product_service.Product", return_value=new_product):
            # Act
            result = await service.create_product(
                product_id=1,
                name="New Product",
                slug="new-product",
                description=None,
                price=99.99,
                image=None,
                inventory=10,
                category=None,
                is_active=True
            )

        # Assert
        assert result == new_product
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_product_fails_duplicate_slug(self, mock_product_factory):
        """Should raise 400 for duplicate slug"""
        # Arrange
        existing_product = mock_product_factory()
        
        mock_repo = Mock(spec=ProductRepository)
        mock_repo.find_by_slug = AsyncMock(return_value=existing_product)
        
        service = ProductService(product_repository=mock_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.create_product(
                product_id=1, name="Test", slug="existing-slug",
                description=None, price=99.99, image=None,
                inventory=10, category=None, is_active=True
            )

        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_product_fails_duplicate_product_id(self, mock_product_factory):
        """Should raise 400 for duplicate product_id"""
        # Arrange
        existing_product = mock_product_factory()
        
        mock_repo = Mock(spec=ProductRepository)
        mock_repo.find_by_slug = AsyncMock(return_value=None)
        mock_repo.find_by_product_id = AsyncMock(return_value=existing_product)
        
        service = ProductService(product_repository=mock_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.create_product(
                product_id=1, name="Test", slug="new-slug",
                description=None, price=99.99, image=None,
                inventory=10, category=None, is_active=True
            )

        assert exc.value.status_code == 400
