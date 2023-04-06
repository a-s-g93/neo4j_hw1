import jwt
from datetime import datetime

from flask import current_app

from neo4j.exceptions import ConstraintError


class commDAO:
    """
    The constructor expects an instance of the Neo4j Driver, which will be
    used to interact with Neo4j.
    """

    def __init__(self, driver, jwt_secret):
        self.driver = driver
        self.jwt_secret = jwt_secret

    """
    This method should create a new Employee node in the database with the name and ID
    provided.

    The properties also be used to generate a JWT `token` which should be included
    with the returned employee.
    """

    # tag::register[]

    def register(self, name, id):

        def create_employee(tx, name, id):
            return tx.run("""
                    MERGE (e:Employee {
                        emp_id: $ID,
                        name: $name
                    })
                    RETURN e
                """,
                          name=name,
                          ID=id).single()

        try:
            with self.driver.session() as session:
                result = session.execute_write(create_employee, name, id)

                user = result['e']

                payload = {
                    "emp_id": user["emp_id"],
                    "name": user["name"],
                }

                payload['token'] = self._generate_token(payload)

                return payload
        except ConstraintError as err:
            print(err)

    # end::register[]
    """
    This method should take the claims encoded into a JWT token and return
    the information needed to authenticate this user against the database.
    """

    # tag::generate[]

    def _generate_token(self, payload):
        iat = datetime.utcnow()

        payload["sub"] = payload["emp_id"]
        payload["iat"] = iat
        payload["nbf"] = iat
        payload["exp"] = iat + current_app.config.get('JWT_EXPIRATION_DELTA')

        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

    # end::generate[]
    """
    This method will attemp to decode a JWT token
    """

    # tag::decode[]
    def decode_token(auth_token, jwt_secret):
        try:
            payload = jwt.decode(auth_token, jwt_secret)
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    # end::decode[]
    """
    This method retrieves all Employee nodes from the database for display.
    """

    # tag::view[]
    def view_employees(self):

        def view(tx):
            result = tx.run("""
                    MATCH (e:Employee)
                    RETURN e
                """)

            return [row.value("e") for row in result]

        try:
            with self.driver.session() as session:

                return session.execute_read(view)

        except ConstraintError as err:
            print(err)

            session.close()

    # end::view[]