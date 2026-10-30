from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

students = [
    {"id": 1, "code": "SV001", "name": "Nguyen Van A", "email": "a@gmail.com", "age": 20},
    {"id": 2, "code": "SV002", "name": "Tran Thi B", "email": "b@gmail.com", "age": 22},
    {"id": 3, "code": "SV003", "name": "Le Van C", "email": "c@gmail.com", "age": 18}
]   


class StudentRequest(BaseModel):
    code: str
    name: str = Field(..., min_length=1)  # Name không được rỗng
    email: str = Field(..., min_length=1) # Email không được rỗng
    age: int = Field(..., gt=0)           # Age phải lớn hơn 0


@app.post("/students")
def create_student(respond: StudentRequest):
    req_code = respond.code
    for s in students:
        if req_code.lower() == s["code"].lower():
            return {"message": "Code không được trùng"}
    
    new_id = max(s["id"] for s in students) + 1 if students else 1
    
    new_student = {
        "id" : new_id,
        "code": respond.code,
        "name": respond.name,
        "email": respond.email,
        "age" : respond.age
    }    
    
    students.append(new_student)
    return {"message": "Thêm học viên thành công", "data": new_student}
    
    
@app.get("/students")
def get_all_students(
    keyword: str = Query(None), 
    min_age: int = Query(None), 
    max_age: int = Query(None)
):
    filtered_students = students
    
    if keyword:
        keyword_lower = keyword.lower()
        filtered_students = [
            s for s in filtered_students 
            if keyword_lower in s["name"].lower() 
            or keyword_lower == s["code"].lower() 
            or keyword_lower in s["email"].lower()
        ]
        
    if min_age is not None:
        filtered_students = [s for s in filtered_students if s["age"] >= min_age]
        
    # Lọc theo số tuổi tối đa
    if max_age is not None:
        filtered_students = [s for s in filtered_students if s["age"] <= max_age]
        
    return {"message": "Lấy thông tin danh sách học viên thành công", "data": filtered_students}


@app.get("/students/{student_id}")
def get_detail_student(student_id: int):
    for s in students:
        if s["id"] == student_id:
            return {"message": "Lấy thông tin chi tiết học viên thành công", "data": s}
        
    return {"message": "Student not found."}
    
    
@app.put("/students/{student_id}")
def update_student(student_id: int, respond: StudentRequest):
    target_student = None
    for s in students:
        if s["id"] == student_id:
            target_student = s
            break
    
    if target_student is None:
        return {"message": "Student not found."}
    
    for s in students:
        if s["code"].lower() == respond.code.lower() and s["id"] != student_id:
            return {"message": "Code không được trùng"}
        
    target_student["code"] = respond.code
    target_student["name"] = respond.name
    target_student["email"] = respond.email
    target_student["age"] = respond.age
    
    return {"message": "Cập nhật thông tin học viên thành công", "data": target_student}


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    for index, s in enumerate(students):
        if s["id"] == student_id:
            students.pop(index) 
            return {"message": f"Xóa học viên có id {student_id} thành công"}
    
    return {"message": "Student not found."}