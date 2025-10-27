"""Unit tests for ProductService business logic."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from bson import ObjectId

from app.services.product_service import ProductService


class TestProductService:
    """Test suite for ProductService."""

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_list_products_without_search(self, mock_product_model, mock_product):
        """Test listing products without search query."""
        # Setup
        mock_find = MagicMock()
        mock_find.skip.return_value.limit.return_value.to_list = AsyncMock(
            return_value=[mock_product]
        )
        mock_product_model.find.return_value = mock_find

        # Execute
        result = await ProductService.list_products(None, 0, 20)

        # Assert
        mock_product_model.find.assert_called_once_with({})
        assert len(result) == 1
        assert result[0] == mock_product

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_list_products_with_search(self, mock_product_model, mock_product):
        """Test listing products with search query."""
        # Setup
        mock_find = MagicMock()
        mock_find.skip.return_value.limit.return_value.to_list = AsyncMock(
            return_value=[mock_product]
        )
        mock_product_model.find.return_value = mock_find

        # Execute
        result = await ProductService.list_products("laptop", 0, 20)

        # Assert
        expected_query = {
            "$or": [
                {"name": {"$regex": "laptop", "$options": "i"}},
                {"category": {"$regex": "laptop", "$options": "i"}}
            ]
        }
        mock_product_model.find.assert_called_once_with(expected_query)
        assert len(result) == 1

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_list_products_with_pagination(self, mock_product_model):
        """Test listing products with pagination parameters."""
        # Setup
        mock_skip = MagicMock()
        mock_limit = MagicMock()
        mock_skip.limit.return_value = mock_limit
        mock_limit.to_list = AsyncMock(return_value=[])

        mock_find = MagicMock()
        mock_find.skip.return_value = mock_skip
        mock_product_model.find.return_value = mock_find

        # Execute
        await ProductService.list_products(None, 10, 5)

        # Assert
        mock_find.skip.assert_called_once_with(10)
        mock_skip.limit.assert_called_once_with(5)

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_get_product_by_slug_success(self, mock_product_model, mock_product):
        """Test successfully retrieving a product by slug."""
        # Setup
        mock_product_model.find_one = AsyncMock(return_value=mock_product)

        # Execute
        result = await ProductService.get_product_by_slug("test-product")

        # Assert
        assert result == mock_product
        mock_product_model.find_one.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_get_product_by_slug_not_found(self, mock_product_model):
        """Test retrieving a non-existent product by slug."""
        # Setup
        mock_product_model.find_one = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await ProductService.get_product_by_slug("non-existent")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_get_product_by_id_success(self, mock_product_model, mock_product):
        """Test successfully retrieving a product by ID."""
        # Setup
        mock_product_model.get = AsyncMock(return_value=mock_product)

        # Execute
        result = await ProductService.get_product_by_id("507f1f77bcf86cd799439011")

        # Assert
        assert result == mock_product
        mock_product_model.get.assert_called_once_with("507f1f77bcf86cd799439011")

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_get_product_by_id_not_found(self, mock_product_model):
        """Test retrieving a non-existent product by ID."""
        # Setup
        mock_product_model.get = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await ProductService.get_product_by_id("507f1f77bcf86cd799439011")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_create_product_success(self, mock_product_model):
        """Test successfully creating a new product."""
        # Setup
        mock_product_model.find_one = AsyncMock(return_value=None)
        mock_product_instance = MagicMock()
        mock_product_instance.insert = AsyncMock()
        mock_product_model.return_value = mock_product_instance

        # Execute
        result = await ProductService.create_product(
            product_id=1,
            name="New Product",
            slug="new-product",
            description="A new product",
            price=99.99,
            image="http://example.com/image.jpg",
            inventory=10,
            category="Electronics",
            is_active=True
        )

        # Assert
        assert result == mock_product_instance
        mock_product_instance.insert.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_create_product_duplicate_slug(self, mock_product_model, mock_product):
        """Test creating a product with duplicate slug."""
        # Setup - first call returns existing product (slug check), second returns None (product_id check)
        mock_product_model.find_one = AsyncMock(side_effect=[mock_product, None])

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await ProductService.create_product(
                product_id=2,
                name="New Product",
                slug="test-product",  # Duplicate slug
                description="A new product",
                price=99.99,
                image="http://example.com/image.jpg",
                inventory=10,
                category="Electronics",
                is_active=True
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Slug already exists"

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_create_product_duplicate_product_id(self, mock_product_model, mock_product):
        """Test creating a product with duplicate product_id."""
        # Setup - first call returns None (slug check), second returns existing product (product_id check)
        mock_product_model.find_one = AsyncMock(side_effect=[None, mock_product])

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await ProductService.create_product(
                product_id=1,  # Duplicate product_id
                name="New Product",
                slug="new-product",
                description="A new product",
                price=99.99,
                image="http://example.com/image.jpg",
                inventory=10,
                category="Electronics",
                is_active=True
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Product ID already exists"

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_update_product_success(self, mock_product_model, mock_product):
        """Test successfully updating a product."""
        # Setup
        mock_product.save = AsyncMock()
        mock_product.product_id = 1
        mock_product_model.get = AsyncMock(return_value=mock_product)
        mock_product_model.find_one = AsyncMock(return_value=None)

        # Execute
        result = await ProductService.update_product(
            product_id="507f1f77bcf86cd799439011",
            new_product_id=1,  # Same ID
            name="Updated Product",
            slug="updated-product",
            description="Updated description",
            price=149.99,
            image="http://example.com/new-image.jpg",
            inventory=20,
            category="Tech",
            is_active=True
        )

        # Assert
        assert result.name == "Updated Product"
        assert result.price == 149.99
        mock_product.save.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_update_product_not_found(self, mock_product_model):
        """Test updating a non-existent product."""
        # Setup
        mock_product_model.get = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await ProductService.update_product(
                product_id="507f1f77bcf86cd799439011",
                new_product_id=1,
                name="Updated Product",
                slug="updated-product",
                description="Updated description",
                price=149.99,
                image="http://example.com/new-image.jpg",
                inventory=20,
                category="Tech",
                is_active=True
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not found"

    @pytest.mark.asyncio
    @patch('app.services.product_service.Product')
    async def test_update_product_duplicate_product_id(self, mock_product_model, mock_product):
        """Test updating a product with duplicate product_id."""
        # Setup
        mock_product.product_id = 1
        mock_product_model.get = AsyncMock(return_value=mock_product)

        # Mock another product with the new ID already exists
        other_product = MagicMock()
        other_product.product_id = 2
        mock_product_model.find_one = AsyncMock(return_value=other_product)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await ProductService.update_product(
                product_id="507f1f77bcf86cd799439011",
                new_product_id=2,  # Trying to change to ID that already exists
                name="Updated Product",
                slug="updated-product",
                description="Updated description",
                price=149.99,
                image="http://example.com/new-image.jpg",
                inventory=20,
                category="Tech",
                is_active=True
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Product ID already exists"

