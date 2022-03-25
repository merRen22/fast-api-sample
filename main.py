from pydantic import BaseModel, Field, SecretStr, EmailStr
from fastapi import FastAPI, Body, Query, Path, status, Form, Header, Cookie, UploadFile, File, HTTPException
from typing import Dict, Optional, List
# Use to generate UUID
# from uuid import UUID
from enum import Enum

app: FastAPI = FastAPI()


class LoginOut(BaseModel):
    username: str = Field(..., max_length=20, example='gus')
    password: str = Field(..., min_length=2, max_length=20, example='123')
    message: str = Field(default='Login successful :)', description='Description message')


class HairColor(Enum):
    white = "white",
    black = "black",
    brown = "brown",
    yellow = "yellow",
    red = "red",


class Location(BaseModel):
    city: str
    state: str
    country: str


class PersonBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., gt=0, le=115)
    hair_color: Optional[HairColor] = Field(default=None)
    is_married: Optional[bool] = Field(
        default=None,
        # example = False
    )

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Rodrigo",
                "last_name": "Lopez",
                "age": 30,
                "hair_color": "black",
                "is_married": False
            }
        }


class Person(PersonBase):
    password: SecretStr = Field(..., title="Password", min_length=8)


class PersonOut(PersonBase):
    pass


@app.get(path="/", status_code=status.HTTP_200_OK,
         tags=["Persons"])
def home() -> Dict:
    return {"hello": "world"}


# The function gets the data from the body of the request
@app.post(
    path="/person/new",
    response_model=PersonOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Persons"],
    summary="Create Person in the app"
)
def create_person(person: Person = Body(...)) -> Person:
    """
    Create Person ( should use copilot for this or Python Docstring Generator )

    This function helps to create a complete new user and stores it in the DB

    Parameters:
    - Request body parameter:
        - **person: Person** -> A person model with first name, last name, age, hair color and marital stauts

    Returns a person model with first name, last name, age, hair color and marital status
    """
    return person


# The function gets the data from query
@app.post(path="/person/detail", status_code=status.HTTP_200_OK, tags=["Persons"], deprecated=True)
def show_person(
        # you can also use regex as validator as well as ge(>=), le(<=), gt(>) and lt(<)
        name: Optional[str] = Query(
            None,
            min_length=1,
            max_length=50,
            title="Person name",
            description="This is the person name. It's between 1 and 50 characters",
            example="gaaaaaaaaaa"
        ),
        age: str = Query(
            ...,
            min_length=1,
            max_length=50,
            title="Person age",
            description="This is the person age",
            example="1"
        )
):
    return {name: age}


persons = [1, 2, 3, 4, 5]


@app.get("/person/detail/{person_id}", tags=["Persons"])
def show_person(
        person_id: int = Path(
            ...,
            gt=0,
            example=123
        )
):
    if person_id not in persons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="¡This person doesn't exist!"
        )
    return {person_id: "It exists!"}


@app.put('/person/{person_id}', tags=["Persons"])
def update_person(
        person_id: int = Path(
            ...,
            ge=1,
            title='Person id',
            description='Id of the person you want to update'
        ),
        person: Person = Body(...),
        location: Location = Body(...)
):
    result = dict(person)
    result.update(dict(location))

    return result


@app.post(
    path='/login',
    response_model=LoginOut,
    status_code=200,
    response_model_exclude={'password'},
    tags=["Persons"]
)
def login(username: str = Form(...), password=Form(...)):
    return LoginOut(username=username, password=password)


@app.post(
    path="/contact",
    status_code=status.HTTP_200_OK,
    tags=["Contact"]
)
def contact(
        first_name: str = Form(
            ...,
            max_length=20,
            min_length=1
        ),
        last_name: str = Form(
            ...,
            max_length=20,
            min_length=1
        ),
        email: EmailStr = Form(...),
        message: str = Form(
            ...,
            min_length=20
        ),
        user_agent: Optional[str] = Header(default=None),
        ads: Optional[str] = Cookie(default=None)
):
    return user_agent


@app.post(
    path='/post-image',
    tags=["Image"]
)
def post_images(
        images: List[UploadFile] = File(...)
):
    info_images = [{
        "filename": image.filename,
        "Format": image.content_type,
        "Size(kb)": round(len(image.file.read()) / 1024, ndigits=2)
    } for image in images]

    return info_images


@app.post(path="/post-image", status_code=status.HTTP_201_CREATED,
          tags=["Image"])
def post_image(image: UploadFile = File(...)):
    return {
        "Filename": image.filename,
        "Format": image.content_type,
        "Size": str(round(len(image.file.read()) / 1024, ndigits=2)) + " mb",
    }
