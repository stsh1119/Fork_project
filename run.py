from fork import create_app
from fork.celery_creator import celery

if __name__ == "__main__":
    app = create_app(celery=celery)
    app.run(debug=True)
