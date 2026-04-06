from fastapi import FastAPI
from fastapi import Query
from pydantic import BaseModel, Field
from typing import Optional
from typing import List

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

orders = []

@app.post("/orders")
def place_order(product_id: int, quantity: int):

    order_id = len(orders) + 1

    order = {
        "order_id": order_id,
        "product_id": product_id,
        "quantity": quantity,
        "status": "pending"
    }

    orders.append(order)

    return {
        "message": "Order placed",
        "order": order
    }

@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return {"error": "Order not found"}