from fastapi import FastAPI

from app.core.database import engine, Base
from app.models.category import Category
from app.models.user import User
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.sale import Sale
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



from app.controllers.category_controller import router as category_router
from app.controllers.auth_controller import router as auth_router
from app.controllers.supplier_controller import router as supplier_router
from app.controllers.product_controller import router as product_router
from app.controllers.sale_controller import router as sale_router
from app.controllers.report_controller import router as report_router
from app.controllers.ui_controller import router as ui_router




app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(supplier_router)
app.include_router(product_router)
app.include_router(sale_router)
app.include_router(report_router)
app.include_router(ui_router)






@app.get("/")
def health_check():
    return {"status": "ok"}
