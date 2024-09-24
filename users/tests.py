from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from users.views import UserViewSet
from rest_framework import status
from rest_framework_simplejwt.settings import api_settings
from users.serializers import MyTokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from users.serializers import UserSerializer
from users.models import User
from rest_framework.test import APITestCase

NULLABLE = {"blank": True, "null": True}


class UserModelTest(TestCase):
    def test_email_format_for_valid_emails(self):
        valid_emails = ['test@example.com', 'test.email+tag@example.com', '1234567890@example.com']
        for email in valid_emails:
            user = User(email=email)
            self.assertTrue(user.is_valid(), f'Invalid email format for {email}')


def test_large_phone_number():
    user = User(email="test@example.com", phone_number="123456789012345678901234567890")
    user.full_clean()  # This will raise ValidationError if the phone number is too long


class UserModelTest(TestCase):
    def test_phone_number_cannot_be_empty(self):
        user = User.objects.create(email="test@example.com")
        user.phone_number = ""
        with self.assertRaises(ValueError):
            user.full_clean()


class UserModelTest(TestCase):
    def test_country_name_length(self):
        user = User(email="test@example.com", country="A" * 101)
        with self.assertRaises(ValueError):
            user.full_clean()


class UserModelTest(TestCase):
    def test_user_should_not_allow_empty_avatar(self):
        # Arrange
        empty_file = SimpleUploadedFile("empty.jpg", b"", content_type="image/jpeg")
        user = User(email="test@example.com", phone_number="1234567890", country="Test Country",
                    avatar=empty_file, tg_chat_id="12345")

        # Act
        with self.assertRaises(ValueError):
            user.full_clean()


class UserModelTest(TestCase):
    def test_tg_chat_id_format(self):
        user = User.objects.create(email="test@example.com", tg_chat_id="123456789")
        self.assertEqual(user.tg_chat_id, "123456789")


def test_my_token_obtain_pair_serializer_with_valid_credentials():
    # Create a user
    user = User.objects.create_user(username='test_user', email='test_user@example.com', password='test_password')

    # Serialize the user
    serializer = MyTokenObtainPairSerializer(data={'username': 'test_user', 'password': 'test_password'})
    serializer.is_valid(raise_exception=True)

    # Get the token
    token = serializer.get_token(user)

    # Assert the token contains the expected fields
    assert 'username' in token
    assert 'email' in token
    assert token['username'] == 'test_user'
    assert token['email'] == 'test_user@example.com'


def test_invalid_user_credentials():
    serializer = MyTokenObtainPairSerializer(data={'username': 'invalid', 'password': 'invalid'})
    serializer.is_valid(raise_exception=True)

    # The following line should raise a ValidationError
    assert serializer.validated_data  # This line will fail if the ValidationError is not raised


def test_token_lifetime_negative_value():
    # Set negative value for TOKEN_LIFETIME
    api_settings.TOKEN_LIFETIME = -1

    # Create a user
    user = User.objects.create(email='testuser@example.com')

    # Attempt to obtain a token
    serializer = MyTokenObtainPairSerializer(data={})
    serializer.is_valid(raise_exception=True)

    # Assert that an error is raised when obtaining a token with negative TOKEN_LIFETIME
    with pytest.raises(ValidationError):
        serializer.get_token(user)


def test_my_token_obtain_pair_serializer():
    user = User.objects.create(username='test_user', email='test@example.com', password='test_password')
    serializer = MyTokenObtainPairSerializer.get_token(user)
    assert 'username' in serializer.data
    assert 'email' in serializer.data
    assert serializer.data['username'] == 'test_user'
    assert serializer.data['email'] == 'test@example.com'


def test_get_token_with_user_fields():
    # Arrange
    user = User.objects.create(username='testuser', email='test@example.com')
    serializer = MyTokenObtainPairSerializer()

    # Act
    token = serializer.get_token(user)

    # Assert
    assert 'username' in token
    assert 'email' in token
    assert token['username'] == 'testuser'
    assert token['email'] == 'test@example.com'


def test_token_with_user_fields():
    # Create a user
    user = User.objects.create(username='testuser', email='test@example.com')

    # Obtain token with user fields
    serializer = MyTokenObtainPairSerializer()
    token = serializer.get_token(user)

    # Check if token contains user fields
    assert 'username' in token.data
    assert 'email' in token.data
    assert token.data['username'] == 'testuser'
    assert token.data['email'] == 'test@example.com'

    # Delete the user
    user.delete()

    # Recreate the user
    user = User.objects.create(username='testuser', email='test@example.com')

    # Obtain token with user fields again
    token = serializer.get_token(user)

    # Check if token still contains user fields
    assert 'username' in token.data
    assert 'email' in token.data
    assert token.data['username'] == 'testuser'
    assert token.data['email'] == 'test@example.com'


def test_get_token_with_social_account():
    # Arrange
    user = User.objects.create(username='test_user', email='test_user@example.com')
    social_account = SocialAccount.objects.create(user=user, provider='test_provider', uid='12345')
    serializer = MyTokenObtainPairSerializer(data={'social_account': social_account})
    serializer.is_valid(raise_exception=True)

    # Act
    token = serializer.get_token(user)

    # Assert
    assert 'username' in token
    assert 'email' in token
    assert token['username'] == 'test_user'
    assert token['email'] == 'test_user@example.com'


class UserSerializerTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user', email='test_user@example.com')

    def test_user_serializer_serializes_all_fields(self):
        serializer = UserSerializer(instance=self.user)
        data = serializer.data

        self.assertEqual(set(data.keys()), set(['id', 'username', 'email']))


def test_user_serializer_validates_input_data():
    # Arrange
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'TestPassword123!',
    }

    # Act
    serializer = UserSerializer(data=data)

    # Assert
    assert serializer.is_valid(), serializer.errors


def test_user_serializer_invalidates_missing_required_field():
    # Arrange
    data = {
        'email': 'testuser@example.com',
        'password': 'TestPassword123!',
    }

    # Act
    serializer = UserSerializer(data=data)

    # Assert
    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)

    assert 'username' in e.value.detail


def test_user_serializer_missing_model_field():
    # Given
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        # Missing 'password' field
    }

    # When
    serializer = UserSerializer(data=data)

    # Then
    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)

    assert 'password' in e.value.detail


def test_user_serializer_nested_relationships():
    # Create a user with nested relationships (e.g., foreign key, many-to-many)
    user = User.objects.create(username='test_user', email='test@example.com')

    # Serialize the user
    serializer = UserSerializer(user)

    # Assert that the serialized data contains the expected nested relationships
    assert 'username' in serializer.data
    assert 'email' in serializer.data
    # Add assertions for any nested relationships in the User model


class UserSerializerTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com')


def test_user_serializer_excludes_specific_fields():
    user = User.objects.create(username='testuser', email='test@example.com')
    serializer = UserSerializer(user, fields=('username',))
    assert set(serializer.data.keys()) == {'username'}


# Unit test for UserSerializer

def test_user_serializer_large_datasets():
    # Assuming we have a large dataset of users
    large_dataset = [User.objects.create(username=f'user{i}', email=f'user{i}@example.com') for i in range(1000)]

    # Serialize the large dataset
    serialized_data = UserSerializer(large_dataset, many=True).data

    # Assert that the number of serialized users matches the number in the dataset
    assert len(serialized_data) == len(large_dataset)

    # Clean up the created users
    for user in large_dataset:
        user.delete()


def test_user_serializer_handles_different_date_time_formats():
    # Arrange
    user = User.objects.create(username='test_user', email='test_user@example.com')
    user.date_of_birth = '1990-01-01'  # Example date format
    user.save()

    # Act
    serializer = UserSerializer(user)

    # Assert
    expected_fields = ['id', 'username', 'email', 'date_of_birth']
    assert set(serializer.data.keys()) == set(expected_fields)


def test_user_creation_with_duplicate_email():
    # Create a user with a known email
    User.objects.create(email='test@example.com', password='test123')

    # Create a client to simulate API requests
    client = APIClient()

    # Attempt to create a user with the same email
    response = client.post('/api/users/', {'email': 'test@example.com', 'password': 'test123'})

    # Assert that the request is unsuccessful due to duplicate email
    assert response.status_code == 400
    assert 'email' in response.data


def test_create_user_with_short_password():
    # Arrange
    serializer = UserSerializer(data={'username': 'testuser', 'password': 'short'})

    # Act
    serializer.is_valid(raise_exception=True)
    serializer.save(is_active=True)

    # Assert
    user = User.objects.get(username='testuser')
    assert len(user.password) >= 8, 'Password should be at least 8 characters long'


def test_user_creation_with_numeric_password():
    # Arrange
    serializer = UserSerializer(data={'username': 'testuser', 'password': '123456'})
    serializer.is_valid(raise_exception=True)

    # Act
    viewset = UserViewSet()
    viewset.perform_create(serializer)

    # Assert
    user = User.objects.get(username='testuser')
    assert not user.check_password('123456')


def test_create_user_with_only_letters_password():
    # Arrange
    serializer = UserSerializer(data={'username': 'testuser', 'password': 'abcdef'})

    # Act
    serializer.is_valid(raise_exception=True)
    serializer.save(is_active=True)
    user = User.objects.get(username='testuser')
    user.set_password(user.password)
    user.save()

    # Assert
    assert user.check_password('abcdef') is False


def test_user_creation_with_space_in_password():
    # Arrange
    serializer = UserSerializer(data={'username': 'testuser', 'password': 'test password'})
    serializer.is_valid(raise_exception=True)

    # Act
    viewset = UserViewSet()
    viewset.perform_create(serializer)

    # Assert
    user = User.objects.get(username='testuser')
    assert user is not None
    assert user.check_password('test password') is False


def test_user_password_not_equal_username():
    # Arrange
    username = "testuser"
    password = "testpassword"
    serializer = UserSerializer(data={"username": username, "password": password})

    # Act
    serializer.is_valid(raise_exception=True)
    user = serializer.save(is_active=True)
    user.set_password(user.password)
    user.save()

    # Assert
    assert user.username != user.password


def test_should_not_create_user_with_common_password():
    # Arrange
    serializer = UserSerializer(data={
        'username': 'testuser',
        'password': 'password123'  # Common password
    })
    serializer.is_valid(raise_exception=True)

    # Act
    viewset = UserViewSet()
    viewset.perform_create(serializer)

    # Assert
    assert User.objects.count() == 0
    assert serializer.instance.check_password('password123') is False


def test_create_user_with_guessable_password():
    # Arrange
    serializer = UserSerializer(data={
        'username': 'testuser',
        'password': 'password',
        'email': 'testuser@example.com'
    })
    serializer.is_valid(raise_exception=True)

    # Act
    viewset = UserViewSet()
    viewset.perform_create(serializer)

    # Assert
    created_user = User.objects.get(username='testuser')
    assert created_user.check_password('password') is False
