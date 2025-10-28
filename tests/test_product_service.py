"""
Unit tests for ProductService.

- List products (basic, with search)
- Get by slug/ID
- Create product with validations
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from app.services.product_service import ProductService
from tests.conftest import QueryChain


class TestProductService:
    """Test cases for product operations"""

    @pytest.mark.asyncio
    async def test_list_products_basic(self, mock_product_factory):
        """Should return list of products"""
        # Arrange
        products = [mock_product_factory(name="Product 1"), mock_product_factory(name="Product 2")]

        with patch("app.services.product_service.Product") as MockProduct:
            MockProduct.find = MagicMock(return_value=QueryChain(products))

            # Act
            result = await ProductService.list_products()

            # Assert
            assert len(result) == 2
            assert isinstance(result, list)
            assert isinstance(result[0], dict)  # Now returns dictionaries
            assert result[0]["name"] == "Product 1"

    @pytest.mark.asyncio
    async def test_list_products_with_search(self, mock_product_factory):
        """Should filter by search query"""
        # Arrange
        products = [mock_product_factory(category="Electronics")]

        with patch("app.services.product_service.Product") as MockProduct:
            MockProduct.find = MagicMock(return_value=QueryChain(products))

            # Act
            result = await ProductService.list_products(search_query="electronics")
            assert isinstance(result[0], dict)  # Now returns dictionaries

            # Assert
            assert len(result) == 1
            call_args = MockProduct.find.call_args[0][0]
            assert "$or" in call_args  # Verify search query structure

    @pytest.mark.asyncio
    async def test_get_product_by_slug_success(self, mock_product_factory):
        """Should return product by slug"""
        # Arrange
        product = mock_product_factory(slug="test-product", is_active=True)

        with patch("app.services.product_service.Product") as MockProduct:
            MockProduct.find_one = AsyncMock(return_value=product)

            # Act
            result = await ProductService.get_product_by_slug("test-product")

            # Assert
            assert isinstance(result, dict)  # Now returns dictionary
            assert result["slug"] == "test-product"

    @pytest.mark.asyncio
    async def test_get_product_by_slug_not_found(self):
        """Should raise 404 when slug not found"""
        # Arrange
        with patch("app.services.product_service.Product") as MockProduct:
            MockProduct.find_one = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await ProductService.get_product_by_slug("nonexistent")

            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_product_by_id_success(self, mock_product_factory):
        """Should return product by ID"""
        # Arrange
        product = mock_product_factory(id="prod_123")

        with patch("app.services.product_service.Product") as MockProduct:
            MockProduct.get = AsyncMock(return_value=product)

            # Act
            result = await ProductService.get_product_by_id("prod_123")

            # Assert
            assert result == product

    @pytest.mark.asyncio
    async def test_create_product_success(self, mock_product_factory):
        """Should create new product"""
        # Arrange
        new_product = mock_product_factory(slug="new-product")

        with patch("app.services.product_service.Product") as MockProduct:
            MockProduct.find_one = AsyncMock(return_value=None)
            MockProduct.return_value = new_product

            # Act
            result = await ProductService.create_product(
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
            new_product.insert.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_product_fails_duplicate_slug(self, mock_product_factory):
        """Should raise 400 for duplicate slug"""
        # Arrange
        with patch("app.services.product_service.Product") as MockProduct:
            MockProduct.find_one = AsyncMock(return_value=mock_product_factory())

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await ProductService.create_product(
                    product_id=1, name="Test", slug="existing-slug",
                    description=None, price=99.99, image=None,
                    inventory=10, category=None, is_active=True
                )

            assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_product_fails_duplicate_product_id(self, mock_product_factory):
        """Should raise 400 for duplicate product_id"""
        # Arrange
        with patch("app.services.product_service.Product") as MockProduct:
            # First call for slug returns None, second for product_id returns existing
            MockProduct.find_one = AsyncMock(side_effect=[None, mock_product_factory()])

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await ProductService.create_product(
                    product_id=1, name="Test", slug="new-slug",
                    description=None, price=99.99, image=None,
                    inventory=10, category=None, is_active=True
                )

            assert exc.value.status_code == 400

