import json

from datetime import timedelta
from unittest import mock

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from django.urls import reverse
from django.test.utils import override_settings
from django.contrib.auth import get_user_model

from ..factories import UserFactory, AdminFactory
from ..models import ActionToken

User = get_user_model()


class UsersTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.set_password('Test123!')
        self.user.save()

        self.admin = AdminFactory()
        self.admin.set_password('Test123!')
        self.admin.save()

    def test_create_new_student_user(self):
        """
        Ensure we can create a new user if we have the permission.
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': "M",
            'birthdate': "1999-11-11",
        }

        response = self.client.post(
            reverse('user-list'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content)['phone'], '1234567890')

        user = User.objects.get(email="John@mailinator.com")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertEqual(1, len(activation_token))

    def test_create_new_user(self):
        """
        Ensure we can create a new user if we have the permission.
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': "M",
            'birthdate': "1999-11-11",
        }

        response = self.client.post(
            reverse('user-list'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content)['phone'], '1234567890')

        user = User.objects.get(email="John@mailinator.com")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertEqual(1, len(activation_token))

    def test_create_new_user_blank_fields(self):
        """
        Ensure we can't create a new user with blank fields
        """
        data = {
            'email': '',
            'password': '',
            'phone': '',
            'first_name': '',
            'last_name': '',
            'gender': "",
            'birthdate': "",
        }

        response = self.client.post(
            reverse('user-list'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {
            'birthdate': [
                'Date has wrong format. Use one of these formats instead: '
                'YYYY[-MM[-DD]].'
            ],
            'first_name': ['This field may not be blank.'],
            'gender': ['"" is not a valid choice.'],
            'last_name': ['This field may not be blank.'],
            'email': ['This field may not be blank.'],
            'password': ['This field may not be blank.'],
            'phone': ['Invalid format.'],
        }
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_missing_fields(self):
        """
        Ensure we can't create a new user without required fields
        """
        data = {}

        response = self.client.post(
            reverse('user-list'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {
            'email': ['This field is required.'],
            'password': ['This field is required.']
        }
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_weak_password(self):
        """
        Ensure we can't create a new user with a weak password
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': '19274682736',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': "M",
            'birthdate': "1999-11-11",
        }

        response = self.client.post(
            reverse('user-list'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {"password": ['This password is entirely numeric.']}
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_invalid_fields(self):
        """
        Ensure we can't create a new user with invalid fields.
        Emails are validated at creation time, this is why no email validation
        messages are sent in this case.
        """
        data = {
            'username': 'John',
            'email': 'John@invalid.com',
            'password': '1927nce-736',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': "invalid_gender",
            'birthdate': "invalid_date",
        }

        response = self.client.post(
            reverse('user-list'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {
            'birthdate': [
                'Date has wrong format. Use one of these formats instead: '
                'YYYY[-MM[-DD]].'
            ],
            'gender': ['"invalid_gender" is not a valid choice.'],
        }
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_invalid_phone(self):
        """
        Ensure we can't create a new user with an invalid phone number
        """
        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': '1fasd6dq#$%',
            'phone': '12345',
            'other_phone': '23445dfg',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': "M",
            'birthdate': "1999-11-11",
        }

        response = self.client.post(
            reverse('user-list'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {
            "phone": ['Invalid format.'],
            "other_phone": ['Invalid format.']
        }
        self.assertEqual(json.loads(response.content), content)

    def test_create_new_user_duplicate_email(self):
        """
        Ensure we can't create a new user with an already existing email
        """

        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': "M",
            'birthdate': "1999-11-11",
        }

        user = UserFactory()
        user.email = data['email']
        user.save()

        response = self.client.post(
            reverse('user-list'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {
            'email': [
                "An account for the specified email address already exists."
            ]
        }
        self.assertEqual(json.loads(response.content), content)

    @override_settings(
        LOCAL_SETTINGS={
            "EMAIL_SERVICE": True,
            "AUTO_ACTIVATE_USER": False,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    @mock.patch('{{ cookiecutter.project_slug }}.views.IMailing')
    def test_create_user_activation_email(self, imailing):
        """
        Ensure that the activation email is sent when user signs up.
        """

        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': "M",
            'birthdate': "1999-11-11",
        }

        instance_imailing = imailing.create_instance.return_value
        instance_imailing.send_templated_email.return_value = {
            "code": "success",
        }

        response = self.client.post(
            reverse('user-list'),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content)['phone'], '1234567890')

        user = User.objects.get(email="John@mailinator.com")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertFalse(user.is_active)
        self.assertEqual(1, len(activation_token))

    @override_settings(
        LOCAL_SETTINGS={
            "EMAIL_SERVICE": True,
            "AUTO_ACTIVATE_USER": False,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    @mock.patch('{{ cookiecutter.project_slug }}.views.IMailing')
    def test_create_user_activation_email_failure(self, imailing):
        """
        Ensure that the user is notified that no email was sent.
        """

        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': "M",
            'birthdate': "1999-11-11",
        }

        instance_imailing = imailing.create_instance.return_value
        instance_imailing.send_templated_email.return_value = {
            "code": "failure",
        }

        response = self.client.post(
            reverse('user-list'),
            data,
            format='json',
        )

        content = {
            'detail': "The account was created but no email was "
                      "sent. If your account is not activated, "
                      "contact the administration.",
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), content)

        user = User.objects.get(email="John@mailinator.com")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertFalse(user.is_active)
        self.assertEqual(1, len(activation_token))

    @override_settings(
        LOCAL_SETTINGS={
            "EMAIL_SERVICE": True,
            "AUTO_ACTIVATE_USER": True,
            "FRONTEND_INTEGRATION": {
                "ACTIVATION_URL": "fake_url",
            }
        }
    )
    @mock.patch('{{ cookiecutter.project_slug }}.views.IMailing')
    def test_create_user_auto_activate(self, imailing):
        """
        Ensure that the user is automatically activated.
        """

        data = {
            'username': 'John',
            'email': 'John@mailinator.com',
            'password': 'test123!',
            'phone': '1234567890',
            'first_name': 'Chuck',
            'last_name': 'Norris',
            'gender': "M",
            'birthdate': "1999-11-11",
        }

        instance_imailing = imailing.create_instance.return_value
        instance_imailing.send_templated_email.return_value = {
            "code": "failure",
        }

        response = self.client.post(
            reverse('user-list'),
            data,
            format='json',
        )

        content = {
            'detail': "The account was created but no email was "
                      "sent. If your account is not activated, "
                      "contact the administration.",
        }

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), content)

        user = User.objects.get(email="John@mailinator.com")
        activation_token = ActionToken.objects.filter(
            user=user,
            type='account_activation',
        )

        self.assertTrue(user.is_active)
        self.assertEqual(1, len(activation_token))

    def test_list_users(self):
        """
        Ensure we can list all users.
        """
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse('user-list'))
        self.assertEqual(json.loads(response.content)['count'], 2)

        first_user = json.loads(response.content)['results'][0]
        self.assertEqual(first_user['email'], self.user.email)

        # Check the system doesn't return attributes not expected
        attributes = [
            'id',
            'url',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'phone',
            'other_phone',
            'is_superuser',
            'is_staff',
            'last_login',
            'date_joined',
            'gender',
            'birthdate',
            'groups',
            'user_permissions',
        ]
        for key in first_user.keys():
            self.assertTrue(
                key in attributes,
                'Attribute "{0}" is not expected but is '
                'returned by the system.'.format(key)
            )
            attributes.remove(key)

        # Ensure the system returns all expected attributes
        self.assertTrue(
            len(attributes) == 0,
            'The system failed to return some '
            'attributes : {0}'.format(attributes)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_without_authenticate(self):
        """
        Ensure we can't list users without authentication.
        """
        response = self.client.get(reverse('user-list'))

        content = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_without_permissions(self):
        """
        Ensure we can't list users without permissions.
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('user-list'))

        content = {
            'detail': 'You do not have permission to perform this action.'
        }
        self.assertEqual(json.loads(response.content), content)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
