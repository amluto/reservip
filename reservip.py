#!/usr/bin/python3

from bottle import route, run, template, request, response
import bottle
import os
import sqlalchemy.ext.declarative
import tempfile
import json

SQLBase = sqlalchemy.ext.declarative.declarative_base()

class Users(SQLBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    token = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True)

def get_user(token):
    session = Session(autocommit=True)
    with session.begin():
        users = session.query(Users).filter_by(token=token).all()
        
        if len(users) == 0:
            raise bottle.HTTPResponse(body='bad token', status=403,
                                      headers={"Access-Control-Allow-Origin":"*"})

        session.expunge(users[0])

    return users[0]

# TODO: Implement CORS

@route('/form/<token>')
def form(token):
    user = get_user(token)

    try:
        f = open('user_%d.json' % user.id, 'rb')
    except OSError as e:
        return '{}'

    return bottle.HTTPResponse(f, headers={'Content-Type':'application/json',
                                           'Access-Control-Allow-Origin':'*'})

@route('/form/<token>', method='PUT')
def form(token):
    user = get_user(token)

    if not request.json:
        raise bottle.HTTPError(400, 'Bad content-type')

    payload = json.dumps(request.json, sort_keys=True)
    f = tempfile.NamedTemporaryFile(dir='.', buffering=0, delete=False)
    try:
        f.write(payload.encode('utf-8'))
        f.flush()
        os.fsync(f.fileno())
        os.rename(f.name, 'user_%d.json' % user.id)
    except:
        os.unlink(f.name)
        raise

    return 'OK'

if __name__ == '__main__':
    if not os.path.exists('users.db'):
        engine = sqlalchemy.create_engine('sqlite:///users.db')
        SQLBase.metadata.create_all(engine)
    else:
        engine = sqlalchemy.create_engine('sqlite:///users.db')

    # Yuck
    Session = sqlalchemy.orm.sessionmaker(bind=engine)

    run(host='localhost', port=8080)
