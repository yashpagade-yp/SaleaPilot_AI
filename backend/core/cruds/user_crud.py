"""CRUD operations for user records."""

from fastapi import HTTPException, status

from commons.logger import logger
from core.database.database import get_engine, get_utc_now, parse_object_id
from core.models.user_model import User, UserRole

logging = logger(__name__)


class CRUDUser:
    """Database access layer for user records."""

    async def create(self, *, obj_in: dict) -> User:
        """Create a new user record.

        Args:
            obj_in (dict): User creation payload.

        Returns:
            User: Created user model instance.

        Raises:
            Exception: If the database write fails.
        """
        try:
            logging.info("Executing CRUDUser.create")
            user = User(**obj_in)
            await get_engine().save(user)
            return user
        except Exception as error:
            logging.error(f"Error in CRUDUser.create: {error}")
            raise error

    async def get_by_id(self, *, id: str) -> User | None:
        """Read a user record by unique identifier.

        Args:
            id (str): User identifier.

        Returns:
            User | None: Matching user model or None when not found.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDUser.get_by_id")
            return await get_engine().find_one(User, User.id == parse_object_id(id))
        except ValueError as error:
            logging.warning(f"Invalid user id received: {id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error),
            ) from error
        except Exception as error:
            logging.error(f"Error in CRUDUser.get_by_id: {error}")
            raise error

    async def get_by_email(self, *, email: str) -> User | None:
        """Read a user record by email address.

        Args:
            email (str): User email address.

        Returns:
            User | None: Matching user model or None when not found.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDUser.get_by_email")
            return await get_engine().find_one(User, User.email == email)
        except Exception as error:
            logging.error(f"Error in CRUDUser.get_by_email: {error}")
            raise error

    async def get_by_phone_number(self, *, phone_number: str) -> User | None:
        """Read a user record by phone number.

        Args:
            phone_number (str): User phone number.

        Returns:
            User | None: Matching user model or None when not found.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDUser.get_by_phone_number")
            return await get_engine().find_one(
                User,
                User.phone_number == phone_number,
            )
        except Exception as error:
            logging.error(f"Error in CRUDUser.get_by_phone_number: {error}")
            raise error

    async def list_by_role(self, *, role: UserRole) -> list[User]:
        """List users filtered by platform role.

        Args:
            role (UserRole): User role to filter by.

        Returns:
            list[User]: Matching users for the requested role.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDUser.list_by_role")
            return await get_engine().find(User, User.role == role)
        except Exception as error:
            logging.error(f"Error in CRUDUser.list_by_role: {error}")
            raise error

    async def update(self, *, id: str, obj_in: dict) -> User | None:
        """Update an existing user record by identifier.

        Args:
            id (str): User identifier.
            obj_in (dict): Fields to update.

        Returns:
            User | None: Updated user model or None when not found.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database update fails.
        """
        try:
            logging.info("Executing CRUDUser.update")
            user = await self.get_by_id(id=id)
            if user is None:
                logging.warning(f"No user found with id: {id}")
                return None

            for field, value in obj_in.items():
                setattr(user, field, value)
            user.updated_at = get_utc_now()

            await get_engine().save(user)
            return user
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in CRUDUser.update: {error}")
            raise error

    async def delete(self, *, id: str) -> bool:
        """Delete an existing user record by identifier.

        Args:
            id (str): User identifier.

        Returns:
            bool: True when the record was deleted, otherwise False.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database delete fails.
        """
        try:
            logging.info("Executing CRUDUser.delete")
            user = await self.get_by_id(id=id)
            if user is None:
                logging.warning(f"No user found with id: {id}")
                return False

            await get_engine().delete(user)
            return True
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in CRUDUser.delete: {error}")
            raise error
