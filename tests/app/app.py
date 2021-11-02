from fastapi import FastAPI
from fastapi_crud.fastapicrud import FastapiCRUD

from tests.app.database import db
from tests.app.models import Company, Employee

app = FastAPI()


@app.get("/")
async def index():
    return {"status": "OK"}


crud = FastapiCRUD(db._engine)
app.include_router(crud.create_router(Company))
app.include_router(crud.create_router(Employee))
