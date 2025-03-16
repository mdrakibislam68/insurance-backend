from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from roles.models import CustomGroup
from user_management.models import Account


# Create your tests here.
class AuthViewSetsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the entire test case.
        """
        # Create a test user
        cls.user = Account.objects.create_user(
            email="testuser@example.com",
            password="strongpassword123",
            is_staff= True,
            is_superuser= True,
        )
        cls.user1 = Account.objects.create_user(
            email="rakibislam@boomdevs.com",
            password="user1password123",
            first_name="Rakib",
            last_name="Islam"
        )
        cls.permission1 = Permission.objects.create(
            codename="view_role",
            name="Can view role",
            content_type_id=1  # Replace with a valid content type ID
        )
        cls.permission2 = Permission.objects.create(
            codename="add_role",
            name="Can add role",
            content_type_id=1  # Replace with a valid content type ID
        )

        # URLs for the endpoints
        cls.signup_url = '/api/v1/auth/signup/'
        cls.login_url = '/api/v1/auth/login/'
        cls.reset_password_send_url = '/api/v1/auth/reset-password-secretkey-send/'
        cls.create_new_user_url = '/api/v1/auth/create-new-user/'
        cls.update_profile_info_url = '/api/v1/auth/update-profile-info/'
        cls.user_permissions_url = '/api/v1/auth/user-permissions/'
        cls.user_list = '/api/v1/auth/users/'
        cls.set_user_role_url = '/api/v1/auth/set-user-role/'
        cls.search_users_url = '/api/v1/auth/search-users/'
        cls.generate_token_url = '/api/v1/auth/generate-token-for-customer/'
        cls.roles_list_url = '/api/v1/roles-permissions/roles/'
        # cls.search_users_url = reverse('auth-search-users')

    def setUp(self):
        login_payload = {
            "email": "testuser@example.com",
            "password": "strongpassword123"
        }

        login_response = self.client.post(
            self.login_url,
            data=login_payload,
            format='json'
        )
        self.role = CustomGroup.objects.create(
            name="Test Role",
            description="Test role for unit tests",
            is_default=False,
            is_admin=False
        )

        # Ensure the login was successful
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)

        # Extract the access token from the login response
        self.access_token = login_response.data['access']
        access_token = str(login_response.data["access"])
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_signup_valid_data(self):
        """
        Test signing up with valid data.
        """
        payload = {
            "email": "newuser@example.com",
            "password": "strongpassword123",
        }

        # Make the POST request
        response = self.client.post(
            self.signup_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Signup Response (Valid Data):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the response message
        self.assertEqual(response.data["message"], "Your account has been successfully created!")

    def test_signup_invalid_data(self):
        """
        Test signing up with invalid data.
        """
        payload = {
            "email": "invalid-email",
            "password": "weak",
            "first_name": "",
            "last_name": ""
        }

        # Make the POST request
        response = self.client.post(
            self.signup_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Signup Response (Invalid Data):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the error messages
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)

    def test_login_valid_data(self):
        """
        Test logging in with valid data.
        """
        payload = {
            "email": "testuser@example.com",
            "password": "strongpassword123"
        }

        # Make the POST request
        response = self.client.post(
            self.login_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Login Response (Valid Data):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the response data
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_data(self):
        """
        Test logging in with invalid data.
        """
        # Test case 1: Incorrect password
        payload_incorrect_password = {
            "email": "testuser@example.com",
            "password": "wrongpassword"  # Incorrect password
        }

        response = self.client.post(
            self.login_url,
            data=payload_incorrect_password,
            format='json'
        )

        print("Login Response (Incorrect Password):", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

        # Test case 2: Empty email field
        payload_empty_email = {
            "email": "",  # Empty email
            "password": "testpassword"
        }

        response = self.client.post(
            self.login_url,
            data=payload_empty_email,
            format='json'
        )

        print("Login Response (Empty Email):", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

        # Test case 3: Empty password field
        payload_empty_password = {
            "email": "testuser@example.com",
            "password": ""  # Empty password
        }

        response = self.client.post(
            self.login_url,
            data=payload_empty_password,
            format='json'
        )

        print("Login Response (Empty Password):", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

        # Test case 4: Invalid email format
        payload_invalid_email_format = {
            "email": "invalid-email-format",  # Invalid email format
            "password": "testpassword"
        }

        response = self.client.post(
            self.login_url,
            data=payload_invalid_email_format,
            format='json'
        )

        print("Login Response (Invalid Email Format):", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

        # Test case 5: Non-existent email
        payload_nonexistent_email = {
            "email": "nonexistent@example.com",  # Non-existent email
            "password": "testpassword"
        }

        response = self.client.post(
            self.login_url,
            data=payload_nonexistent_email,
            format='json'
        )

        print("Login Response (Non-existent Email):", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

        # Test case 6: Missing email field
        payload_missing_email = {
            "password": "testpassword"  # Missing email field
        }

        response = self.client.post(
            self.login_url,
            data=payload_missing_email,
            format='json'
        )

        print("Login Response (Missing Email):", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

        # Test case 7: Missing password field
        payload_missing_password = {
            "email": "testuser@example.com"  # Missing password field
        }

        response = self.client.post(
            self.login_url,
            data=payload_missing_password,
            format='json'
        )

        print("Login Response (Missing Password):", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

        # Test case 8: Incorrect email and password
        payload_incorrect_email_password = {
            "email": "wronguser@example.com",  # Incorrect email
            "password": "wrongpassword"  # Incorrect password
        }

        response = self.client.post(
            self.login_url,
            data=payload_incorrect_email_password,
            format='json'
        )

        print("Login Response (Incorrect Email and Password):", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_reset_password_send_valid_email(self):
        """
        Test sending a password reset email with a valid email.
        """
        payload = {
            "email": "testuser@example.com"
        }

        # Make the POST request
        response = self.client.post(
            self.reset_password_send_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Reset Password Send Response (Valid Email):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the response message
        self.assertEqual(response.data["message"], "Reset password email send")

    def test_reset_password_send_invalid_email(self):
        """
        Test sending a password reset email with an invalid email.
        """
        payload = {
            "email": "nonexistent@example.com"  # Email does not exist in the database
        }

        # Make the POST request
        response = self.client.post(
            self.reset_password_send_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Reset Password Send Response (Invalid Email):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the error message
        self.assertIn("email", response.data)

    def test_reset_password_send_empty_email(self):
        """
        Test sending a password reset email with an empty email.
        """
        payload = {
            "email": ""  # Empty email
        }

        # Make the POST request
        response = self.client.post(
            self.reset_password_send_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Reset Password Send Response (Empty Email):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the error message
        self.assertIn("email", response.data)

    def test_create_new_user_missing_email(self):
        """
        Test creating a new user with missing email.
        """
        payload = {
            "first_name": "Admin",
            "last_name": "User",
            "role": self.role.id
        }

        # Make the POST request
        response = self.client.post(
            self.create_new_user_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Create New User Response (Missing Email):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the error message
        self.assertIn("email", response.data)

    def test_create_new_user_invalid_email(self):
        """
        Test creating a new user with an invalid email.
        """
        payload = {
            "email": "invalid-email",  # Invalid email format
            "first_name": "Admin",
            "last_name": "User",
            "role": self.role.id
        }

        # Make the POST request
        response = self.client.post(
            self.create_new_user_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Create New User Response (Invalid Email):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the error message
        self.assertIn("email", response.data)

    def test_create_new_user_missing_role(self):
        """
        Test creating a new user with missing role.
        """
        payload = {
            "email": "newadmin@example.com",
            "first_name": "Admin",
            "last_name": "User"
        }

        # Make the POST request
        response = self.client.post(
            self.create_new_user_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Create New User Response (Missing Role):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the error message
        self.assertIn("role", response.data)

    def test_create_new_user_invalid_role(self):
        """
        Test creating a new user with an invalid role.
        """
        payload = {
            "email": "newadmin@example.com",
            "first_name": "Admin",
            "last_name": "User",
            "role": 999  # Invalid role ID
        }

        # Make the POST request
        response = self.client.post(
            self.create_new_user_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Create New User Response (Invalid Role):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the error message
        self.assertIn("role", response.data)

    def test_create_new_user_valid_data(self):
        """
        Test creating a new user with valid data.
        """
        payload = {
            "email": "newadmin@example.com",
            "first_name": "Admin",
            "last_name": "User",
            "role": self.role.id
        }

        # Make the POST request
        response = self.client.post(
            self.create_new_user_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Create New User Response (Valid Data):", response.data)
        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert the response message
        self.assertEqual(response.data["message"], "New user has been successfully created!")

    def test_update_profile_info_valid_data(self):
        """
        Test updating profile info with valid data.
        """
        # Create a dummy file for testing
        # profile_picture = SimpleUploadedFile(
        #     name="profile.jpg",
        #     content=b"file_content",
        #     content_type="image/jpeg"
        # )

        payload = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": 'testuser@example.com'
        }

        # Make the PUT request
        response = self.client.put(
            self.update_profile_info_url,
            data=payload,
            format='multipart'
        )

        # Print the response data for debugging
        print("Update Profile Info Response (Valid Data):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh the user instance from the database
        self.user.refresh_from_db()

        # Assert the updated fields
        self.assertEqual(self.user.first_name, "Jane")
        self.assertEqual(self.user.last_name, "Smith")

    def test_update_profile_info_invalid_data(self):
        """
        Test updating profile info with invalid data.
        """
        payload = {
            "first_name": "",  # Empty first name
            "last_name": "",  # Empty last name
            "avatar": "invalid_file",  # Invalid file
            "email": '',
        }

        # Make the PUT request
        response = self.client.put(
            self.update_profile_info_url,
            data=payload,
            format='multipart'
        )

        # Print the response data for debugging
        print("Update Profile Info Response (Invalid Data):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the error messages
        self.assertIn("email", response.data)

    def test_update_profile_info_missing_data(self):
        """
        Test updating profile info with missing data.
        """
        payload = {}  # Empty payload

        # Make the PUT request
        response = self.client.put(
            self.update_profile_info_url,
            data=payload,
            format='multipart'
        )

        # Print the response data for debugging
        print("Update Profile Info Response (Missing Data):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_get_user_permissions(self):
        """
        Test retrieving user permissions.
        """
        # Make the GET request
        response = self.client.get(self.user_permissions_url)

        # Print the response data for debugging
        print("User Permissions Response:", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_list(self):
        """
        Test retrieving a list of users.
        """
        # Make the GET request
        response = self.client.get(self.user_list)

        # Print the response data for debugging
        print("User List Response:", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_user_role_valid_data(self):
        """
        Test setting a user role with valid data.
        """
        payload = {
            "email": "testuser@example.com",
            "groups": [self.role.id]
        }

        # Make the POST request
        response = self.client.post(
            self.set_user_role_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Set User Role Response (Valid Data):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_user_role_invalid_email(self):
        """
        Test setting a user role with an invalid email.
        """
        payload = {
            "email": "nonexistent@example.com",  # Invalid email
            "groups": [self.role.id]
        }

        # Make the POST request
        response = self.client.post(
            self.set_user_role_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Set User Role Response (Invalid Email):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_set_user_role_missing_email(self):
        """
        Test setting a user role with a missing email.
        """
        payload = {
            "email": '',
            "groups": [self.role.id]  # Missing email
        }

        # Make the POST request
        response = self.client.post(
            self.set_user_role_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Set User Role Response (Missing Email):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_set_user_role_invalid_role(self):
        """
        Test setting a user role with an invalid role.
        """
        payload = {
            "email": "testuser@example.com",
            "groups": [999]  # Invalid role ID
        }

        # Make the POST request
        response = self.client.post(
            self.set_user_role_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Set User Role Response (Invalid Role):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the error message
        self.assertIn("groups", response.data)

    def test_set_user_role_unauthenticated(self):
        """
        Test setting a user role without authentication.
        """
        # Log out the admin user
        self.client.logout()

        payload = {
            "email": "testuser@example.com",
            "groups": [self.role.id]
        }

        # Make the POST request
        response = self.client.post(
            self.set_user_role_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Set User Role Response (Unauthenticated):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_user_role_non_admin(self):
        """
        Test setting a user role as a non-admin user.
        """
        # Authenticate a non-admin user
        self.client.force_authenticate(user=self.user)

        payload = {
            "email": "test@example.com",
            "groups": [self.role.id]
        }

        # Make the POST request
        response = self.client.post(
            self.set_user_role_url,
            data=payload,
            format='json'
        )
        # Print the response data for debugging
        print("Set User Role Response (Non-Admin):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_users_valid_email(self):
        """
        Test searching users with a valid email.
        """
        # Add a query parameter
        url = f"{self.search_users_url}?email=rakibislam@boomdevs.com"

        # Make the GET request
        response = self.client.get(url)

        # Print the response data for debugging
        print("Search Users Response (Valid Email):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_roles_list(self):
        """
        Test retrieving a list of roles.
        """
        # Make the GET request
        response = self.client.get(self.roles_list_url)

        # Print the response data for debugging
        print("Roles List Response:", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_role_valid_data(self):
        """
        Test creating a role with valid data.
        """
        payload = {
            "name": "Role",
            "is_admin": False,
            "is_default": False,
            "description": "This is a test role.",
            "permissions": [self.permission1.id, self.permission2.id]
        }

        # Make the POST request
        response = self.client.post(
            self.roles_list_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Create Role Response (Valid Data):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_role_missing_name(self):
        """
        Test creating a role with a missing name.
        """
        payload = {
            "is_admin": False,
            "is_default": False,
            "description": "This is a test role.",
            "permissions": [self.permission1.id, self.permission2.id]
        }

        # Make the POST request
        response = self.client.post(
            self.roles_list_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Create Role Response (Missing Name):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the error message
        self.assertIn("name", response.data)

    def test_create_role_invalid_permissions(self):
        """
        Test creating a role with invalid permissions.
        """
        payload = {
            "name": "Test Role",
            "is_admin": False,
            "is_default": False,
            "description": "This is a test role.",
            "permissions": [999]  # Invalid permission ID
        }

        # Make the POST request
        response = self.client.post(
            self.roles_list_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Create Role Response (Invalid Permissions):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert the error message
        self.assertIn("permissions", response.data)

    def test_create_role_unauthenticated(self):
        """
        Test creating a role without authentication.
        """
        # Log out the admin user
        self.client.logout()

        payload = {
            "name": "Test Role",
            "is_admin": False,
            "is_default": False,
            "description": "This is a test role.",
            "permissions": [self.permission1.id, self.permission2.id]
        }

        # Make the POST request
        response = self.client.post(
            self.roles_list_url,
            data=payload,
            format='json'
        )

        # Print the response data for debugging
        print("Create Role Response (Unauthenticated):", response.data)

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
