import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'root', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_q = {
            'question': 'New Test Question ?',
            'answer': 'Test Answer',
            'difficulty': '1',
            'category': '2'
        }

        self.duplicate_q = {
            'question': 'Test Question 2 ?',
            'answer': 'Test Answer',
            'difficulty': '1',
            'category': '2'
        }

        self.search_term = {
            'searchTerm': 'Test'
        }

        self.play = {'previous_questions': [],
                          'quiz_category': {'type': 'click', 'id': 1}}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_q(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['currentCategory'], None)

    def test_404_not_valid_page(self):
        response = self.client().get('/questions?page=2000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_post_categories(self):
        response = self.client().post('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)

    def test_del_q(self):
        response = self.client().delete('/questions/22')
        data = json.loads(response.data)

        q = Question.query.filter(Question.id == 22).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], '22')
        self.assertEqual(q, None)

    def test_error_404_del_q(self):
        response = self.client().delete('/questions/3')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_post_add_q(self):
        response = self.client().post('/questions', json=self.new_q)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_error_409_add_q(self):
        response = self.client().post('/questions', json=self.duplicate_q)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'The request could not be completed due to a conflict')

    def test_error_406_add_q(self):
        response = self.client().post('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 406)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Accepted Request')

    def test_post_search(self):
        response = self.client().post('/questions/search', json=self.search_term)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)

    def test_error_404_post_search(self):
        response = self.client().post('/questions/search', json={'searchTerm': 'NoMatch'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_per_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        questions = Question.query.filter(Question.category == 1).count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], questions)
        self.assertEqual(data['current_category'], 1)

    def test_error_404_questions_per_category(self):
        response = self.client().get('/categories/444/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_play_game(self):
        response = self.client().post('/quizzes', json=self.play)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_error_422_play_game(self):
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_error_406_play_game(self):
        response = self.client().post('/quizzes')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 406)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Accepted Request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
