from models import Base, User
from flask import Flask, request, jsonify, make_response, url_for, abort, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, sessionmaker
#from marshmallow_sqlalchemy import ModelSchema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import create_engine

engine = create_engine('sqlite:///users.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

auth = HTTPBasicAuth()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://Peter:piento078@localhost:3306/mentorshipsDB'
SQLALCHEMY_TRACK_MODIFICATIONS = False

db = SQLAlchemy(app)

class Mentorships(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(50))
    link = db.Column(db.String(50))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def __init__(self, name, description, link):
        self.name = name
        self.description = description
        self.link = link
    
    def __repr__(self):
        return '<program %d>' % self.id

class Scholarships(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(50))
    link = db.Column(db.String(50))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def __init__(self, name, description, link):
        self.name = name
        self.description = description
        self.link = link
    
    def __repr__(self):
        return '<program %d>' % self.id

db.create_all()

class MentorshipsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Mentorships
        sqla_session = db.session
        include_relationships = True
        load_instance = True

    # id = fields.Number(dump_only=True)
    # name = fields.String(required=True)
    # description = fields.String(required=True)
    # link = fields.String(required=True)
    

class ScholarshipsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Scholarships
        sqla_session = db.session
        include_fk = True
        load_instance = True

    # id = fields.Number(dump_only=True)
    # name = fields.String(required=True)
    # description = fields.String(required=True)
    # link = fields.String(required=True)

@auth.verify_password
def verify_password(username, password):
    user = session.query(User).filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

@app.route('/admin', methods = ['POST'])
@auth.login_required
def new_user():
    username = request.json.get('admin')
    password = request.json.get('password')
    if username is None or password is None:
        print("missing arguments")
        abort(400) 
        
    if session.query(User).filter_by(username = username).first() is not None:
        print("existing user")
        user = session.query(User).filter_by(username=username).first()
        return jsonify({'message':'user already exists'}), 200#, {'Location': url_for('get_user', id = user.id, _external = True)}

    user = User(username = username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({ 'admin': user.username }), 201#, {'Location': url_for('get_user', id = user.id, _external = True)}

@app.route('/')
def index():
    return "Welcome to undergrads mentorships and scholarships API :) use\
                '/mentorships': for all mentorship programs available, \
                '/scholarships': for all scholarship programs available"

@app.route('/mentorships', methods = ['GET'])
def indexMentorships():
    get_mentorships = Mentorships.query.all()
    mentorships_schema = MentorshipsSchema(many=True)
    mentorships = mentorships_schema.dump(get_mentorships)
    return make_response(jsonify({"mentorship programs available": mentorships}))

@app.route('/scholarships', methods = ['GET'])
def indexScholarships():
    get_scholarships = Scholarships.query.all()
    scholarships_schema = ScholarshipsSchema(many=True)
    scholarships = scholarships_schema.dump(get_scholarships)
    return make_response(jsonify({"scholarship programs available": scholarships}))


@app.route('/createMentorships', methods = ['POST'])
@auth.login_required
def create_mentorships():
    data = request.get_json()
    mentorships_schema = MentorshipsSchema()
    mentorships = mentorships_schema.load(data)
    result = mentorships_schema.dump(data)
    mentorships.create()
    return make_response(jsonify({"program": result}),201)

@app.route('/createScholarships', methods = ['POST'])
@auth.login_required
def create_scholarships():
    data = request.get_json()
    scholarships_schema = ScholarshipsSchema()
    scholarships = scholarships_schema.load(data)
    result = scholarships_schema.dump(data)
    scholarships.create()
    return make_response(jsonify({"program": result}),201)

@app.route('/deleteMentorships/<id>', methods = ['DELETE'])
@auth.login_required
def delete_mentorship_by_id(id):
    get_mentorships = Mentorships.query.filter_by(id=id).one()
    db.session.delete(get_mentorships)
    db.session.commit()
    return make_response("",204)

@app.route('/deleteScholarships/<id>', methods = ['DELETE'])
@auth.login_required
def delete_scholarship_by_id(id):
    get_scholarships = Scholarships.query.filter_by(id=id).one()
    db.session.delete(get_scholarships)
    db.session.commit()
    return make_response("",204)

if __name__ == '__main__':
    app.run(debug=True)
