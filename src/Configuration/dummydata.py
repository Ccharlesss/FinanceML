from sqlite3 import IntegrityError
from src.Controllers.RoleController import assign_role, create_role
from src.Models import UserModel


async def seed_initial_data(session):
    try:
        # Seed roles
        await create_role("user", session)
        await create_role("manager", session)

        # Seed a user with the manager role
        user_data = {
            "username": "Romain",
            "email": "romain.kuhne@bluewin.ch",
            "password": "password123"  # Hash the password before saving in production
        }
        user = UserModel.User(**user_data)
        session.add(user)
        await session.commit()

        # Assign role to the user
        await assign_role(user.email, "manager", session)  # Assuming you want to assign role based on email

    except IntegrityError as e:
        await session.rollback()
        print(f"IntegrityError occurred: {str(e)}")
    except Exception as e:
        await session.rollback()
        print(f"Error occurred: {str(e)}")
    finally:
        await session.close()  # Ensure the session is properly closed

