from django.test import TestCase
from django.contrib.auth import get_user_model

# Create your tests here.
from apps.v1_core.models import Comment, Reply

User = get_user_model()

class TestCommentModel(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='user@test.com', password='foo'
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