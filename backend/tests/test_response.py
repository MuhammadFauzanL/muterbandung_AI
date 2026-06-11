"""
Tests for response utility functions.
Validates the standard response format helpers.
"""

from app.utils.response import success_response, error_response, paginated_response


class TestSuccessResponse:
    def test_default_values(self):
        result = success_response()
        assert result == {
            "statusCode": 200,
            "message": "Success",
            "data": None,
        }

    def test_custom_values(self):
        result = success_response(
            data={"key": "value"},
            message="Created",
            status_code=201,
        )
        assert result["statusCode"] == 201
        assert result["message"] == "Created"
        assert result["data"] == {"key": "value"}


class TestErrorResponse:
    def test_default_values(self):
        result = error_response()
        assert result == {
            "statusCode": 400,
            "message": "An error occurred",
            "errors": [],
        }

    def test_custom_errors(self):
        result = error_response(
            message="Invalid",
            status_code=422,
            errors=[{"field": "name", "message": "required"}],
        )
        assert result["statusCode"] == 422
        assert len(result["errors"]) == 1


class TestPaginatedResponse:
    def test_pagination_meta(self):
        result = paginated_response(
            data=[1, 2, 3],
            page=2,
            limit=10,
            total=25,
        )
        assert result["statusCode"] == 200
        assert result["data"] == [1, 2, 3]
        meta = result["meta"]
        assert meta["page"] == 2
        assert meta["limit"] == 10
        assert meta["total"] == 25
        assert meta["totalPages"] == 3  # ceil(25/10)

    def test_single_page(self):
        result = paginated_response(data=[], page=1, limit=10, total=5)
        assert result["meta"]["totalPages"] == 1

    def test_zero_total(self):
        result = paginated_response(data=[], page=1, limit=10, total=0)
        assert result["meta"]["totalPages"] == 0

    def test_exact_division(self):
        result = paginated_response(data=[], page=1, limit=10, total=30)
        assert result["meta"]["totalPages"] == 3
