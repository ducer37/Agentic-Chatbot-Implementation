from pydantic import BaseModel, Field
from typing import Optional

# Nhóm 1: Lịch Sự kiện (Học, Họp, Khám bệnh, Hẹn hò...)
class EventSchedule(BaseModel):
    activity_type: str = Field(description="Loại sự kiện: học, họp, workshop...")
    title: str = Field(description="Tiêu đề cụ thể")
    date: str = Field(description="Ngày diễn ra")
    time: str = Field(description="Giờ bắt đầu")
    location: str = Field(description="Địa điểm (Phòng học, link Zoom, quán cafe)")

# Nhóm 2: Lịch Di chuyển (Máy bay, Tàu hỏa, Xe khách...)
class TravelSchedule(BaseModel):
    transport_type: str = Field(description="Loại phương tiện: máy bay, tàu, xe...")
    departure: str = Field(description="Điểm đi")
    destination: str = Field(description="Điểm đến")
    date: str = Field(description="Ngày đi")
    time: Optional[str] = Field(description="Giờ khởi hành", default="Chưa rõ")