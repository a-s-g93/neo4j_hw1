from flask import Flask, render_template, current_app, request
from datetime import timedelta
from flask_bootstrap import Bootstrap
from forms import inputForm
from comm import commDAO
from flask_jwt_extended import JWTManager
from drivers import init_driver

app = Flask(__name__)
Bootstrap(app)

# JWT
jwt = JWTManager(app)

FLASK_APP = 'api'
FLASK_DEBUG = 'true'
FLASK_RUN_PORT = 3000

NEO4J_URI = 'bolt://3.86.97.186:7687'
NEO4J_USERNAME = 'neo4j'
NEO4J_PASSWORD = 'sip-rocks-make'

JWT_SECRET = 'secret'
SALT_ROUNDS = 10

app.config.from_mapping(NEO4J_URI=NEO4J_URI,
                        NEO4J_USERNAME=NEO4J_USERNAME,
                        NEO4J_PASSWORD=NEO4J_PASSWORD,
                        JWT_SECRET_KEY=JWT_SECRET,
                        JWT_AUTH_HEADER_PREFIX="Bearer",
                        JWT_VERIFY_CLAIMS="signature",
                        JWT_EXPIRATION_DELTA=timedelta(360),
                        SECRET_KEY="secret")

with app.app_context():
    init_driver(
        app.config['NEO4J_URI'],
        app.config['NEO4J_USERNAME'],
        app.config['NEO4J_PASSWORD'],
    )


@app.route("/", methods=['GET', 'POST'])
def index():
    """ this is the main page
    """
    dao = commDAO(current_app.driver, current_app.config.get('SECRET_KEY'))
    header = "Add New Employee"
    message = ""

    form = inputForm()

    employees = dao.view_employees()
    print(employees)

    if request.method == 'POST':
        # push data to client
        try:
            # format name correctly
            name_temp = form.employee_name.data.split()
            name = " ".join([
                n.capitalize().strip() for n in name_temp
                if type(name_temp) is not str
            ])

            print("name: ", name)
            new_employee = dao.register(name=name, id=form.employee_id.data)
            print("new employee: ", new_employee)
            message = "{name} successfully added to database".format(name=name)
            employees = dao.view_employees()
        except Exception as e:
            print("error: ", e)
            message = "Unable to add employee to database"

    return render_template('index.html',
                           form=form,
                           header=header,
                           message=message,
                           employees=employees)


if __name__ == "__main__":
    app.run(threaded=True, host="127.0.0.1", port=8080, debug=True)
