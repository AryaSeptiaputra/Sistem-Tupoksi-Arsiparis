"""
Pagination utility untuk handle large datasets efficiently.
Mendukung offset-based dan cursor-based pagination.
"""

from typing import TypeVar, Generic, List, Dict, Any, Optional
from sqlalchemy.orm import Query
from math import ceil

T = TypeVar('T')


class PaginationParams:
    """Extract pagination parameters dari request"""
    
    def __init__(self, page: int = 1, per_page: int = 20, 
                 sort_by: str = 'id', sort_order: str = 'asc'):
        """
        Args:
            page: Page number (1-indexed), default 1
            per_page: Items per page, default 20, max 100
            sort_by: Column to sort by
            sort_order: 'asc' or 'desc'
        """
        self.page = max(1, int(page)) if page else 1
        self.per_page = min(100, max(1, int(per_page))) if per_page else 20
        self.sort_by = sort_by or 'id'
        self.sort_order = (sort_order or 'asc').lower()
        
        if self.sort_order not in ['asc', 'desc']:
            self.sort_order = 'asc'
    
    @property
    def offset(self) -> int:
        """Calculate offset dari page"""
        return (self.page - 1) * self.per_page
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'page': self.page,
            'per_page': self.per_page,
            'sort_by': self.sort_by,
            'sort_order': self.sort_order
        }


class PaginatedResult:
    """Response wrapper untuk paginated data"""
    
    def __init__(self, items: List[Any], total: int, 
                 page: int, per_page: int):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.total_pages = ceil(total / per_page) if per_page > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary untuk JSON response"""
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
    """
    Apply pagination ke SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        pagination: PaginationParams instance
    
    Returns:
        PaginatedResult dengan items dan metadata
    """
    # Get total count SEBELUM apply limit/offset
    total = query.count()
    
    # Apply sort jika valid
    if hasattr(query.statement.froms[0], pagination.sort_by):
        sort_column = getattr(query.statement.froms[0], pagination.sort_by)
        if pagination.sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    
    # Apply pagination
    items = query.offset(pagination.offset).limit(pagination.per_page).all()
    
    return PaginatedResult(
        items=items,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page
    )


def get_pagination_params(request_args: dict) -> PaginationParams:
    """
    Extract pagination params dari request.args
    
    Usage dalam route:
        pagination = get_pagination_params(request.args)
    """
    return PaginationParams(
        page=request_args.get('page', 1, type=int),
        per_page=request_args.get('per_page', 20, type=int),
        sort_by=request_args.get('sort_by', 'id'),
        sort_order=request_args.get('sort_order', 'asc')
    )
