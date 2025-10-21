from pydantic import BaseModel

class AccessRuleCreate(BaseModel):
    role_id: int
    element_id: int
    read_permission: bool = False
    create_permission: bool = False
    update_permission: bool = False
    delete_permission: bool = False
