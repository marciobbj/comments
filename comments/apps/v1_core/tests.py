import datetime

from apps.v1_core.models import Comment
from apps.v1_core.models import Reply
from apps.v1_core.serializers import CommentSerializer
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APITestCase
# Create your tests here.

User = get_user_model()


class TestCommentModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user@test.com', password='thisisapassword',
        )
        self.comment_data = {
            'content': 'this is a comment',
            'user': self.user,
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
        self.user = User.objects.create_user(
            username='userreply@test.com', password='thisisapassword',
        )
        self.comment = Comment.objects.create(
            content='this is a comment', user=self.user,
        )
        self.reply_data = {
            'content': 'this is a reply to the comment',
            'comment': self.comment,
        }

    def test_create_reply_instance(self):
        instance = Reply.objects.create(**self.reply_data)
        self.assertEqual(instance.content, self.reply_data['content'])


class APIViewBaseTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user@test.com', password='thisisapassword',
        )


class SubmitCommentTestCase(APIViewBaseTest):

    def setUp(self):
        super().setUp()
        self.comment_data = {
            'content': 'this is a comment',
            'user': self.user.id,
        }

    def test_user_able_to_submit_comment(self):
        self.client.login(username='user@test.com', password='thisisapassword')
        before_request = Comment.objects.count()
        response = self.client.post(
            '/api/comment/', data=self.comment_data, follow=True,
        )
        after_request = Comment.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(after_request, before_request)


class UpdateCommentTestCase(APIViewBaseTest):

    def setUp(self):
        super().setUp()
        self.comment_data = {
            'content': 'this is a comment',
            'user': self.user,
        }
        self.put_data = {'content': 'updated_comment'}

    def test_user_able_to_update_comment(self):
        self.client.login(username='user@test.com', password='thisisapassword')
        instance = Comment.objects.create(**self.comment_data)
        response = self.client.patch(
            f'/api/comment/{instance.id}/', self.put_data, follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.data['content'], self.put_data['content'])
        self.assertEqual(
            Comment.objects.get(
                pk=instance.id,
            ).content, self.put_data['content'],
        )
        self.assertNotEqual(
            Comment.objects.get(
                pk=instance.id,
            ).content, self.comment_data['content'],
        )


class DeleteCommentTestCase(APIViewBaseTest):

    def setUp(self):
        super().setUp()
        self.comment_data = {
            'content': 'this is a comment',
            'user': self.user,
        }

    def test_user_able_to_delete_comment(self):
        self.client.login(username='user@test.com', password='thisisapassword')
        instance = Comment.objects.create(**self.comment_data)
        counter_before_request = Comment.objects.count()
        response = self.client.delete(
            f'/api/comment/{instance.id}/', follow=True,
        )
        counter_after_request = Comment.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(counter_after_request, (counter_before_request - 1))


class FetchCommentTestCase(APIViewBaseTest):

    def setUp(self):
        super().setUp()
        self.other_user = User.objects.create_user(
            username='other@test.com', password='thisisapassword',
        )
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

    def test_not_authenticated_permissions(self):
        response = self.client.get('/api/comment/', follow=True)
        self.assertEqual(response.status_code, 403)

    def test_get_all_comments(self):
        self.client.login(
            username='other@test.com',
            password='thisisapassword',
        )
        response = self.client.get('/api/comment/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.comments))

    def test_get_all_comments_user_1(self):
        self.client.login(
            username='other@test.com',
            password='thisisapassword',
        )
        response = self.client.get(
            '/api/comment/', {'search': 'other@test.com'}, follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_get_all_comments_user_2(self):
        self.client.login(username='user@test.com', password='thisisapassword')
        response = self.client.get(
            '/api/comment/', {'search': 'user@test.com'}, follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

    def test_get_latest_comments(self):
        self.client.login(username='user@test.com', password='thisisapassword')
        for i in range(1, 8):
            post_date = datetime.datetime.now() + datetime.timedelta(seconds=4)

            Comment.objects.create(
                content=f'Comment day {i}',
                user=self.other_user,
                created_at=post_date,
            )

        params = {'ordering': '-created_at'}
        response = self.client.get(
            '/api/comment/', params, follow=True,
        )
        serializer = CommentSerializer(
            Comment.objects.all().order_by('-created_at'), many=True,
        )
        result_expected = JSONRenderer().render(serializer.data)

        self.assertEqual(result_expected, response.content)

    def test_get_comments_from_specific_user(self):
        self.client.login(username='user@test.com', password='thisisapassword')
        for i in range(1, 8):
            post_date = datetime.datetime.now() + datetime.timedelta(seconds=4)

            Comment.objects.create(
                content=f'Comment day {i}',
                user=self.other_user,
                created_at=post_date,
            )

        params = {'ordering': 'user'}
        response = self.client.get(
            '/api/comment/', params, follow=True,
        )
        serializer = CommentSerializer(
            Comment.objects.all().order_by('user'), many=True,
        )
        result_expected = JSONRenderer().render(serializer.data)

        self.assertEqual(result_expected, response.content)

    def test_get_older_comments(self):
        self.client.login(username='user@test.com', password='thisisapassword')
        for i in range(1, 8):
            post_date = datetime.datetime.now() + datetime.timedelta(seconds=4)

            Comment.objects.create(
                content=f'Comment day {i}',
                user=self.other_user,
                created_at=post_date,
            )

        params = {'ordering': 'created_at'}
        response = self.client.get(
            '/api/comment/', params, follow=True,
        )
        serializer = CommentSerializer(
            Comment.objects.all().order_by('created_at'), many=True,
        )
        result_expected = JSONRenderer().render(serializer.data)
        self.assertEqual(result_expected, response.content)


class ReplyAPITestCase(APIViewBaseTest):

    def setUp(self):
        super().setUp()
        self.comment = Comment.objects.create(
            content='this is a comment',
            user=self.user,
        )
        self.reply_data = {
            'content': 'this is a reply to the comment',
            'comment': self.comment.id,
        }
        self.put_data = {
            'content': 'this is the updated reply',
        }
        User.objects.create_user(
            username='reply@test.com', password='thisisapassword',
        )

    def test_user_able_to_submit_reply(self):
        self.client.login(
            username='reply@test.com',
            password='thisisapassword',
        )
        response = self.client.post(
            '/api/reply/', data=self.reply_data, follow=True,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_able_to_update_reply(self):
        self.client.login(
            username='reply@test.com',
            password='thisisapassword',
        )
        reply = Reply.objects.create(
            content='this is a reply to the comment',
            comment=self.comment,
        )
        response = self.client.patch(
            f'/api/reply/{reply.id}/', self.put_data, follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.data['content'], self.put_data['content'])
        self.assertEqual(
            Reply.objects.get(
                pk=reply.id,
            ).content, self.put_data['content'],
        )
        self.assertNotEqual(
            Comment.objects.get(
                pk=reply.id,
            ).content, self.reply_data['content'],
        )

    def test_user_able_to_delete_reply(self):
        self.client.login(
            username='reply@test.com',
            password='thisisapassword',
        )
        reply = Reply.objects.create(
            content='this is a reply to the comment',
            comment=self.comment,
        )
        counter_before_request = Reply.objects.count()
        response = self.client.delete(
            f'/api/comment/{reply.id}/', follow=True,
        )
        counter_after_request = Reply.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(counter_after_request, (counter_before_request - 1))


class TestLikeUpdateView(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='like@test.com', password='thisisapassword',
        )
        self.comment = Comment.objects.create(
            content='this awesome comment',
            user=self.user,
        )
        self.reply_data = {
            'content': 'this is a reply to the comment',
            'comment': self.comment,
        }
        self.reply = Reply.objects.create(
            content='reply to this comment',
            comment=self.comment,
        )

    def test_value_comment_like_change_at_request(self):
        self.client.login(username='like@test.com', password='thisisapassword')
        before = self.comment.likes_comments
        response = self.client.put(
            f'/api/comment/{self.comment.id}/like', data={'user': self.user.id},  # NOQA
        )
        after = response.data['likes_comments']
        self.assertEqual(after, (before + 1))
        self.assertEqual(response.status_code, 200)

    def test_value_reply_like_change_at_request(self):
        self.client.login(username='like@test.com', password='thisisapassword')
        before = self.reply.likes_replies
        response = self.client.put(
            f'/api/reply/{self.reply.id}/like', data={'comment': self.comment.id},  # NOQA
        )
        after = response.data['likes_replies']
        self.assertEqual(after, (before + 1))
        self.assertEqual(response.status_code, 200)
