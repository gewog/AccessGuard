import uvicorn
from fastapi import FastAPI

from app.routers import auth, users, roles, ac_rule

app = FastAPI(debug=True)

app.include_router(auth.router, prefix="/auth", tags=["auth"]) # Роутер аутентификации
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(ac_rule.router, prefix="/access-rules", tags=["access_rules"])

@app.get("/")
async def main():
    """Сообщение стартовой страницы"""
    return {"message": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)