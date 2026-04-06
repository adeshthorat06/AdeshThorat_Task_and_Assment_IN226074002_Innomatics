from fastapi import FastAPI
from fastapi import Query
from pydantic import BaseModel, Field
from typing import Optional
from typing import List
from fastapi import HTTPException

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": False},

    # Q1 : new product
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]

@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }

@app.get("/products/category/{category_name}")
def get_product_by_category(category_name: str):
    result = [p for p in products if p['category'].lower() == category_name.lower()]

    if not result:
        return {"error" : "No product found in category"}
    
    return{"category": category_name, "product" : result, "total": len(result)}


@app.get("/products/instock")
def get_product_by_stock():
    available_products = [p for p in products if p["in_stock"] == True]

    return{
        "in_stock_Product" : available_products, "count" : len(available_products)
    }


@app.get("/store/summary")
def store_summary():

    total_products = len(products)

    in_stock_count = len([p for p in products if p["in_stock"] == True])

    out_of_stock_count = total_products - in_stock_count

    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock_count,
        "out_of_stock": out_of_stock_count,
        "categories": categories
    }

@app.get("/products/search/{keyword}")
def product_search(keyword: str):
    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": "No product match found"}

    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }


@app.get("/products/deals")
def get_deals():
    cheapest_product = min(products, key=lambda p: p["price"])
    most_expensive_product = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest_product,
        "premium_pick": most_expensive_product
    }


#Assignement - 02 Codes!

@app.get("/products/filter")
def filter_products(
    category: str = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None)):
    result = products
    # filter by category
    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    # filter by minimum price
    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    # filter by maximum price
    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    return result


@app.get("/products/{product_id}/price")
def get_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"name" : product["name"] , "price" : product["price"]}
    else:
        return {"error": "Product not found"}
    

class Feedback(BaseModel):
    customer_name : str = Field(..., min_length=2, max_length=100)
    product_id : int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


feedback = []

@app.post("/feedback")
def Submit_Feedback(data: Feedback):
    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback)
    }

@app.get("/products/summary")
def product_summary():
    in_stock = [p for p in products if p["in_stock"]]
    out_stock =  [p for p in products if not p["in_stock"]]
    expensive  = max(products, key=lambda p: p["price"])
    cheapest   = min(products, key=lambda p: p["price"])
    category = list(set(p["category"] for p in products))

    return{
        "Total_products" : len(products),
        "in_stock" : len(in_stock),
        "out_of_stock": len(out_stock),
        "expensive_product": {"name":expensive["name"], "price":expensive["price"]},
        "cheap_product": {"name":cheapest["name"], "price":cheapest["price"]},
        "categories": category


    }
    

class OrderItem(BaseModel):
    product_id : int = Field(...,gt = 0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})
    return {"company": order.company_name, "confirmed": confirmed,
            "failed": failed,
              "grand_total": grand_total}


# @app.post("/orders")
# def place_order(product_id: int, quantity: int):

#     order_id = len(orders) + 1

#     order = {
#         "order_id": order_id,
#         "product_id": product_id,
#         "quantity": quantity,
#         "status": "pending"
#     }

#     orders.append(order)

#     return {
#         "message": "Order placed",
#         "order": order
#     }

# @app.get("/orders/{order_id}")
# def get_order(order_id: int):

#     for order in orders:
#         if order["order_id"] == order_id:
#             return order

#     return {"error": "Order not found"}
# ASSIGNMENT - 03

class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool


@app.post("/products")
def add_product(product: Product):
    for p in products:
        if p["name"].lower() == product.name.lower():
            return {"error": "Product already exists"}

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {"message": "Product added", "product": new_product}



@app.get("/products/audit")
def products_audit():

    total_products = len(products)
    in_stock_products = [p for p in products if p["in_stock"]]
    in_stock_count = len(in_stock_products)

    out_of_stock_names = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda x: x["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }


@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):

    updated = []

    for product in products:
        if product["category"].lower() == category.lower():

            new_price = int(product["price"] * (1 - discount_percent / 100))
            product["price"] = new_price

            updated.append({
                "name": product["name"],
                "new_price": new_price
            })

    if not updated:
        return {"message": "No products found in this category"}

    return {"updated_products": len(updated), "products": updated}


# DYNAMIC ROUTES AFTER FIXED ROUTES

@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):

    for product in products:
        if product["id"] == product_id:

            if price is not None:
                product["price"] = price

            if in_stock is not None:
                product["in_stock"] = in_stock

            return {"message": "Product updated", "product": product}

    return {"error": "Product not found"}


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            products.remove(product)

            return {"message": f"Product '{product['name']}' deleted"}

    return {"error": "Product not found"}
# ASSIGNMENT 4 — CART SYSTEM

orders = []
cart = []


@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * product["price"]

            return {"message": "Cart updated", "cart_item": item}

    new_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": quantity * product["price"]
    }

    cart.append(new_item)

    return {"message": "Added to cart", "cart_item": new_item}


@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)

            return {"message": "Item removed", "item": item}

    raise HTTPException(status_code=404, detail="Item not in cart")


class Checkout(BaseModel):
    customer_name: str
    delivery_address: str


@app.post("/cart/checkout")
def checkout(order: Checkout):

    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    created_orders = []
    order_id = len(orders) + 1

    for item in cart:

        new_order = {
            "order_id": order_id,
            "customer_name": order.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }

        orders.append(new_order)
        created_orders.append(new_order)

        order_id += 1

    grand_total = sum(item["subtotal"] for item in cart)

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": created_orders,
        "grand_total": grand_total
    }


@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }


#------------Assignment 5--------------#

@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]
    if not results:
        return {"message": f"No products found for: {keyword}"}
    return {
        "keyword": keyword,
        "total_found": len(results),
        "products": results
    }




@app.get("/products/sort")
def sort_products(
    sort_by: str = "price",
    order: str = "asc"
):
    if sort_by not in ["price", "name"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'price' or 'name'")
    reverse = True if order == "desc" else False

    sorted_products = sorted(
        products,
        key=lambda x: x[sort_by],
        reverse=reverse
    )
    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }


@app.get("/products/page")
def paginate_products(
    page: int = 1,
    limit: int = 2
):
    total = len(products)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit
    return {
        "page": page,
        "limit": limit,
        "total_products": total,
        "total_pages": total_pages,
        "products": products[start:end]
    }

class Order(BaseModel):
    order_id: int
    customer_name: str
    product_id: int


@app.post("/orders")
def create_order(order: Order):
    orders.append(order.dict())
    return {"message": "Order placed successfully", "order": order}


@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    result = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not result:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(result),
        "orders": result
    }

@app.get("/products/sort-category")
def sort_by_category():
    sorted_products = sorted(
        products,
        key=lambda x: (x["category"], x["price"])
    )

    return {"products": sorted_products}



@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    result = products


    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]


    if sort_by not in ["price", "name"]:
        raise HTTPException(status_code=400, detail="Invalid sort_by")

 
    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": len(result),
        "products": result[start:end]
    }
# FIRST
@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit

    return {
        "total": len(orders),
        "orders": orders[start:end]
    }


# AFTER
@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            return order

    raise HTTPException(status_code=404, detail="Order not found")