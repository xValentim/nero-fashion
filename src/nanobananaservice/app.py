from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
from src.image_service import remix_images_service, describe_image_service, ImageSellProductService
from contextlib import asynccontextmanager 
from fastapi.middleware.cors import CORSMiddleware 

from prompts.describe_product import prompt as prompt_product
from prompts.describe_person import prompt as prompt_person
from prompts.assistant_fashion import prompt as prompt_fashion
from prompts.search_and_sell_product_fashion import prompt as prompt_sell_product


from io import BytesIO
import base64

import grpc
import demo_pb2_grpc
import demo_pb2

import uuid
import time

import os

# cria o app

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    global channel, stub
    global cart_channel, cart_stub
    global email_channel, email_stub
    
    # ProductCatalogService connection
    # host = "[::]:3550"  # Atualize com o host e porta corretos do seu serviço gRPC
    # host = 'localhost:3550'
    host = os.getenv('PRODUCT_CATALOG_SERVICE_ADDR', 'productcatalogservice:3550')
    channel = grpc.insecure_channel(host)
    stub = demo_pb2_grpc.ProductCatalogServiceStub(channel)
    
    # CartService connection
    cart_host = os.getenv('CART_SERVICE_ADDR', 'cartservice:7070')
    cart_channel = grpc.insecure_channel(cart_host)
    cart_stub = demo_pb2_grpc.CartServiceStub(cart_channel)
    
    # EmailService connection
    email_host = os.getenv('EMAIL_SERVICE_ADDR', 'emailservice:5000')
    email_channel = grpc.insecure_channel(email_host)
    email_stub = demo_pb2_grpc.EmailServiceStub(email_channel)
    
    print("gRPC channels and stubs created (ProductCatalog, Cart, Email).")
    
    yield  # <- necessário para funcionar como async generator
    
    print("Shutting down gRPC channels.")
    channel.close()
    cart_channel.close()
    email_channel.close()
    

app = FastAPI(title="Nano Banana Service", 
              description="AI-powered fashion and image remixing service using Gemini AI",
              lifespan=lifespan)

# Allow all origins (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
def read_root():
    return {"message": "Nano Banana Service is running!"}


# Route to list all products
@app.get("/products")
def get_products():
    try:
        response = stub.ListProducts(demo_pb2.Empty())
        products = []
        # print(response)
        for product in response.products:
            products.append({
                "id": str(product.id),
                "name": str(product.name),
                "description": str(product.description),
                "price": str(product.price_usd.units),
                "picture": str(product.picture),
                "categories": [str(category) for category in product.categories]
            })
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

# Route to search product by ID
@app.get("/products/{product_id}")
def get_product_by_id(product_id: str):
    try:
        product = stub.GetProduct(demo_pb2.GetProductRequest(id=product_id))
        return {
            "id": str(product.id),
            "name": str(product.name),
            "description": str(product.description),
            "price": str(product.price_usd.units),
            "picture": str(product.picture)
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Product not found: {str(e)}")

# Route to search product by name
@app.get("/products-name/{name}")
def get_product_by_name(name: str):
    try:
        response = stub.ListProducts(demo_pb2.Empty())
        products = []

        for product in response.products:
            if product.name == name:
                products.append({
                    "id": str(product.id),
                    "name": str(product.name),
                    "description": str(product.description),
                    "price": str(product.price_usd.units),
                    "picture": str(product.picture),
                    "categories": [str(category) for category in product.categories]
                })
        # print(products)
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")

@app.post("/remix-images")
async def remix_images_endpoint(
    image1: UploadFile = File(..., description="First image for remixing"),
    image2: UploadFile = File(..., description="Second image for remixing"),
    prompt: str = Form(..., description="Prompt for image remixing"),
    stream: bool = Form(False, description="Use streaming response")
):
    """
    Endpoint to remix two images using Gemini AI.

    Receives two images and a prompt, returns the remixed image.
    """
    try:
        # Validate file types
        if not image1.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="image1 must be an image file")
        if not image2.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="image2 must be an image file")

        # Read image bytes
        image1_bytes = await image1.read()
        image2_bytes = await image2.read()

        # Generate unique image ID
        session_id = str(uuid.uuid4())[:8]  # First 8 characters of UUID
        timestamp = int(time.time())
        image_id = f"{timestamp}_{session_id}"

        # Process images using the service
        result_bytesio = remix_images_service(
            image1_bytes=image1_bytes,
            image2_bytes=image2_bytes,
            prompt=prompt,
            stream=stream
        )

        # Get bytes from BytesIO for response
        result_bytesio.seek(0)  # Ensure we're at the beginning
        result_bytes = result_bytesio.read()

        # Return image as response with unique ID in filename
        return Response(
            content=result_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=remixed_{image_id}.png",
                "X-Image-ID": image_id,  # Custom header with ID
                "X-BytesIO-Type": "converted"  # Indicates it came from BytesIO
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/describe-image")
async def describe_image(
    image: UploadFile = File(..., description="Product or person image"),
    type_prompt: str = "product"
):
    """
    Endpoint to describe a product or person from an image using Gemini AI.

    Receives an image and returns a description of the person or product, depending on type_prompt.
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        if type_prompt not in ["product", "person"]:
            raise HTTPException(status_code=400, detail="type_prompt must be 'product' or 'person'")

        # Read image bytes
        image_bytes = await image.read()

        # Generate unique image ID
        session_id = str(uuid.uuid4())[:8]  # First 8 characters of UUID
        timestamp = int(time.time())
        image_id = f"{timestamp}_{session_id}"

        # Process image using the correct service
        description = describe_image_service(
            image_bytes=image_bytes,
            prompt={
                "product": prompt_product,
                "person": prompt_person
            }.get(type_prompt, "product")
        )

        # Return description as JSON response with unique ID
        return {
            "image_id": image_id,
            "description": description
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/assistant-fashion")
async def assistant_fashion(
    image: UploadFile = File(..., description="User image with fashion items"),
):
    """
    Endpoint to provide fashion advice and compliments based on user's image.

    Receives an image of the user wearing fashion items and returns compliments and fashion tips.
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read image bytes
        image_bytes = await image.read()

        # Generate unique image ID
        session_id = str(uuid.uuid4())[:8]  # First 8 characters of UUID
        timestamp = int(time.time())
        image_id = f"{timestamp}_{session_id}"

        # Process image using the fashion assistant service
        description = describe_image_service(
            image_bytes=image_bytes,
            prompt=prompt_fashion,
            model_name="gemini-2.0-flash"
        )

        # Return description as JSON response with unique ID
        return {
            "image_id": image_id,
            "description": description
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/sell-product-from-query")
async def sell_product_from_query(
    image: UploadFile = File(..., description="User's image"),
    text: str = Form(..., description="User's text expressing interest in a product"),
    model_name: str = Form("gemini-2.5-flash-image-preview", description="Gemini model to use"),
    stream: bool = Form(False, description="Use streaming response")
):
    """
    Endpoint to create personalized product sales content from user image and text query.

    Receives a user image and text expressing product interest.
    Returns a remixed image and personalized sales description to encourage purchase.
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read image bytes
        image_bytes = await image.read()
        
        service = ImageSellProductService(api_key=None,
                                          model_name=model_name,
                                          text=text)
        # print(service)
        
        extracted_product = service.extract_product_from_text(text)
        if not extracted_product or extracted_product['name'] == "None":
            raise HTTPException(status_code=400, detail="No product identified in user query.")
        product_name = extracted_product['name']
        product_id = extracted_product.get('id', None)

        product = get_product_by_name(product_name)['products'][0]
        # print(product)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product '{product_name}' not found in store.")

        # print(f"Product identified: {product_name} (ID: {product['id']})")

        picture_path_product = product['picture'][1:]

        # Open product image using the path
        try:
            with open(picture_path_product, "rb") as f:
                product_image_bytes = f.read()
        # product_image_bytes will be used to mix with user's photo
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Product image not found: {str(e)}")

        result_bytesio = remix_images_service(
            image1_bytes=image_bytes,
            image2_bytes=product_image_bytes,
            prompt=f"Create a natural blend of both images. Place the product on the person in a realistic way.",
            stream=stream
        )

        result_bytesio.seek(0)  # Ensure we're at the beginning
        result_bytes = result_bytesio.read()
        
        # Generate unique image ID
        session_id = str(uuid.uuid4())[:8]  # First 8 characters of UUID
        timestamp = int(time.time())
        image_id = f"{timestamp}_{session_id}"
        
        result_sell_text = service.sell_product_from_image_from_bytes(
            image_bytes=result_bytes,
            product=product,
            prompt=prompt_sell_product
        )
        
        # Encode remixed image in base64 for easy JSON return
        image_base64 = base64.b64encode(result_bytes).decode("utf-8")

        return {
            "image_id": image_id,
            "image_base64": image_base64,
            "sell_text": result_sell_text,
            "product_id": product_id,
            "product_name": product_name
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# ==============================
# CARTSERVICE ENDPOINTS
# ==============================

@app.post("/cart/add-item")
def add_item_to_cart(user_id: str = Form(...), product_id: str = Form(...), quantity: int = Form(1)):
    """Add item to user's cart."""
    try:
        cart_item = demo_pb2.CartItem()
        cart_item.product_id = product_id
        cart_item.quantity = quantity
        
        request = demo_pb2.AddItemRequest()
        request.user_id = user_id
        request.item.CopyFrom(cart_item)
        
        cart_stub.AddItem(request)
        
        return {"message": f"Item {product_id} added to cart for user {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding item to cart: {str(e)}")

@app.get("/cart/{user_id}")
def get_cart(user_id: str):
    """Get user's cart contents."""
    try:
        request = demo_pb2.GetCartRequest()
        request.user_id = user_id
        
        cart = cart_stub.GetCart(request)
        
        items = []
        for item in cart.items:
            items.append({
                "product_id": item.product_id,
                "quantity": item.quantity
            })
        
        return {"user_id": user_id, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cart: {str(e)}")

@app.delete("/cart/{user_id}")
def empty_cart(user_id: str):
    """Empty user's cart."""
    try:
        request = demo_pb2.EmptyCartRequest()
        request.user_id = user_id
        
        cart_stub.EmptyCart(request)
        
        return {"message": f"Cart emptied for user {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error emptying cart: {str(e)}")

# ==============================
# EMAILSERVICE ENDPOINTS
# ==============================

@app.post("/email/send-confirmation")
def send_order_confirmation(
    email: str = Form(...),
    order_id: str = Form(...),
    shipping_tracking_id: str = Form(...),
    street_address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    country: str = Form(...),
    zip_code: str = Form(...)
):
    """Send order confirmation email."""
    try:
        # Create address
        address = demo_pb2.Address()
        address.street_address = street_address
        address.city = city
        address.state = state
        address.country = country
        # Convert zip_code to int if needed (protobuf may expect int)
        try:
            address.zip_code = int(zip_code.replace('-', '').replace(' ', ''))
        except ValueError:
            address.zip_code = 0  # Fallback if conversion fails
        
        # Create shipping cost (free by default)
        shipping_cost = demo_pb2.Money()
        shipping_cost.currency_code = "USD"
        shipping_cost.units = 0
        shipping_cost.nanos = 0
        
        # Create order data
        order_data = demo_pb2.OrderResult()
        order_data.order_id = order_id
        order_data.shipping_tracking_id = shipping_tracking_id
        order_data.shipping_cost.CopyFrom(shipping_cost)
        order_data.shipping_address.CopyFrom(address)
        
        # Create email request
        email_request = demo_pb2.SendOrderConfirmationRequest()
        email_request.email = email
        email_request.order.CopyFrom(order_data)
        
        email_stub.SendOrderConfirmation(email_request)
        
        return {"message": f"Confirmation email sent to {email}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint to verify service status."""
    return {"status": "healthy"}
