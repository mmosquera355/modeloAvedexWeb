from flask_script import Manager,Server
from aplicacion.app import app

manager = Manager(app)
app.config['DEBUG'] = False  # Ensure debugger will load.
server = Server(host='192.168.1.53', port=5000)
manager.add_command("runserver", server)

if __name__ == '__main__':
    manager.run()
