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


  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    questions = [question.format() for question in selection ]
    current_questions = questions[start:end]
    return current_questions

  '''@TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
        
  @app.route('/categories')
  def retrieve_all_categories():
    try:
      # retrive all categories from database 
      categories= Category.query.all()

    # create categories dict and add categories in proper format 
      categories_dict = {}
      for category in categories:
        categories_dict[category.id] = category.type

      if len(categories_dict) == 0:
        abort(404)
      
    
      return jsonify({
        'success': True,
        'categories': categories_dict
      })

    except:
      abort(422)


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
    #page = request.args.get('page', 1, type=int)

    # retrave all questions and paginate 
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)


    # create categories dict and add categories in proper format 
    categories= Category.query.all()
    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type
    
    if len(categories_dict) == 0:
      abort(404)

    

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': categories_dict

    })




  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    # get the question object by id 
    question= Question.query.filter(Question.id==id).one_or_none()

    # make sure object exist in database
    if question is None: 
      abort(404)

    #delete the question
    Question.delete(question)

    # get all exist questions to update the view
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, questions)
    
    return jsonify({
    'success': True,
    'current_questions': current_questions,
    'total_questions': len(questions),
    'deleted': id
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

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=['POST'])
  def search_and_creat_question ():
    # since creat question and search are ussing the same route and method are the same the are merged 


    # get the data from request body  
    body = request.get_json()
    search_term = body.get('searchTerm')
    new_question = body.get('question',None)
    new_answer = body.get('answer',None)
    new_difficulty =int(body.get('difficulty',1)) 
    new_category = int(body.get('category',1))
  

    # if POST request has search_term perform search 
    if (search_term):
        result = Question.query.filter(Question.question.ilike('%'+ search_term +'%')).all()
        current_questions = paginate_questions(request, result)
        
        # if no question match the search tearm 
        if len(result) == 0:
          abort(404)
        
        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(result)
          }),200
    else:
      # if POST request has new question data add new question
      # make sure all fields is not null 
      if ((new_question is None) or (new_answer is None)or (new_difficulty is None) or (new_category is None)):
        abort(422)

      try:
        # creat new question object and add it to the database 
        question_object= Question(question=new_question ,answer=new_answer,difficulty=new_difficulty,category=new_category)
        question_object.insert()

        # get all exist questions to update the view
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        return jsonify({
          'success': True,
          'created':question_object.id,
          'question_created': question_object.question,
          'questions': current_questions,
          'total_questions': len(questions),
        
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
  @app.route('/categories/<int:id>/questions')
  def retrieve_by_category(id):

     # make sure id is an int 
     category_id = int(id)

     # make sure category exist in database 
     current_category = Category.query.filter_by(id=category_id).one_or_none()   
     if current_category is None :
       abort(404)
 
     # get questions in selected category
     questions = Question.query.filter_by(category=category_id).all()
     current_questions = paginate_questions(request, questions)

     if len(current_questions) == 0:
       abort(404)

     return jsonify({
       'success': True,
       'questions': current_questions,
       'total_questions': len(questions),
       'current_category':current_category.type
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

  @app.route('/quizzes', methods=['POST'])
  def get_random_quiz_question():

    # to be called later in the method
    def is_used(new_question):
        Found = False
        for question in previous_questions:
            if (question == new_question.id):
                Found = True
                break
  
        return Found






    # method body start here 
    # get info from request body  
    body = request.get_json()
    previous_questions = body.get('previous_questions')
    category = body.get('quiz_category')

    # make sure all fields is not null 
    if ((category is None) or (previous_questions is None)):
        abort(404)
    
    # make sure id is an int 
    category_id = int(category['id'])
    #  case: all questions is selected id=0 
    if (category_id == 0):
        questions = Question.query.all()
   
    else:
        # case : spicific category is selected  
        questions = Question.query.filter_by(category=category_id).all()


    # get total number of questions for both cases 
    total_questions_in_category= len(questions)

     # get random question
    question = questions[random.randrange(0, total_questions_in_category, 1)]

    # check if question is used or select new one 
    while (is_used(question)):
        question = questions[random.randrange(0, total_questions_in_category, 1)]

        # if all questions in the category have been asked and no new questions to ask thes case occure when questions in category less than 5 questions
        if (len(previous_questions) == total_questions_in_category):
          return jsonify({
             'success': True
             })
    # if new and unused question have found 
    return jsonify({
        'success': True,
        'question': question.format(),

    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404


  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
      }), 400

        
  return app

    

          