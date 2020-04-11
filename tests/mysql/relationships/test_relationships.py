import os
import unittest

from src.masonite.orm.models import Model
from src.masonite.orm.relationships import belongs_to, has_many

if os.getenv("RUN_MYSQL_DATABASE", False) == "True":

    class Profile(Model):
        __table__ = "profiles"

    class Articles(Model):
        __table__ = "articles"

        @belongs_to("id", "article_id")
        def logo(self):
            return Logo

    class Logo(Model):
        __table__ = "logos"

    class User(Model):

        _eager_loads = ()

        @belongs_to("id", "user_id")
        def profile(self):
            return Profile

        @has_many("id", "user_id")
        def articles(self):
            return Articles

        def get_is_admin(self):
            return "You are an admin"

    class TestRelationships(unittest.TestCase):
        maxDiff = None

        def test_relationship_can_be_callable(self):
            self.assertEqual(
                User.profile().where("name", "Joe").to_sql(),
                "SELECT * FROM `profiles` WHERE `profiles`.`name` = 'Joe'",
            )

        def test_can_access_relationship(self):
            for user in User.where("id", 1).get():
                self.assertIsInstance(user.profile, Profile)
                print(user.profile.city)

        def test_can_access_has_many_relationship(self):
            user = User.hydrate(User.where("id", 1).first())
            self.assertEqual(len(user.articles), 4)

        def test_can_access_relationship_multiple_times(self):
            user = User.hydrate(User.where("id", 1).first())
            self.assertEqual(len(user.articles), 4)
            self.assertEqual(len(user.articles), 4)

        def test_loading(self):
            users = User.with_("articles").get()
            for user in users:
                print(user)
                # print(user.articles)

        def test_casting(self):
            users = User.with_("articles").where("is_admin", 1).get()
            for user in users:
                print(user.is_admin)
                # self.assertIs(user.is_admin, True)
                # print(user.articles)

        def test_setting(self):
            users = User.with_("articles").where("is_admin", 1).get()
            for user in users:
                user.name = "Joe"
                user.is_admin = 1
                user.save()

        def test_relationship_has(self):
            to_sql = User.has("articles").to_sql()
            self.assertEqual(
                to_sql,
                "SELECT * FROM `users` WHERE EXISTS ("
                "SELECT * FROM `articles` WHERE `articles`.`user_id` = `users`.`id`"
                ")",
            )

        def test_relationship_multiple_has(self):
            to_sql = User.has("articles", "profile").to_sql()
            self.assertEqual(
                to_sql,
                "SELECT * FROM `users` WHERE EXISTS ("
                "SELECT * FROM `articles` WHERE `articles`.`user_id` = `users`.`id`"
                ") AND EXISTS ("
                "SELECT * FROM `profiles` WHERE `profiles`.`user_id` = `users`.`id`"
                ")",
            )

            count = User.has("articles", "profile").get().count()
            self.assertEqual(count, 2)

        def test_nested_has(self):
            to_sql = User.has("articles.logo").to_sql()
            self.assertEqual(
                to_sql,
                "SELECT * FROM `users` WHERE EXISTS (SELECT * FROM `articles` WHERE `articles`.`user_id` = `users`.`id` AND EXISTS (SELECT * FROM `logos` WHERE `logos`.`article_id` = `articles`.`id`))",
            )

            count = User.has("articles.logo").get().count()
            self.assertEqual(count, 2)