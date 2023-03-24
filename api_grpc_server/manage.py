from asyncio import run as aiorun
from faker import Faker
import typer

from db.db import async_session
from schemas.user import UserCreateDto
from services.user_repository import users_crud


fake = Faker()


app = typer.Typer()


@app.command()
def create_admin(email: str, password: str, first_name: str, last_name: str):
    async def create():
        async with async_session() as session:
            admin = UserCreateDto(email=email, password=password, first_name=first_name, last_name=last_name)
            item = await users_crud.create_admin(db=session, dto=admin)
            print(f'User created: {item}!')

    aiorun(create())


@app.command()
def create_fake_users(amount: int):
    async def create():
        async with async_session() as session:
            for _ in range(amount):
                user = UserCreateDto(
                    email=fake.ascii_company_email(),
                    password='123123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                )
                await users_crud.create(db=session, obj_in=user)
                print(f'User created  {user}!')

    aiorun(create())


@app.command()
def hello(name: str):
    print(f'Hello Practicum {name}!')


if __name__ == '__main__':
    app()
