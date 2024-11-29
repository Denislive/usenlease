from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for the User model to handle user creation logic.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        
        Args:
            email (str): The user's email address.
            password (str, optional): The user's password.
            **extra_fields: Additional fields for the user model.
        
        Raises:
            ValueError: If the email is not provided.

        Returns:
            User: The created user instance.
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)  # Normalize the email address.
        user = self.model(email=email, **extra_fields)  # Create a new user instance.
        user.set_password(password)  # Set the user's password.
        user.save(using=self._db)  # Save the user to the database.
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        
        Args:
            email (str): The superuser's email address.
            password (str, optional): The superuser's password.
            **extra_fields: Additional fields for the user model.

        Raises:
            ValueError: If the `is_staff` or `is_superuser` fields are not set to True.

        Returns:
            User: The created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)  # Ensure the superuser has staff permissions.
        extra_fields.setdefault('is_superuser', True)  # Ensure the superuser has superuser permissions.
        extra_fields.setdefault('is_active', True)  # Ensure the superuser is active.

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)  # Create the superuser.
