from django.db import IntegrityError
from django.utils import timezone
from users.models import User
from main.paginators import HabitPaginator
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from main.permissions import IsOwner
from celery.contrib import pytest
from main.serializers import HabitSerializer
from config.settings import TELEGRAM_URL, TELEGRAM_TOKEN
from main.services import send_tg_message
from datetime import timedelta
from unittest import mock
from main.models import Habit
from main.validators import RelatedHabitValidator, DurationTimeHabitValidator, RewardHabitValidator, \
    PleasentHabitValidator
from unittest import TestCase
from main.validators import RegularityHabitValidator
from rest_framework.serializers import ValidationError


class HabitTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='last.chance.20@mail.ru', password='123456')


def test_habit_creation_with_missing_required_fields(self):
    with self.assertRaises(IntegrityError):
        Habit.objects.create(
            user=None,
            place='',
            time=None,
            action='',
            is_pleasent=False,
            associated_habit=None,
            frequency='',
            frequency_in_days=None,
            reward='',
            time_doing=None,
            is_public=False
        )


def test_habit_creation_with_associated_habit_not_exist(self):
    with self.assertRaises(IntegrityError):
        Habit.objects.create(
            user=self.user,
            place='Home',
            time=timezone.now().time(),
            action='Reading',
            is_pleasent=True,
            associated_habit=Habit.objects.create(
                user=self.user,
                place='Work',
                time=timezone.now().time(),
                action='Workout',
                is_pleasent=False,
                associated_habit=None,
                frequency='daily',
                frequency_in_days=5,
                reward='Medal',
                time_doing=timezone.timedelta(minutes=45),
                is_public=True
            ),
            frequency='daily',
            frequency_in_days=5,
            reward='Book',
            time_doing=timezone.timedelta(minutes=30),
            is_public=True
        )


def test_habit_creation_with_monthly_frequency_and_frequency_in_days_not_null(self):
    with self.assertRaises(ValidationError):
        Habit.objects.create(
            user=self.user,
            place='Home',
            time=timezone.now().time(),
            action='Reading',
            is_pleasent=True,
            associated_habit=None,
            frequency='monthly',
            frequency_in_days=5,
            reward='Book',
            time_doing=timezone.timedelta(minutes=30),
            is_public=True
        )


def test_habit_creation_with_reward_null_but_is_pleasent_true(self):
    habit = Habit.objects.create(
        user=self.user,
        place='Home',
        time=timezone.now().time(),
        action='Reading',
        is_pleasent=True,
        associated_habit=None,
        frequency='daily',
        frequency_in_days=5,
        reward=None,
        time_doing=timezone.timedelta(minutes=30),
        is_public=True
    )
    self.assertEqual(habit.action, 'Reading')
    self.assertEqual(habit.place, 'Home')
    self.assertEqual(habit.user, self.user)
    self.assertTrue(habit.is_pleasent)
    self.assertIsNone(habit.associated_habit)
    self.assertEqual(habit.frequency, 'daily')
    self.assertEqual(habit.frequency_in_days, 5)
    self.assertIsNone(habit.reward)
    self.assertEqual(habit.time_doing, timezone.timedelta(minutes=30))
    self.assertTrue(habit.is_public)


def test_habit_creation_with_time_doing_exceeding_maximum_allowed_duration(self):
    with self.assertRaises(ValidationError):
        Habit.objects.create(
            user=self.user,
            place='Home',
            time=timezone.now().time(),
            action='Reading',
            is_pleasent=True,
            associated_habit=None,
            frequency='daily',
            frequency_in_days=5,
            reward='Book',
            time_doing=timezone.timedelta(hours=25),  # Exceeding maximum allowed duration
            is_public=True
        )


def test_habit_retrieval_with_valid_user_id(self):
    user = User.objects.create_user(username='testuser', password='testpassword')
    habit = Habit.objects.create(
        user=user,
        place='Home',
        time=timezone.now().time(),
        action='Reading',
        is_pleasent=True,
        associated_habit=None,
        frequency='daily',
        frequency_in_days=5,
        reward='Book',
        time_doing=timezone.timedelta(minutes=30),
        is_public=True
    )
    retrieved_habit = Habit.objects.get(user=user.id)
    self.assertEqual(retrieved_habit.action, habit.action)
    self.assertEqual(retrieved_habit.place, habit.place)
    self.assertEqual(retrieved_habit.user, habit.user)
    self.assertEqual(retrieved_habit.is_pleasent, habit.is_pleasent)
    self.assertEqual(retrieved_habit.associated_habit, habit.associated_habit)
    self.assertEqual(retrieved_habit.frequency, habit.frequency)
    self.assertEqual(retrieved_habit.frequency_in_days, habit.frequency_in_days)
    self.assertEqual(retrieved_habit.reward, habit.reward)
    self.assertEqual(retrieved_habit.time_doing, habit.time_doing)
    self.assertEqual(retrieved_habit.is_public, habit.is_public)


def test_habit_retrieval_with_invalid_user_id(self):
    with self.assertRaises(User.DoesNotExist):
        Habit.objects.get(user=999999)  # Invalid user ID    


def test_habit_update_with_valid_changes(self):
    habit = Habit.objects.create(
        user=self.user,
        place='Home',
        time=timezone.now().time(),
        action='Reading',
        is_pleasent=True,
        associated_habit=None,
        frequency='daily',
        frequency_in_days=5,
        reward='Book',
        time_doing=timezone.timedelta(minutes=30),
        is_public=True
    )

    updated_habit_data = {
        'place': 'Work',
        'time': timezone.now().time(),
        'action': 'Workout',
        'is_pleasent': False,
        'associated_habit': None,
        'frequency': 'weekly',
        'frequency_in_days': 3,
        'reward': 'Medal',
        'time_doing': timezone.timedelta(minutes=45),
        'is_public': False
    }

    habit.place = updated_habit_data['place']
    habit.time = updated_habit_data['time']
    habit.action = updated_habit_data['action']
    habit.is_pleasent = updated_habit_data['is_pleasent']
    habit.associated_habit = updated_habit_data['associated_habit']
    habit.frequency = updated_habit_data['frequency']
    habit.frequency_in_days = updated_habit_data['frequency_in_days']
    habit.reward = updated_habit_data['reward']
    habit.time_doing = updated_habit_data['time_doing']
    habit.is_public = updated_habit_data['is_public']
    habit.save()

    updated_habit = Habit.objects.get(pk=habit.id)
    self.assertEqual(updated_habit.place, updated_habit_data['place'])
    self.assertEqual(updated_habit.time, updated_habit_data['time'])
    self.assertEqual(updated_habit.action, updated_habit_data['action'])
    self.assertEqual(updated_habit.is_pleasent, updated_habit_data['is_pleasent'])
    self.assertEqual(updated_habit.associated_habit, updated_habit_data['associated_habit'])
    self.assertEqual(updated_habit.frequency, updated_habit_data['frequency'])
    self.assertEqual(updated_habit.frequency_in_days, updated_habit_data['frequency_in_days'])
    self.assertEqual(updated_habit.reward, updated_habit_data['reward'])
    self.assertEqual(updated_habit.time_doing, updated_habit_data['time_doing'])
    self.assertEqual(updated_habit.is_public, updated_habit_data['is_public'])


def test_habit_paginator_default_page_size():
    # Arrange
    paginator = HabitPaginator()
    factory = APIRequestFactory()
    request = factory.get('/habits/')

    # Act
    paginated_response = paginator.paginate_queryset(None, request)

    # Assert
    assert paginator.page_size == len(paginated_response)


def test_habit_paginator_negative_page_size():
    paginator = HabitPaginator()
    paginator.page_size = -5
    assert paginator.page_size == 5, "Negative page_size should be set to default value"

    def test_denies_access_if_user_is_not_owner(self):
        request = self.factory.get('/habits/1/')
        request.user = self.user2
        self.assertFalse(self.permission.has_object_permission(request, None, self.habit))


def test_is_owner_allows_access_if_user_is_the_owner():
    # Arrange
    user = UserFactory()
    habit = HabitFactory(user=user)
    request = RequestFactory().get('/')
    request.user = user
    permission = IsOwner()

    # Act
    result = permission.has_object_permission(request, None, habit)

    # Assert
    assert result is True


def test_is_owner_denies_access_if_not_authenticated():
    client = APIClient()
    habit = Habit.objects.create(user=None, name='Test Habit')  # Create a habit without a user
    response = client.get(f'/habits/{habit.id}/')  # Perform a request to the habit detail view
    assert response.status_code == status.HTTP_401_UNAUTHORIZED  # Check if the response status code is 401 (Unauthorized)


def test_is_owner_without_habit_object():
    factory = APIRequestFactory()
    user = User.objects.create(username='testuser')
    request = factory.get('/habits/')
    request.user = user

    # Act
    permission = IsOwner()

    # Assert
    assert not permission.has_object_permission(request, None, None)


def test_is_owner_permission_different_user():
    # Create a different user
    different_user = User.objects.create_user(username='different_user')

    # Create a habit object associated with a different user
    habit = Habit.objects.create(user=different_user, name='Test Habit')

    # Create a request object with a different user
    factory = APIRequestFactory()
    request = factory.get('/api/habits/')
    request.user = different_user

    # Create an instance of IsOwner permission
    permission = IsOwner()

    # Act
    result = permission.has_object_permission(request, None, habit)

    # Assert
    assert result is False


def test_is_owner_different_habit():
    # Create a user and a habit associated with a different user
    user1 = User.objects.create(username='user1')
    user2 = User.objects.create(username='user2')
    habit = Habit.objects.create(user=user1, title='Test Habit')

    # Create a request with user2 as the authenticated user
    factory = APIRequestFactory()
    request = factory.get('/habits/1/')
    request.user = user2

    # Instantiate the permission class and check object permission
    permission = IsOwner()
    assert not permission.has_object_permission(request, None, habit)


def test_reward_not_empty_when_associated_habit_provided():
    habit = Habit(reward="Test Reward", associated_habit="Test Habit")
    serializer = HabitSerializer(instance=habit)
    assert RewardHabitValidator(field1="reward", field2="associated_habit").validate(serializer.validated_data) is None


def test_error_when_associated_habit_not_provided_but_reward_is():
    habit = Habit(reward="Test Reward", associated_habit=None)
    serializer = HabitSerializer(instance=habit)
    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert str(e.value) == "Reward and associated habit cannot both be empty."


def test_associated_habit_cannot_be_a_habit_itself():
    habit = Habit(reward="Test Reward", associated_habit="Test Habit")
    serializer = HabitSerializer(instance=habit)
    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert str(e.value) == "Associated habit cannot be a habit itself."


def test_time_doing_is_positive_integer():
    habit = Habit(time_doing=10)
    serializer = HabitSerializer(instance=habit)
    assert DurationTimeHabitValidator(field="time_doing").validate(serializer.validated_data) is None


def test_error_when_time_doing_not_provided():
    habit = Habit(reward="Test Reward", associated_habit="Test Habit", time_doing=None)
    serializer = HabitSerializer(instance=habit)
    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert str(e.value) == "Time doing must be provided."


def test_is_pleasent_is_boolean():
    habit = Habit(reward="Test Reward", associated_habit="Test Habit", is_pleasent="True")
    serializer = HabitSerializer(instance=habit)
    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert str(e.value) == "is_pleasent must be a boolean value."


def test_error_when_is_pleasent_not_provided():
    habit = Habit(reward="Test Reward", associated_habit="Test Habit", time_doing=30, frequency_in_days=7)
    serializer = HabitSerializer(instance=habit)
    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert str(e.value) == "is_pleasent field is required."


def test_error_when_frequency_in_days_not_provided():
    habit = Habit(reward="Test Reward", associated_habit="Test Habit", time_doing=30, is_pleasent=True)
    serializer = HabitSerializer(data=habit.__dict__)
    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert str(e.value) == "Frequency in days must be provided."


def test_all_fields_provided_and_valid():
    habit = Habit(reward="Test Reward", associated_habit="Test Habit", time_doing=30, is_pleasent=True,
                  frequency_in_days=7)
    serializer = HabitSerializer(instance=habit)
    assert serializer.is_valid() is True


class TestSendTgMessage(TestCase):
    @mock.patch('main.services.requests.get')
    def test_send_tg_message_success(self, mock_get):
        chat_id = 123456789
        message = "Hello, this is a test message"
        expected_url = f'{TELEGRAM_URL}{TELEGRAM_TOKEN}/sendMessage'
        expected_params = {'text': message, 'chat_id': chat_id}

        send_tg_message(chat_id, message)

        mock_get.assert_called_once_with(expected_url, params=expected_params)


def test_send_tg_message_missing_chat_id():
    with mock.patch('main.services.requests.get') as mock_get:
        mock_get.return_value.status_code = 400
        mock_get.return_value.json.return_value = {'description': 'Bad Request: chat not found'}

        chat_id = None
        message = 'Test message'

        try:
            send_tg_message(chat_id, message)
        except Exception as e:
            assert str(e) == 'Bad Request: chat not found'
        else:
            assert False, 'Expected an exception to be raised'


class TestSendTgMessage(TestCase):
    def test_send_tg_message_missing_message(self):
        chat_id = 123456789
        message = None

        with self.assertRaises(TypeError):
            send_tg_message(chat_id, message)


class RewardHabitValidatorTestCase(TestCase):
    def setUp(self):
        self.validator = RewardHabitValidator('related_habit', 'reward')

    def test_raise_validation_error_when_both_related_habit_and_reward_are_provided(self):
        data = {'related_habit': 'some_related_habit', 'reward': 'some_reward'}
        with self.assertRaises(ValidationError) as cm:
            self.validator(data)
        self.assertEqual(
            str(cm.exception),
            "Невозможен одновременный выбор связанной привычки и указания вознаграждения."
        )


class RewardHabitValidatorTestCase(TestCase):
    def test_should_not_raise_validation_error_when_only_related_habit_provided(self):
        validator = RewardHabitValidator('reward', 'related_habit')
        data = {'related_habit': 'Test related habit'}
        try:
            validator(data)
        except ValidationError as e:
            self.fail(f"ValidationError was raised: {e}")


class RewardHabitValidatorTestCase(TestCase):
    def test_raises_validation_error_when_related_habit_and_reward_are_empty_strings(self):
        validator = RewardHabitValidator('related_habit', 'reward')
        data = {'related_habit': '', 'reward': ''}
        with self.assertRaises(ValidationError) as cm:
            validator(data)
        self.assertEqual(
            cm.exception.detail,
            "Невозможен одновременный выбор связанной привычки и указания вознаграждения."
        )


class RewardHabitValidatorTestCase(TestCase):
    def setUp(self):
        self.validator = RewardHabitValidator('related_habit', 'reward')

    def test_raises_validation_error_when_related_habit_is_provided_as_none(self):
        value = {'related_habit': None, 'reward': 'some reward'}
        with self.assertRaises(ValidationError) as cm:
            self.validator(value)
        self.assertEqual(
            cm.exception.detail,
            "Невозможен одновременный выбор связанной привычки и указания вознаграждения."
        )


class RewardHabitValidatorTestCase(TestCase):
    def setUp(self):
        self.validator = RewardHabitValidator('reward', 'related_habit')

    def test_raise_validation_error_when_reward_is_provided(self):
        data = {'reward': None, 'related_habit': 'habit1'}
        with self.assertRaises(ValidationError) as cm:
            self.validator(data)
        self.assertEqual(
            str(cm.exception),
            "Невозможен одновременный выбор связанной привычки и указания вознаграждения."
        )


def test_reward_habit_validator_related_habit_as_number():
    validator = RewardHabitValidator('related_habit', 'reward')
    value = {'related_habit': 123, 'reward': None}
    try:
        validator(value)
    except ValidationError as e:
        assert str(e) == "Невозможен одновременный выбор связанной привычки и указания вознаграждения."
    else:
        assert False, "ValidationError was not raised"


def test_reward_habit_validator_raises_validation_error_when_reward_is_provided_as_number():
    validator = RewardHabitValidator('reward', 'related_habit')
    data = {'reward': 100, 'related_habit': None}
    with self.assertRaises(ValidationError) as cm:
        validator(data)
    self.assertEqual(
        cm.exception.message,
        "Невозможен одновременный выбор связанной привычки и указания вознаграждения."
    )


class RewardHabitValidatorTestCase(TestCase):
    def setUp(self):
        self.validator = RewardHabitValidator('related_habit', 'reward')


def test_related_habit_validator_should_not_raise_error_when_related_habit_is_pleasant():
    validator = RelatedHabitValidator('related_habit')
    related_habit = MagicMock()
    related_habit.is_pleasent = True
    data = {'related_habit': related_habit}
    validator(data)


def test_related_habit_validator_empty_string():
    validator = RelatedHabitValidator('related_habit')
    habit = {'related_habit': ''}
    try:
        validator(habit)
    except ValidationError as e:
        assert str(e) == "В связанные привычки могут попадать только привычки с признаком приятной привычки."
    else:
        assert False, "ValidationError was not raised"


class TestDurationTimeHabitValidator(TestCase):
    def setUp(self):
        self.validator = DurationTimeHabitValidator('duration')

    def test_valid_timedelta_within_limit(self):
        value = {'duration': timedelta(seconds=119)}
        self.validator(value)

    def test_invalid_timedelta_exceeding_limit(self):
        value = {'duration': timedelta(seconds=121)}
        with self.assertRaises(ValidationError):
            self.validator(value)


class TestDurationTimeHabitValidator(TestCase):
    def test_duration_time_habit_validator_with_different_field_names(self):
        # Test with different field names
        validator1 = DurationTimeHabitValidator('execution_time')
        validator2 = DurationTimeHabitValidator('duration')

        # Test with valid input
        self.assertIsNone(validator1({'execution_time': timedelta(seconds=100)}))
        self.assertIsNone(validator2({'duration': timedelta(seconds=100)}))

        # Test with invalid input
        with self.assertRaises(ValidationError):
            validator1({'execution_time': timedelta(seconds=121)})

        with self.assertRaises(ValidationError):
            validator2({'duration': timedelta(seconds=121)})


class TestDurationTimeHabitValidator(TestCase):
    def setUp(self):
        self.validator = DurationTimeHabitValidator('duration_time')

    def test_valid_timedelta_value(self):
        value = {'duration_time': timedelta(minutes=1)}
        self.validator(value)

    def test_invalid_timedelta_value_minutes(self):
        value = {'duration_time': timedelta(minutes=3)}
        with self.assertRaises(ValidationError) as cm:
            self.validator(value)
        self.assertEqual(str(cm.exception), "Время выполнения должно быть не больше 120 секунд")

    def test_invalid_timedelta_value_hours(self):
        value = {'duration_time': timedelta(hours=1)}
        with self.assertRaises(ValidationError) as cm:
            self.validator(value)
        self.assertEqual(str(cm.exception), "Время выполнения должно быть не больше 120 секунд")


class TestDurationTimeHabitValidator(TestCase):
    def test_negative_timedelta_value(self):
        validator = DurationTimeHabitValidator('duration_time')
        value = {'duration_time': -timedelta(seconds=10)}
        with self.assertRaises(ValidationError) as cm:
            validator(value)
        self.assertEqual(str(cm.exception), "Время выполнения должно быть не больше 120 секунд")


def test_duration_time_habit_validator_non_timedelta():
    # Arrange
    validator = DurationTimeHabitValidator("duration")
    value = {"duration": "120"}  # Non-timedelta value

    # Act
    with mock.patch("main.validators.dict") as mock_dict:
        mock_dict.return_value = value
        with self.assertRaises(ValidationError) as cm:
            validator(value)

    # Assert
    self.assertEqual(
        str(cm.exception), "['Время выполнения должно быть не больше 120 секунд']"
    )


class TestDurationTimeHabitValidator(TestCase):
    def setUp(self):
        self.validator = DurationTimeHabitValidator('duration')

    def test_non_dict_input(self):
        with self.assertRaises(ValidationError) as cm:
            self.validator(123)
        self.assertEqual(str(cm.exception), "Expected a dictionary, but got <class 'int'>.")

    def test_duration_exceeds_limit(self):
        with self.assertRaises(ValidationError) as cm:
            self.validator({'duration': timedelta(seconds=121)})
        self.assertEqual(str(cm.exception), "Время выполнения должно быть не больше 120 секунд")

    def test_duration_within_limit(self):
        self.validator({'duration': timedelta(seconds=119)})


class TestDurationTimeHabitValidator(TestCase):
    def test_empty_dictionary(self):
        validator = DurationTimeHabitValidator('duration')
        value = {}
        validator(value)
        # No exception raised, test passes


def test_duration_time_habit_validator_missing_field():
    validator = DurationTimeHabitValidator("duration_time")
    input_data = {"habit_name": "Test Habit"}
    try:
        validator(input_data)
    except ValidationError as e:
        assert str(e) == "Время выполнения должно быть не больше 120 секунд"
    else:
        assert False, "ValidationError was not raised"


class PleasentHabitValidatorTestCase(TestCase):
    def setUp(self):
        self.validator = PleasentHabitValidator('is_pleasent')

    def test_pleasent_habit_validator_raises_validation_error_with_reward_and_related_habit(self):
        input_data = {
            'is_pleasent': True,
            'reward': 'some reward',
            'related_habit': 'some related habit'
        }
        with self.assertRaises(ValidationError) as cm:
            self.validator(input_data)
        self.assertEqual(
            str(cm.exception),
            "У приятной привычки не может быть вознаграждения или связанной привычки."
        )


class PleasentHabitValidatorTestCase(TestCase):
    def test_pleasent_habit_validator_should_not_raise_error_when_reward_is_none_and_related_habit_is_present(self):
        validator = PleasentHabitValidator('is_pleasent')
        input_data = {
            'is_pleasent': True,
            'reward': None,
            'related_habit': 'related_habit_id'
        }
        validator(input_data)


def test_pleasent_habit_validator_reward_present_related_habit_none():
    validator = PleasentHabitValidator('is_pleasent')
    input_data = {
        'is_pleasent': True,
        'reward': 'some reward',
        'related_habit': None
    }
    try:
        validator(input_data)
    except ValidationError as e:
        assert False, f'ValidationError was raised: {str(e)}'


def test_pleasent_habit_validator_no_reward_no_related_habit():
    validator = PleasentHabitValidator("is_pleasent")
    input_data = {"is_pleasent": True, "reward": None, "related_habit": None}
    try:
        validator(input_data)
    except ValidationError as e:
        assert False, f"ValidationError was raised: {str(e)}"


class PleasentHabitValidatorTestCase(TestCase):
    def setUp(self):
        self.validator = PleasentHabitValidator('is_pleasent')

    def test_raises_validation_error_when_reward_and_related_habit_are_present(self):
        input_data = {
            'is_pleasent': True,
            'reward': 'some reward',
            'related_habit': 'some related habit',
        }
        with self.assertRaises(ValidationError) as cm:
            self.validator(input_data)
        self.assertEqual(
            str(cm.exception),
            "У приятной привычки не может быть вознаграждения или связанной привычки."
        )

    def test_does_not_raise_validation_error_when_reward_and_related_habit_are_not_present(self):
        input_data = {
            'is_pleasent': True,
        }
        self.validator(input_data)


class TestPleasentHabitValidator(TestCase):
    def setUp(self):
        self.validator = PleasentHabitValidator("is_pleasent")

    def test_valid_combinations(self):
        # Test valid combinations with additional fields
        valid_data = {
            "is_pleasent": True,
            "reward": None,
            "related_habit": None,
            "extra_field": "some_value"
        }
        self.validator(valid_data)  # No ValidationError should be raised


def test_pleasent_habit_validator_raises_error_with_reward_and_related_habit():
    validator = PleasentHabitValidator('is_pleasent')
    input_data = {
        'is_pleasent': True,
        'reward': 'Reward 1',
        'related_habit': 'Related Habit 1',
    }
    with self.assertRaises(ValidationError) as cm:
        validator(input_data)
    self.assertEqual(
        cm.exception.message,
        "У приятной привычки не может быть вознаграждения или связанной привычки."
    )


def test_pleasent_habit_validator_with_reward_and_related_habit():
    validator = PleasentHabitValidator('is_pleasent')
    value = {
        'is_pleasent': True,
        'reward': 'some reward',
        'related_habit': 'some related habit'
    }
    with self.assertRaises(ValidationError) as cm:
        validator(value)
    self.assertEqual(
        cm.exception.message,
        "У приятной привычки не может быть вознаграждения или связанной привычки."
    )


class PleasentHabitValidatorTestCase(TestCase):
    def setUp(self):
        self.validator = PleasentHabitValidator('is_pleasent')

    def test_pleasent_habit_with_reward_and_related_habit(self):
        data = {
            'is_pleasent': True,
            'reward': 'some reward',
            'related_habit': 'some related habit',
        }
        with self.assertRaises(ValidationError) as cm:
            self.validator(data)
        self.assertEqual(
            cm.exception.detail,
            "У приятной привычки не может быть вознаграждения или связанной привычки."
        )


class PleasentHabitValidatorTestCase(TestCase):
    def test_pleasent_habit_validator_with_reward_and_related_habit(self):
        validator = PleasentHabitValidator('is_pleasent')
        data = {
            'is_pleasent': True,
            'reward': 'Some reward',
            'related_habit': 'Some related habit'
        }
        with self.assertRaises(ValidationError) as cm:
            validator(data)
        self.assertEqual(
            cm.exception.detail,
            ["У приятной привычки не может быть вознаграждения или связанной привычки."]
        )


class RegularityHabitValidatorTestCase(TestCase):
    def test_should_raise_validation_error_when_frequency_in_days_is_less_than_1(self):
        validator = RegularityHabitValidator('frequency_in_days')
        value = {'frequency_in_days': 0}

        with self.assertRaises(ValidationError) as cm:
            validator(value)

        self.assertEqual(str(cm.exception), "Нельзя выполнять привычку реже, чем 1 раз в 7 дней.")


class RegularityHabitValidatorTestCase(TestCase):
    def setUp(self):
        self.validator = RegularityHabitValidator('frequency_in_days')


def test_regularity_habit_validator_frequency_1():
    validator = RegularityHabitValidator('frequency_in_days')
    value = {'frequency_in_days': 1}
    try:
        validator(value)
    except ValidationError as e:
        assert str(e) == "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."
    else:
        assert True


class TestRegularityHabitValidator(TestCase):
    def test_should_not_raise_validation_error_when_frequency_in_days_is_exactly_7(self):
        validator = RegularityHabitValidator('frequency_in_days')
        value = {'frequency_in_days': 7}
        validator(value)


def test_regularity_habit_validator_case_insensitive_field_names():
    validator = RegularityHabitValidator("frequency_in_days")
    data = {"FREQUENCY_IN_DAYS": 3}
    validator(data)
    data = {"frequency_in_days": 0}
    with pytest.raises(ValidationError) as e:
        validator(data)
    assert str(e.value) == "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."
    data = {"frequency_in_days": 8}
    with pytest.raises(ValidationError) as e:
        validator(data)
    assert str(e.value) == "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."
