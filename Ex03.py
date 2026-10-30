from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from datetime import date as dt_date

app = FastAPI()

rooms = [
    {"id": 1, "code": "R101", "name": "Room 101", "capacity": 30, "status": "AVAILABLE"},
    {"id": 2, "code": "R102", "name": "Room 102", "capacity": 20, "status": "AVAILABLE"},
    {"id": 3, "code": "R103", "name": "Room 103", "capacity": 40, "status": "MAINTENANCE"}
]

room_bookings = [
    {
        "id": 1,
        "room_id": 1,
        "class_name": "Python Basic",
        "student_count": 25,
        "date": "2026-07-01",
        "slot": "MORNING"
    }
]


class RoomRequest(BaseModel):
    code: str
    name: str = Field(..., min_length=1)  # Name không được rỗng
    capacity: int = Field(..., gt=0)      # Capacity phải lớn hơn 0
    status: str = Field(..., pattern="^(AVAILABLE|IN_USE|MAINTENANCE)$") # Chỉ nhận 1 trong 3 giá trị

class BookingRequest(BaseModel):
    room_id: int
    class_name: str = Field(..., min_length=1)
    student_count: int = Field(..., gt=0) # Phải lớn hơn 0
    date: str  # Định dạng YYYY-MM-DD
    slot: str = Field(..., pattern="^(MORNING|AFTERNOON|EVENING)$") # Chỉ nhận 1 trong 3 giá trị


@app.post("/rooms")
def create_room(respond: RoomRequest):
    for r in rooms:
        if respond.code.lower() == r["code"].lower():
            return {"message": "Code không được trùng"}
            
    new_id = max(r["id"] for r in rooms) + 1 if rooms else 1
    new_room = {
        "id": new_id,
        "code": respond.code,
        "name": respond.name,
        "capacity": respond.capacity,
        "status": respond.status
    }
    rooms.append(new_room)
    return {"message": "Thêm phòng học thành công", "data": new_room}


@app.get("/rooms")
def get_all_rooms(
    keyword: str = Query(None), 
    status: str = Query(None), 
    min_capacity: int = Query(None)
):
    filtered_rooms = rooms
    
    if keyword:
        k_lower = keyword.lower()
        filtered_rooms = [r for r in filtered_rooms if k_lower in r["code"].lower() or k_lower in r["name"].lower()]
        
    if status:
        filtered_rooms = [r for r in filtered_rooms if r["status"].upper() == status.upper()]
        
    if min_capacity is not None:
        filtered_rooms = [r for r in filtered_rooms if r["capacity"] >= min_capacity]
        
    return {"message": "Lấy danh sách phòng học thành công", "data": filtered_rooms}


@app.get("/rooms/{room_id}")
def get_detail_room(room_id: int):
    for r in rooms:
        if r["id"] == room_id:
            return {"message": "Lấy chi tiết phòng học thành công", "data": r}
    return {"message": "Room not found"}


@app.put("/rooms/{room_id}")
def update_room(room_id: int, respond: RoomRequest):
    target_room = None
    for r in rooms:
        if r["id"] == room_id:
            target_room = r
            break
            
    if target_room is None:
        return {"message": "Room not found"}
        
    for r in rooms:
        if r["code"].lower() == respond.code.lower() and r["id"] != room_id:
            return {"message": "Code không được trùng"}
            
    target_room["code"] = respond.code
    target_room["name"] = respond.name
    target_room["capacity"] = respond.capacity
    target_room["status"] = respond.status
    
    return {"message": "Cập nhật phòng học thành công", "data": target_room}

@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    for index, r in enumerate(rooms):
        if r["id"] == room_id:
            rooms.pop(index)
            return {"message": f"Xóa phòng học có id {room_id} thành công"}
    return {"message": "Room not found"}


@app.post("/room-bookings")
def create_booking(respond: BookingRequest):
    target_room = None
    for r in rooms:
        if r["id"] == respond.room_id:
            target_room = r
            break
            
    if target_room is None:
        return {"message": "Room id không tồn tại"}
        
    if target_room["status"] != "AVAILABLE":
        return {"message": f"Phòng này hiện tại không khả dụng (Trạng thái: {target_room['status']})"}
        
    if respond.student_count > target_room["capacity"]:
        return {"message": f"Số lượng học viên ({respond.student_count}) vượt quá sức chứa của phòng ({target_room['capacity']})"}
        
    for b in room_bookings:
        if b["room_id"] == respond.room_id and b["date"] == respond.date and b["slot"].upper() == respond.slot.upper():
            return {"message": "Phòng đã bị trùng lịch vào ngày và ca học này"}
            
    new_id = max(b["id"] for b in room_bookings) + 1 if room_bookings else 1
    new_booking = {
        "id": new_id,
        "room_id": respond.room_id,
        "class_name": respond.class_name,
        "student_count": respond.student_count,
        "date": respond.date,
        "slot": respond.slot.upper()
    }
    room_bookings.append(new_booking)
    return {"message": "Đặt lịch phòng học thành công", "data": new_booking}


@app.get("/room-bookings")
def get_all_bookings():
    return {"message": "Lấy danh sách lịch đặt phòng thành công", "data": room_bookings}