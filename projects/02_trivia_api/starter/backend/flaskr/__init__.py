import os
from flask import Flask, request, abort, jsonify,json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
# generate random integer values
from random import seed
from random import choice

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection ]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app= Flask(__name__)
  setup_db(app)
  db = SQLAlchemy(app)
 

  '''@TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs'''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response 

  '''@TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/List')
  def retrieve_all_categories():
    try:
      questions = Question.query.all()
      current_questions = [question.format() for question in selection ]

      if len(current_questions) == 0:
        # or no question Available 
        abort(404)

      return jsonify({
      'success': True,
      'current_questions': current_questions,
      'total_questions': len(questions)
      })

    except:
      abourt(422)


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_all():
    questions = Question.query.all()
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
    'success': True,
    'current_questions': current_questions,
    'total_questions': len(questions),
    'current category': questions[0].category

    })




  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    question= Question.query.filter(Question.id==id).one_or_none()

    if question is None: 
      abort(404)
    
    Question.delete(question)

    questions = Question.query.all()
    current_questions = paginate_questions(request, questions)
    
    return jsonify({
    'success': True,
    'current_questions': current_questions,
    'total_questions': len(questions)
    })




  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/newquestions', methods=['POST'])
  def new_question():

    body=request.get_json()
    new_question=body.get('question',None)
    new_answer=body.get('answer',None)
    new_difficulty=int(body.get('difficulty',None))
    new_category=int(body.get('category',None))

    try:
      question= Question(question=new_question ,answer=new_answer,difficulty=new_difficulty,category=new_category)
      question.insert()
      
      questions = Question.query.all()
      current_questions = paginate_questions(request, questions)



      return jsonify({
        'success': True,
        'created':question.id,
        'current_questions': current_questions,
        'total_questions': len(questions)
        })

    except:
      abort(422)
  


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/search', methods=['POST'])
  def search_questions():

    body = request.get_json()
    try:
    
        search_term= request.args.get('search_term','',type=str)
        result = Question.query.filter(Question.question.ilike('%'+ search_term +'%')).all()
        current_questions = paginate_questions(request, result)
        
        if len(current_questions) == 0:
          abort(404)
        
        return jsonify({
          'success': True,
          'current_questions': current_questions,
          'total_result': len(result)
          })

    except:
      abort(422)
     
    

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/category/<int:id>')
  def retrieve_by_category(id):
    questions = Question.query.filter(Question.category==id).all()
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
    'success': True,
    'current_questions': current_questions,
    'total_questions': len(questions)
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/play', methods=['POST'])
  def play_questions():
    # from the catagory 
    catagory= request.args.get('catagory','',type=int)
    questions_in_category = Question.query.filter(Question.category==catagory).all()
    total_questions=len(questions_in_category)
    # random 
    quiz={'22','20'}
    found = False
    while (not found):
      selected_question= questions_in_category[random.randrange(0, total_questions, 1)]
      # check if used 
      for q in quiz:
        if (q == selected_question.id):
          break
        else:
          found=True
          return selected_question.format()

     
  
     # list of this game qustion 
     
    

     
	

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    