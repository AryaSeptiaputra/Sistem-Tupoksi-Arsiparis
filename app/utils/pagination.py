"""Pagination berbasis offset untuk query SQLAlchemy.

Item hasil query bisa berupa object model atau dict hasil `to_dict()`,
jadi diberi tipe `Any`.
"""

from typing import Any
from sqlalchemy.orm import Query
from werkzeug.datastructures import MultiDict
from math import ceil


class PaginationParams:
    """Parameter halaman yang sudah dirapikan dari request."""

    def __init__(self, page: int = 1, per_page: int = 20,
                 sort_by: str = 'id', sort_order: str = 'asc') -> None:
        """
        Args:
            page: Nomor halaman, mulai dari 1.
            per_page: Jumlah item per halaman, dibatasi 1-100.
            sort_by: Nama kolom pengurut.
            sort_order: `asc` atau `desc`; nilai lain dianggap `asc`.
        """
        self.page = max(1, int(page)) if page else 1
        self.per_page = min(100, max(1, int(per_page))) if per_page else 20
        self.sort_by = sort_by or 'id'
        self.sort_order = (sort_order or 'asc').lower()

        if self.sort_order not in ['asc', 'desc']:
            self.sort_order = 'asc'

    @property
    def offset(self) -> int:
        """Jumlah baris yang dilewati sebelum halaman ini."""
        return (self.page - 1) * self.per_page

    def to_dict(self) -> dict[str, Any]:
        """Mengubah parameter menjadi dict.

        Returns:
            Nilai `page`, `per_page`, `sort_by`, dan `sort_order`.
        """
        return {
            'page': self.page,
            'per_page': self.per_page,
            'sort_by': self.sort_by,
            'sort_order': self.sort_order
        }


class PaginatedResult:
    """Item satu halaman beserta informasi halamannya."""

    def __init__(self, items: list[Any], total: int,
                 page: int, per_page: int) -> None:
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.total_pages = ceil(total / per_page) if per_page > 0 else 0

    def to_dict(self) -> dict[str, Any]:
        """Mengubah hasil menjadi bentuk respons JSON.

        Returns:
            Dict berisi `data` dan `pagination`.
        """
        return {
            'data': self.items,
            'pagination': {
                'page': self.page,
                'per_page': self.per_page,
                'total': self.total,
                'total_pages': self.total_pages,
                'has_next': self.page < self.total_pages,
                'has_prev': self.page > 1
            }
        }


def paginate_query(query: Query, pagination: PaginationParams) -> PaginatedResult:
    """Menjalankan query untuk satu halaman.

    Args:
        query: Query SQLAlchemy yang belum dibatasi.
        pagination: Parameter halaman.

    Returns:
        Item halaman yang diminta beserta total baris.
    """
    # Total dihitung sebelum limit/offset diterapkan
    total = query.count()

    if hasattr(query.statement.froms[0], pagination.sort_by):
        sort_column = getattr(query.statement.froms[0], pagination.sort_by)
        if pagination.sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

    items = query.offset(pagination.offset).limit(pagination.per_page).all()

    return PaginatedResult(
        items=items,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page
    )


def get_pagination_params(request_args: MultiDict[str, str]) -> PaginationParams:
    """Membaca parameter halaman dari query string.

    Args:
        request_args: `request.args` dari Flask.

    Returns:
        Parameter halaman dengan nilai default bila tidak dikirim.
    """
    return PaginationParams(
        page=request_args.get('page', 1, type=int),
        per_page=request_args.get('per_page', 20, type=int),
        sort_by=request_args.get('sort_by', 'id'),
        sort_order=request_args.get('sort_order', 'asc')
    )
