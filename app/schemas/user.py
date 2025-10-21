from pydantic import BaseModel, EmailStr, model_validator

class UserCreate(BaseModel):
    email: EmailStr
    password1: str
    password2: str
    first_name: str
    last_name: str

    @model_validator(mode='after')
    def validate_passwords(self):
        # Проверяем длину пароля в байтах (UTF-8)
        password_bytes = self.password1.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValueError("Пароль не должен превышать 72 байта")

        if self.password1 != self.password2:
            raise ValueError("Пароли не совпадают")
        return self



class UserLogin(BaseModel):
    email: EmailStr
    password: str
