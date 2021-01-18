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
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('noura.@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is the longest river in the world ? ',
            'answer': 'The Nile',
            'difficulty': 3,
            'category': 1
        }


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

    """
    get categories 
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])


    def test_404_get_categories(self):
        res = self.client().get('/categoriess')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404) 
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    '''
    Play Quiz
    '''
    def test_play_quiz(self):
        results = self.client().post('/quizzes', json={"previous_questions": [], "quiz_category": {"type": "Science", "id": "1"}})
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue('question')
    
    def test_404_play_quiz(self):
        results = self.client().post('/quizzes', json={"previous_questions": [], "quiz_category": None})
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')
    
    '''
    Search
    '''
    def test_search(self):
        results = self.client().post('/questions', json={'searchTerm': 'title'})
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        #self.assertTrue(len(data['questions']))
    
    def test_404_search(self):
        results = self.client().post('/questions', json={'searchTerm': 'aaaaa'})
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Not Found')



    '''
    Get Questions
    '''

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200) 
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories']) 
    
    
 
    def test_404_get_questions_beyond_pages(self):
        # back
        res = self.client().get('/questions?page=404')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404) 
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Not Found')

    '''
    Delete Question
    '''

    def test_delete_question(self):
        res = self.client().delete('/questions/32')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 32).one_or_none()
        self.assertEqual(res.status_code, 200) 
        self.assertEqual(data['success'], True)
        self.assertTrue(data['current_questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['deleted'], 32)
        self.assertEqual(question, None)


    def test_404_delete_question(self):
        #back
        res = self.client().delete('/questions/404')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404) 
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')
    
    '''
    Create Question
    '''
    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200) 
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['question_created'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
    
    def test_422_create_question(self):
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422) 
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable') 
    
   
    
    '''
    Get Question in Category
    '''
    def test_get_questions_in_category(self):
        results = self.client().get('/categories/1/questions')
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'])
        self.assertEqual(data['total_questions'])
        self.assertEqual(data['current_category'])


    
    def test_get_questions_in_category(self):
        results = self.client().get('/categories/8/questions')
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 404)
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()