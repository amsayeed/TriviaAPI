import random
from flask import (
    request,
    Flask,
    abort,
    jsonify,
    flash
)
from flask_cors import CORS

from models import (
    setup_db,
    Question,
    Category,
    Questions_schema,
    paginate
)


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/*/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.set('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        return response

    @app.route('/categories')
    def categories():
        all_categories = Category.get(Category)
        if all_categories:
            categories_result = {}
            for cat in all_categories:
                categories_result[cat.id] = cat.type
            return jsonify({
                'success': True,
                'categories': categories_result
            }), 200
        else:
            abort(404)

    @app.route('/questions')
    def all_questions():
        categories_result = {}
        categories = Category.query.all()
        for category in categories:
            categories_result[category.id] = category.type
        questions_list = Question.query.all()
        if questions_list:
            questions_result = Questions_schema.dump(questions_list)
            questions = paginate(request, questions_result)
            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(questions_list),
                'categories': categories_result,
                'currentCategory': None
            }), 200
        else:
            abort(404)

    @app.route("/questions/<question_id>", methods=['DELETE'])
    def del_question(question_id):
        question = Question.query.filter_by(id=question_id).first()
        if question:
            try:
                question.delete()
                return jsonify({
                    'success': True,
                    'deleted': question_id
                }), 200
            except:
                abort(422)
        else:
            abort(404)

    @app.route("/questions", methods=['POST'])
    def add_question():
        data = request.get_json()
        if data is None:
            abort(406)
        if not ("question" in data and "answer" in data and "difficulty" in data and "category" in data):
            abort(422)
        question_valid = Question.query.filter_by(question=data.get('question')).first()
        if question_valid:
            abort(409)
        else:
            try:
                question = Question(question=data.get('question'),
                                    answer=data.get('answer'),
                                    difficulty=data.get('difficulty'),
                                    category=data.get('category'))
                question.insert()
                return jsonify({
                    'success': True,
                    'created': question.id,
                }), 201
            except:
                abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search():
        data = request.get_json()
        if data is None:
            abort(406)
        if not ("searchTerm" in data):
            abort(422)
        search_term = data.get('searchTerm', None)
        search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        if search_results:
            result = Questions_schema.dump(search_results)
            return jsonify({
                'success': True,
                'questions': result,
                'total_questions': len(search_results),
                'current_category': None
            })
        else:
            abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def questions_per_category(category_id):
        cat_id = str(category_id)
        questions = Question.query.filter(Question.category == cat_id).all()
        if questions:
            questions_result = Questions_schema.dump(questions)
            return jsonify({
                'success': True,
                'questions': questions_result,
                'total_questions': len(questions_result),
                'current_category': category_id
            }), 200
        else:
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def quiz():
        data = request.get_json()
        # >> {previous_questions: [], quiz_category: {type: "click", id: "1"}}
        if data is None:
            abort(406)
        if not ("quiz_category" in data and "previous_questions" in data):
            abort(422)
        try:
            quiz_cat = data.get('quiz_category')
            previous = data.get('previous_questions')
            if quiz_cat['type'] != 'click':
                available_questions = Question.query.filter_by(category=quiz_cat['id']).filter(
                    Question.id.notin_(previous)).all()
            else:
                available_questions = Question.query.filter(Question.id.notin_(previous)).all()
            new_question = available_questions[random.randrange(0, len(available_questions))].format() if len(
                available_questions) > 0 else None
            return jsonify({
                'success': True,
                'question': new_question
            }), 200
        except:
            abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "The browser (or proxy) sent a request that this server could not understand"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "error": 401,
            "message": "Unauthorized Page"
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "success": False,
            "error": 403,
            "message": "Access to the requested resource is forbidden"
        }), 403

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(405)
    def invalid_method(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405

    @app.errorhandler(409)
    def duplicate_resource(error):
        return jsonify({
            "success": False,
            "error": 409,
            "message": "The request could not be completed due to a conflict"
        }), 409

    @app.errorhandler(406)
    def not_accepted(error):
        return jsonify({
            "success": False,
            "error": 406,
            "message": "Not Accepted Request"
        }), 406

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app
