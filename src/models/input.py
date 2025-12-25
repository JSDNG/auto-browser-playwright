"""Input models used by the current automation scripts."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class ViewportConfig(BaseModel):
    width: int = 1280
    height: int = 720


class Config(BaseModel):
    """Config cho việc lọc dữ liệu."""
    created_date: int = Field(default=2, ge=1, le=12, description="Số tháng để lọc ngày đăng (1-12, ví dụ: 2 = trong vòng 2 tháng)")


class SearchInput(BaseModel):
    """Simple search input for Etsy scraping."""

    keyword: str = Field(default="t-shirt", min_length=1)
    pages: int = Field(default=5, ge=1, le=20)
    config: Optional[Config] = Field(default_factory=lambda: Config(created_date=2), description="Config cho việc lọc dữ liệu")

    @field_validator("keyword")
    @classmethod
    def strip_keyword(cls, v: str):
        cleaned = v.strip()
        return cleaned or "t-shirt"


class HideMyAccSearchInput(BaseModel):
    """
    Search input for Etsy scraping với HideMyAcc profile.
    
    Có 2 trường hợp sử dụng:
    1. Không có proxy: chỉ truyền profile_id, keyword, pages
    2. Có proxy: truyền thêm proxy_server, proxy_username, proxy_password
    """

    profile_id: str = Field(..., description="HideMyAcc profile ID (bắt buộc)")
    keyword: str = Field(..., min_length=1, description="Từ khóa tìm kiếm (bắt buộc)")
    pages: int = Field(..., ge=1, le=20, description="Số trang cần spy (bắt buộc)")
    config: Optional[Config] = Field(default_factory=lambda: Config(created_date=2), description="Config cho việc lọc dữ liệu")
    proxy_server: Optional[str] = Field(default=None, description="Proxy server address (ví dụ: http://149.20.240.190:4444)")
    proxy_username: Optional[str] = Field(default=None, description="Proxy username (bắt buộc nếu có proxy_server)")
    proxy_password: Optional[str] = Field(default=None, description="Proxy password (bắt buộc nếu có proxy_server)")

    @field_validator("keyword")
    @classmethod
    def strip_keyword(cls, v: str):
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("keyword không được để trống")
        return cleaned
    
    @model_validator(mode='after')
    def validate_proxy_fields(self):
        """Đảm bảo nếu có proxy_server thì phải có đầy đủ username và password"""
        proxy_server = self.proxy_server
        proxy_username = self.proxy_username
        proxy_password = self.proxy_password
        
        # Nếu có proxy_server thì phải có đầy đủ username và password
        if proxy_server:
            if not proxy_username or not proxy_password:
                raise ValueError("Nếu có proxy_server thì phải có đầy đủ proxy_username và proxy_password")
        
        # Nếu có proxy_username hoặc proxy_password thì phải có proxy_server
        if (proxy_username or proxy_password) and not proxy_server:
            raise ValueError("Nếu có proxy_username hoặc proxy_password thì phải có proxy_server")
        
        return self