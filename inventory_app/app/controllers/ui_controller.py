from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
from app.core.ui_auth import require_ui_user

router = APIRouter(prefix="/ui")
templates = Jinja2Templates(directory="app/templates")

API_BASE = "http://127.0.0.1:8000"


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )


@router.post("/login")
def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    resp = requests.post(
        f"{API_BASE}/auth/login",
        data={
            "username": username,
            "password": password
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        timeout=5
    )

    if resp.status_code != 200:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Invalid credentials"}
        )

    token = resp.json()["access_token"]

    response = RedirectResponse("/ui/categories", status_code=302)
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="lax"
    )
    return response


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request}
    )


@router.post("/register")
@router.post("/register")
def register_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    resp = requests.post(
        f"{API_BASE}/auth/register",
        data={
            "username": username,
            "password": password
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        timeout=5
    )

    if resp.status_code != 200:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "User already exists"}
        )

    return RedirectResponse("/ui/login", status_code=302)




@router.get("/categories")
def category_list(
    request: Request,
    search: str | None = None
):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies["access_token"]

    params = {}
    if search:
        params["search"] = search

    resp = requests.get(
        f"{API_BASE}/api/categories",
        params=params,
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=5
    )

    categories = resp.json() if resp.status_code == 200 else []

    return templates.TemplateResponse(
        "category/list.html",
        {
            "request": request,
            "categories": categories,
            "search": search
        }
    )



@router.post("/categories/add")
def add_category(
    request: Request,
    name: str = Form(...)
):
    # 🔐 protect page
    auth = require_ui_user(request)
    if auth:
        return auth

    # ❗ STRICT cookie read (do not use .get)
    token = request.cookies["access_token"]

    resp = requests.post(
        f"{API_BASE}/api/categories",
        json={"name": name},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        timeout=5
    )

    # 🔴 TEMP DEBUG (REMOVE LATER)
    if resp.status_code != 201:
        print("ADD CATEGORY FAILED")
        print("STATUS:", resp.status_code)
        print("RESPONSE:", resp.text)

    return RedirectResponse("/ui/categories", status_code=302)

@router.post("/categories/delete/{category_id}")
def delete_category(
    request: Request,
    category_id: int
):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies["access_token"]

    requests.delete(
        f"{API_BASE}/api/categories/{category_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=5
    )

    return RedirectResponse("/ui/categories", status_code=302)

@router.post("/categories/update/{category_id}")
def update_category(
    request: Request,
    category_id: int,
    name: str = Form(...)
):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies["access_token"]

    requests.put(
        f"{API_BASE}/api/categories/{category_id}",
        json={"name": name},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        timeout=5
    )

    return RedirectResponse("/ui/categories", status_code=302)


# -------------------------
# SUPPLIERS UI
# -------------------------
@router.get("/suppliers")
def supplier_list(request: Request, search: str | None = None):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies["access_token"]

    params = {"search": search} if search else {}

    resp = requests.get(
        f"{API_BASE}/api/suppliers",
        params=params,
        headers={"Authorization": f"Bearer {token}"}
    )

    suppliers = resp.json() if resp.status_code == 200 else []

    return templates.TemplateResponse(
        "supplier/list.html",
        {
            "request": request,
            "suppliers": suppliers,
            "search": search
        }
    )


@router.post("/suppliers/add")
def add_supplier(request: Request, name: str = Form(...)):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies["access_token"]

    requests.post(
        f"{API_BASE}/api/suppliers",
        json={"name": name},
        headers={"Authorization": f"Bearer {token}"}
    )

    return RedirectResponse("/ui/suppliers", status_code=302)


@router.post("/suppliers/update/{supplier_id}")
def update_supplier(
    request: Request,
    supplier_id: int,
    name: str = Form(...)
):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies["access_token"]

    requests.put(
        f"{API_BASE}/api/suppliers/{supplier_id}",
        json={"name": name},
        headers={"Authorization": f"Bearer {token}"}
    )

    return RedirectResponse("/ui/suppliers", status_code=302)


@router.post("/suppliers/delete/{supplier_id}")
def delete_supplier(request: Request, supplier_id: int):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies["access_token"]

    requests.delete(
        f"{API_BASE}/api/suppliers/{supplier_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    return RedirectResponse("/ui/suppliers", status_code=302)


@router.get("/products")
def product_list(
    request: Request,
    search: str | None = None,
    category_id: int | None = None,
    supplier_id: int | None = None,
):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies.get("access_token")

    params = {}
    if search:
        params["search"] = search
    if category_id:
        params["category_id"] = category_id
    if supplier_id:
        params["supplier_id"] = supplier_id

    products = []
    categories = []
    suppliers = []

    try:
        p_resp = requests.get(
            f"{API_BASE}/api/products",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=5
        )
        if p_resp.status_code == 200:
            products = p_resp.json()
    except Exception:
        pass

    try:
        c_resp = requests.get(
            f"{API_BASE}/api/categories",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if c_resp.status_code == 200:
            categories = c_resp.json()
    except Exception:
        pass

    try:
        s_resp = requests.get(
            f"{API_BASE}/api/suppliers",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if s_resp.status_code == 200:
            suppliers = s_resp.json()
    except Exception:
        pass

    # ✅ ALWAYS RETURN TEMPLATE
    return templates.TemplateResponse(
        "product/list.html",
        {
            "request": request,
            "products": products,
            "categories": categories,
            "suppliers": suppliers,
            "search": search,
            "category_id": category_id,
            "supplier_id": supplier_id,
        }
    )

@router.post("/products/add")
def add_product(
    request: Request,
    name: str = Form(...),
    sku: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    category_id: int = Form(...),
    supplier_id: int = Form(...)
):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/ui/login", status_code=302)

    payload = {
        "name": name,
        "sku": sku,
        "price": price,
        "quantity": quantity,
        "category_id": category_id,
        "supplier_id": supplier_id
    }

    resp = requests.post(
        f"{API_BASE}/api/products",
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )

    if resp.status_code not in (200, 201):
        print("PRODUCT ADD FAILED")
        print(resp.status_code, resp.text)

    return RedirectResponse("/ui/products", status_code=302)

@router.post("/products/update/{product_id}")
def update_product(
    request: Request,
    product_id: int,
    name: str = Form(...),
    sku: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    category_id: int = Form(...),
    supplier_id: int = Form(...)
):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies["access_token"]

    payload = {
        "name": name,
        "sku": sku,
        "price": price,
        "quantity": quantity,
        "category_id": category_id,
        "supplier_id": supplier_id
    }

    resp = requests.put(
        f"{API_BASE}/api/products/{product_id}",
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )

    if resp.status_code != 200:
        print("PRODUCT UPDATE FAILED")
        print(resp.text)

    return RedirectResponse("/ui/products", status_code=302)


@router.post("/products/delete/{product_id}")
def delete_product(request: Request, product_id: int):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies["access_token"]

    requests.delete(
        f"{API_BASE}/api/products/{product_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    return RedirectResponse("/ui/products", status_code=302)


# =========================
# SALES LIST PAGE
# =========================
@router.get("/sales")
def sales_list(request: Request):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies.get("access_token")

    # ---- Fetch products ----
    products_resp = requests.get(
        f"{API_BASE}/api/products",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5
    )
    products = products_resp.json() if products_resp.status_code == 200 else []

    # ---- Fetch sales ----
    sales_resp = requests.get(
        f"{API_BASE}/api/sales",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5
    )
    sales = sales_resp.json() if sales_resp.status_code == 200 else []

    # ---- Build product map ----
    product_map = {p["id"]: p for p in products}

    # ---- Enrich sales (SAFE) ----
    enriched_sales = []
    for s in sales:
        product = product_map.get(s["product_id"])

        s["product_name"] = product["name"] if product else "—"
        s["product_price"] = product["price"] if product else 0

        enriched_sales.append(s)

    return templates.TemplateResponse(
        "sale/list.html",
        {
            "request": request,
            "sales": enriched_sales,
            "products": products
        }
    )


# =========================
# ADD SALE
# =========================
@router.post("/sales/add")
def sales_add(
    request: Request,
    product_id: int = Form(...),
    quantity_sold: int = Form(...)
):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies.get("access_token")

    requests.post(
        f"{API_BASE}/api/sales",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product_id,
            "quantity_sold": quantity_sold
        },
        timeout=5
    )

    return RedirectResponse("/ui/sales", status_code=302)


# =========================
# UPDATE SALE
# =========================
@router.post("/sales/update/{sale_id}")
def sales_update(
    request: Request,
    sale_id: int,
    product_id: int = Form(...),
    quantity_sold: int = Form(...)
):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies.get("access_token")

    resp = requests.put(
        f"{API_BASE}/api/sales/{sale_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product_id,
            "quantity_sold": quantity_sold
        },
        timeout=5
    )

    if resp.status_code != 200:
        return RedirectResponse("/ui/sales?error=update_failed", status_code=302)

    return RedirectResponse("/ui/sales", status_code=302)


# =========================
# DELETE SALE
# =========================
@router.post("/sales/delete/{sale_id}")
def sales_delete(request: Request, sale_id: int):
    auth = require_ui_user(request)
    if auth:
        return auth

    token = request.cookies.get("access_token")

    requests.delete(
        f"{API_BASE}/api/sales/{sale_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5
    )

    return RedirectResponse("/ui/sales", status_code=302)






  