from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

courses = [
    {"id": 1, "code": "PY101", "name": "Python Basic", "duration": 30, "fee": 3000000},
    {"id": 2, "code": "API101", "name": "FastAPI Basic", "duration": 24, "fee": 2500000},
    {"id": 3, "code": "JV101", "name": "Java Basic", "duration": 40, "fee": 4000000}
]   

class CourseRequest(BaseModel):
    code: str
    name: str = Field(min_length=1)
    duration: int = Field(gt=0)
    fee: int = Field(ge=0)

@app.post("/courses")
def create_course(respond: CourseRequest):
    req_code = respond.code
    for i in courses:
        if req_code.lower() == i["code"].lower():
            return {"message": "Code không được trùng"}
    
    new_id = max(course["id"] for course in courses) + 1
    
    new_course = {
        "id" : new_id,
        "code": respond.code,
        "name": respond.name,
        "duration": respond.duration,
        "fee" : respond.fee
    }    
    
    courses.append(new_course)
    
    return{"message": "Thêm khóa học thành công", "data": new_course}
    
    
@app.get("/course")
def get_all_courses(keyword: str = Query(None), min_fee: int = Query(None), max_fee: int = Query(None)):
    filtered_course = courses
    
    if keyword:
        filtered_course = [c for c in courses if keyword.lower() == c["name"].lower() or keyword.lower() == c["code"].lower()]
        
    if not min_fee == None:
        filtered_course = [c for c in courses if c["fee"] >= min_fee]
        
    if not max_fee == None:
        filtered_course = [c for c in courses if c["fee"] <= max_fee]
        
    return {"message": "Lấy thông tin khóa học thành công", "data": filtered_course}


@app.get("/courses/{course_id}")
def get_detail_course(course_id: int):
    check = False
    for c in courses:
        if c["id"] == course_id:
            value = c
            check = True
            return {"message": "Lấy thông tin chi tiết khóa học thành công", "data": value}
        
    if check == False:
        return {"message": "Course not found."}
    
    
@app.put("/courses/{course_id}")
def update_course(course_id: int, respond: CourseRequest):
    target_course = None
    for c in courses:
        if c["id"] == course_id:
            target_course = c
    
    if target_course == None:
        return {"message": "Course not found"}
    
    for c in courses:
        if c["code"].lower() == respond.code.lower():
            return {"message": "Code không được trùng"}
        
    target_course["code"] = respond.code
    target_course["name"] = respond.name
    target_course["duration"] = respond.duration
    target_course["fee"] = respond.fee
    
    return {"message": "Cập nhật khóa học thành công", "data": target_course}

@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    check = False
    for c in courses:
        if c["id"] == course_id:
            courses.pop(course_id - 1)
            check = True
            return {"message": f"Xóa khóa học có id {course_id} thành công"}
    
    if check == False:
        return {"message": "Course not found"}
    
    