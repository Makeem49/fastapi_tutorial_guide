from fastapi import (
    FastAPI,
    Query,
    Path,
    Body,
    Cookie,
    Header,
    status,
    Form,
    File,
    UploadFile,
    HTTPException
)
from enum import Enum
from typing import Union, Set, List
from pydantic import BaseModel, Field,  EmailStr

app = FastAPI()

# basic path


@app.get("/")
async def root():
    return {"message": "Hello World"}


# PATH PARAMETERS


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    ''' remove the type hint will make the route to  accept any parameter type '''
    return {"item_id": item_id}


class ModelName(str, Enum):
    '''This will be rendered as drop box on the swagger UI and it's predefined'''
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"
    mallow = 'marshmallow'


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    '''predefined parameter'''
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    elif model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    elif model_name.mallow.value == 'marshmallow':
        return {"model_name": model_name, "message": "marshamllow all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    '''file path parameter'''
    return {"file_path": file_path}


# QUERY PARAMETER

fake_items_db = [{"item_name": "Foo"}, {
    "item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]


# PATH PARAM AND QUERY PARAM

@app.get("/product/{product_id}")
async def read_product(product_id: int, q: Union[str, None] = None, short: bool = False):
    # if q:
    #     return {"product_id": product_id, "q": q}
    item = {"item_id": product_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )

    return item


# REQUEST BODY

class Item(BaseModel):
    name: str = Field(example="Foo")
    description: Union[str, None] = Field(
        default=None, example="A very nice Item")
    price: float = Field(example=35.4)
    tax: Union[float, None] = Field(default=None, example=3.2)

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


@app.post("/items/")
def create_item(item: Item):
    return item


# REQUEST BODY, QUERY PARAMETER AND PATH PARAMETER(S)

@app.put("/items/{item_id}")
def create_item(item_id: int, item: Item, q: bool = True):
    '''FastAPI will be able to differentiate between path param and response body'''
    return {"item_id": item_id, **item.dict(), 'q': q}

# QUERY PARAM AND STRING VALIDATION


@app.get("/query_valid/")
def read_items(q: Union[str, None] = Query(default=None, max_length=5)):
    '''The Query function will make sure the query is default to None, and of max length 5'''
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# PATH PARAM AND

@app.get('/path_valid/{path_id}')
def read_valid_path(path_id: int = Path(title="The ID of the item to get"),
                    q: Union[str, None] = Query(default=None, alias="item-query"),):
    '''Uisng the Path to explicit take the function param as Path param and other meta data can be use in it'''
    results = {"item_id": path_id}
    if q:
        results.update({"q": q})
    return results


# COMNINATION OF BODIES AND PATH


class User(BaseModel):
    username: str
    full_name: Union[str, None] = None


@app.put("/combine_items/{item_id}")
def update_item(item_id: int, item: Item, user: User, importance: Union[None, int] = Body(default=1)):
    results = {"item_id": item_id, "item": item,
               "user": user, "importance": importance}
    return results


# NESTED MODEL

class Image(BaseModel):
    url: str
    name: str


class Product(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()
    image: Union[Image, None] = None


@app.put("/nested_items/{item_id}")
async def nested_item(item_id: int, item: Product):
    results = {"item_id": item_id, "item": item}
    return results


# COOKIE PARAMETERS

@app.get('/get_cookie')
def read_cookies(ads_id: Union[str, None] = Cookie(default=None)):
    print(Cookie())
    return {"ads_id": ads_id}


# HEADER PARAMETERS

@app.get("/get_heaers/")
async def get_heaers(user_agent: Union[str, None] = Header(default=None), content_type=Header(default=None)):
    return {"User-Agent": user_agent, "Content-type": content_type}

# RESPONSE MODEL


@app.post("/single_item/")
async def single_item(item: Item) -> Item:
    return item


@app.get("/list_items/", response_model=List[Item])
def list_items():
    return [
        {"name": "Portal Gun", "price": 42.0},
        {"name": "Plumbus", "price": 32.0},
    ]


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Union[str, None] = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


def fake_password_hash(raw_password: str) -> str:
    return 'suppersecret' + raw_password


def save_fake_user(user_in: UserIn):
    hashed_password = fake_password_hash(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    # print(user_in_db)
    return user_in_db


# Don't do this in production!
@app.post("/user/", response_model=UserOut, response_model_exclude_unset=True, status_code=201)
def create_user(user: UserIn):
    print(user)
    user = save_fake_user(user)
    return user


products = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/get_item/{item_id}", response_model=Item, response_model_exclude_unset=True, response_model_exclude_defaults=False, response_model_exclude_none=False, response_model_include={"name"},)
def get_item(item_id: str):
    return products[item_id]


# LIST OF MODELS

class Description(BaseModel):
    name: str
    description: str


objects = [
    {"name": "Foo", "description": "There comes my hero"},
    {"name": "Red", "description": "It's my aeroplane"},
]


@app.get("/get_description/", response_model=List[Description], status_code=status.HTTP_201_CREATED)
async def read_items():
    return objects


# FORM DATA

@app.post("/login/")
def login(username: str = Form(), password: str = Form(), age: str = Form()):
    return {"username": username, "age": age}


# FILE UPLOAD
# class FileIn(BaseModel):
#     name: str
#     age: int


@app.post("/files/")
async def create_file(file: Union[bytes, None] = File(default=None)):
    if not file:
        return {"message": "No file sent"}
    else:
        return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: Union[UploadFile, None] = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}


# EXCEPTION HANDLING

store_items = {"foo": "The Foo Wrestlers"}


@app.get("/get_item_or_errror/{item_id}", tags=['Item'])
async def read_item(item_id: str):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    if item_id not in store_items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"}
        )
    return {"item": store_items[item_id]}


# JSON COMPATIBLE ENCODER
