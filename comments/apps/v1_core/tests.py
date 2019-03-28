import json
from functools import partial

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

# Create your tests here.
from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from apps.v1_core.models import Comment, Reply
from apps.v1_core.views import CommentAPIView

User = get_user_model()

class TestCommentModel(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="test", email='user@test.com', password='foo'
        )
        self.comment_data = {
            'content': 'this is a comment',
            'user': self.user
        }

    def test_instance_is_being_created(self):
        before_creation = Comment.objects.count()
        instance = Comment.objects.create(**self.comment_data)
        after_creation = Comment.objects.count()
        self.assertGreater(after_creation, before_creation)
        self.assertEqual(instance.user.email, self.user.email)
        self.assertEqual(instance.content, self.comment_data['content'])


class TestReplyModel(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='userreply@test.com', password='foo')
        self.comment = Comment.objects.create(
            content="this is a comment", user=self.user)
        self.reply_data = {
            'content': 'this is a reply to the comment',
            'comment': self.comment,
        }

    def test_create_reply_instance(self):
        instance = Reply.objects.create(**self.reply_data)
        self.assertEqual(instance.content, self.reply_data['content'])


class APIViewBaseTest(APITestCase):

    def setUp(self):

        self.user = User.objects.create(
            email='user@test.com', password='foo')


class SubmitCommentTestCase(APIViewBaseTest):

    def setUp(self):
        super().setUp()
        self.comment_data = {
            'content': 'this is a comment',
            'user': self.user.id}


    def test_user_able_to_submit_comment(self):
        before_request = Comment.objects.count()
        response = self.client.post('/api/comment/', data=self.comment_data, follow=True)
        after_request = Comment.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(after_request, before_request)

class UpdateCommentTestCase(APIViewBaseTest):

    def setUp(self):
        super().setUp()
        self.comment_data = {
            'content': 'this is a comment',
            'user': self.user
        }
        self.put_data = {'content':'updated_comment'}

    def test_user_able_to_update_comment(self):
        instance = Comment.objects.create(**self.comment_data)
        response = self.client.patch(f'/api/comment/{instance.id}/', self.put_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.data['response'], 'updated')
        self.assertEqual(Comment.objects.get(pk=instance.id).content, self.put_data['content'])
        self.assertNotEqual(Comment.objects.get(pk=instance.id).content, self.comment_data['content'])

class DeleteCommentTestCase(APIViewBaseTest):

    def setUp(self):
        super().setUp()
        self.comment_data = {
            'content': 'this is a comment',
            'user': self.user
        }

    def test_user_able_to_delete_comment(self):
        instance = Comment.objects.create(**self.comment_data)
        counter_before_request = Comment.objects.count()
        response = self.client.delete(f'/api/comment/{instance.id}/', follow=True)
        counter_after_request = Comment.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(counter_after_request, (counter_before_request-1))

class FetchCommentTestCase(APIViewBaseTest):

    def setUp(self):
        super().setUp()
        self.other_user = User.objects.create(username='other', email='other@test.com', password='moo')
        self.comments = [
            {'content': 'this is a comment 1', 'user': self.user},
            {'content': 'this is a comment 2', 'user': self.user},
            {'content': 'this is a comment 3', 'user': self.user},
            {'content': 'this is a comment 4', 'user': self.user},
            {'content': 'this is a comment 5', 'user': self.other_user},
            {'content': 'this is a comment 6', 'user': self.other_user},
            {'content': 'this is a comment 7', 'user': self.other_user},
        ]

        for comment in self.comments:
            Comment.objects.create(**comment)

    def test_get_all_comments(self):
        response = self.client.get('/api/comment/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 7)

