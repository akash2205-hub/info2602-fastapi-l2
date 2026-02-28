import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command()
def get_user(username:str=typer.Argument(..., help="Username of the you need to look for")):
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)

@cli.command()
def get_all_users():
    # The code for task 5.2 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)


@cli.command()
def change_email(username: str=typer.Argument(..., help="Username of the user whose email should be updated"), new_email:str= typer.Argument(..., help="New email address to assign to the user")):
    # The code for task 6 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")


@cli.command()
def create_user(username: str  = typer.Argument(..., help="Username for the new user"), email:str = typer.Argument(..., help="Email address of the new user"), password: str= typer.Argument(..., help="Password for the new user account")):
    # The code for task 7 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db: # Get a connection to the database
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback() 
            #print(e.orig) #optionally print the error raised by the database
            print("Username or email already taken!") 
        else:
            print(newuser) # print the newly created user

@cli.command()
def delete_user(username: str= typer.Argument(..., help="Username of the user to delete")):
    # The code for task 8 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')

@cli.command()
def find_user(search: str= typer.Argument(..., help="Partial username or email to search for")):
    with get_session() as db:
        results = db.exec(
            select(User).where(
                or_(
                    User.username.contains(search),
                    User.email.contains(search)
                )
            )
        ).all()

        if not results:
            print(f"No users found matching '{search}'")
        else:
            for user in results:
                print(user)

@cli.command()
def list_users(limit: int = typer.Argument(10, help="Maximum number of users to return (default: 10)"), offset: int = typer.Argument(0, help="Number of users to skip before returning results (default: 0)")):
    with get_session() as db:
        users = db.exec(
            select(User).offset(offset).limit(limit)
        ).all()

        if not users:
            print("No users found")
        else:
            for user in users:
                print(user)


if __name__ == "__main__":
    cli()