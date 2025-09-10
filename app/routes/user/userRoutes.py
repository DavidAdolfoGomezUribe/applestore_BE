from fastapi import APIRouter, HTTPException, status
from app.schemas.user.userSchemas import UserRequest, UserResponse
from app.services.user.userService import create_user_db, get_user_db, update_user_db, delete_user_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_route(user: UserRequest):
    user_id = create_user_db(user.name, user.email, user.password)
    if not user_id:
        raise HTTPException(status_code=500, detail="Error creating user")
    return {"id": user_id, "name": user.name, "email": user.email}

@router.get("/{user_id}", response_model=UserResponse)
def get_user_route(user_id: int):
    user = get_user_db(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_user_route(user_id: int, user: UserRequest):
    if not update_user_db(user_id, user.name, user.email):
        raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_route(user_id: int):
    if not delete_user_db(user_id):
        raise HTTPException(status_code=404, detail="User not found")