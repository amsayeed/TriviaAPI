
from flask import app , abort
from sqlalchemy import Column, String, Integer, create_engine, func
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow, Schema, fields

database_name = "trivia"
database_path = "postgres://{}:{}@{}/{}".format('postgres', 'root', 'localhost:5432', database_name)

db = SQLAlchemy()
ma = Marshmallow(app)
'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''

PAGE_SIZE = 10

def paginate(request, data):
    page = request.args.get('page', 1, type=int)
    start_item = (page - 1) * PAGE_SIZE
    end_item = start_item + PAGE_SIZE
    result = data
    current_result = result[start_item:end_item]
    if not current_result:
        abort(404)
    else:
        return current_result


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Question

'''


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(String)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_by_id(self,id):
        db.session.query(self).filter(self.category == id).all()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }


'''
Category

'''


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def get(self):
        return db.session.query(self).all()

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }


class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category

    id = ma.auto_field()
    type = ma.auto_field()


class QuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Question

    id = ma.auto_field()
    question = ma.auto_field()
    answer = ma.auto_field()
    category = ma.auto_field()
    difficulty = ma.auto_field()


Category_schema = CategorySchema()
Categories_schema = CategorySchema(many=True)
Question_schema = QuestionSchema()
Questions_schema = QuestionSchema(many=True)
