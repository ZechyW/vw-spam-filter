"""
UI Prototype for Spam classification with Vowpal Wabbit using the raw Enron-Spam
dataset
"""
import json
import os
import pickle
import random
import time
from pathlib import Path

import cherrypy
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from vowpalwabbit import pyvw

from ui_prototype.conf import vw_opts
from util.text import process_text, to_vw_format

# Configuration
# =============
# The path to hold the Vowpal Wabbit regression model -- Will be created if it does not
# already exist.
# Note that the original VW options saved in the model file may override any new
# options specified at run-time when it is loaded.
model_file = Path("./ui_prototype/data/model.vw")

# The server maintains a pickled shuffling and partitioning of all the email
# documents into a train and a test set.
# Setting this to true re-shuffles the sets and resets all user input.
reshuffle_data = False

# Backend server port
backend_port = 4000

# Data management
# ===============
# FIXME: Pickling is hardly efficient, but is used as a stand-in for access to some
#  better backing DB
print("Loading datasets...")
start_time = time.perf_counter()
data_path = Path("./ui_prototype/data")
if reshuffle_data:
    print("Dataset shuffle requested, this could take a while...")

    # Stand-in for pulling data from a database or some external source
    # Each item of the list being a Dict with keys "subject" and "content"
    with open(data_path / "all_ham.pkl", "rb") as f:
        all_ham = pickle.load(f)
    with open(data_path / "all_spam.pkl", "rb") as f:
        all_spam = pickle.load(f)

    # Optionally reshuffle and partition the train/test sets
    ham_labels = [1 for _ in range(len(all_ham))]
    spam_labels = [-1 for _ in range(len(all_spam))]
    train_docs, test_docs, train_labels, test_labels = train_test_split(
        all_ham + all_spam, ham_labels + spam_labels
    )

    # Pre-process the test set into VW format before saving
    def to_vw(doc):
        feature_spaces = {
            "subject": process_text(doc["subject"]).strip(),
            "content": process_text(doc["content"]).strip(),
        }
        return to_vw_format(feature_spaces)

    test_docs = [to_vw(doc).strip() for doc in test_docs]

    with open(data_path / "train_docs.pkl", "wb") as f:
        pickle.dump(train_docs, f)
    with open(data_path / "test_docs.pkl", "wb") as f:
        pickle.dump(test_docs, f)
    with open(data_path / "train_labels.pkl", "wb") as f:
        pickle.dump(train_labels, f)
    with open(data_path / "test_labels.pkl", "wb") as f:
        pickle.dump(test_labels, f)
else:
    with open(data_path / "train_docs.pkl", "rb") as f:
        train_docs = pickle.load(f)
    with open(data_path / "test_docs.pkl", "rb") as f:
        test_docs = pickle.load(f)
    with open(data_path / "train_labels.pkl", "rb") as f:
        train_labels = pickle.load(f)
    with open(data_path / "test_labels.pkl", "rb") as f:
        test_labels = pickle.load(f)

print(f"Loaded in {time.perf_counter() - start_time:.3f}s")

# This is a dict of email IDs -> user provided labels, with built-in support counts
user_label_file = data_path / "user_labels.pkl"
if not user_label_file.exists() or reshuffle_data:
    print("Resetting user-provided training labels...")
    user_labels = {"count_1": 0, "count_-1": 0}
    with open(user_label_file, "wb") as f:
        pickle.dump(user_labels, f)
else:
    with open(user_label_file, "rb") as f:
        user_labels = pickle.load(f)

# Model management
# ================
if model_file.exists():
    vw_opts["initial_regressor"] = model_file

model = pyvw.vw(**vw_opts)


# API Server and access helpers
# =============================
def get_random_emails(k):
    """
    Get k random email IDs from the training set
    :param k:
    :return: List of email IDs
    """
    return random.sample(range(len(train_docs)), k)


def get_raw_email(email_id):
    """
    Return object representing the email with given ID
    :param email_id:
    :return: Copy of the email document as a Dict
    """
    email_id = int(email_id)

    if email_id >= len(train_docs):
        raise cherrypy.HTTPError(404, f"No email with the given ID: {email_id}")

    email_copy = train_docs[email_id].copy()
    email_copy["id"] = email_id
    return email_copy


def get_vw_email(email_id, label=None):
    """
    Get email contents in VW format
    :param email_id:
    :return:
    """
    doc = get_raw_email(email_id)
    feature_spaces = {
        "subject": process_text(doc["subject"]).strip(),
        "content": process_text(doc["content"]).strip(),
    }
    return to_vw_format(feature_spaces, label)


def get_email(email_id):
    """
    Get email document with additional information (label/prediction)
    :param email_id:
    :return:
    """
    email = get_raw_email(email_id)
    email["label"] = get_label(email_id)
    email["prediction"] = get_prediction(email_id)

    return email


def get_prediction(email_id):
    """
    Run the given email through VW to get a prediction based on the current model
    :param email_id:
    :return: VW's prediction as a float -- Probability of the message being ham
    """
    return model.predict(get_vw_email(email_id))


def get_label(email_id):
    if email_id in user_labels:
        return user_labels[email_id]
    else:
        return None


def set_label(email_id, label):
    """
    Ensures that the params are valid, then saves the user-provided label
    :param email_id:
    :param label:
    :return:
    """
    # Sanity check: Does email exist?
    _ = get_raw_email(email_id)

    if label != "ham" and label != "spam":
        raise cherrypy.HTTPError(400, f'Label must be "ham" or "spam"')

    if label == "ham":
        label = "1"
    if label == "spam":
        label = "-1"

    # Train model and save
    # Keep re-learning the example until it predicts correctly :think
    label_learnt = False
    while not label_learnt:
        model.learn(get_vw_email(email_id, label))
        new_predicted_label = (
            "1" if model.predict(get_vw_email(email_id)) >= 0.5 else "-1"
        )
        if new_predicted_label == label:
            label_learnt = True

    model.save(str(model_file))

    # FIXME: This is a stand-in for a more efficient data storage mechanism
    # Adjust counts
    try:
        current_label = user_labels[email_id]
        if label != current_label:
            user_labels[f"count_{current_label}"] -= 1
            user_labels[f"count_{label}"] += 1
    except KeyError:
        # No current label
        user_labels[f"count_{label}"] += 1

    # Label and save
    user_labels[email_id] = label
    with open(user_label_file, "wb") as f:
        pickle.dump(user_labels, f)


def get_test_report():
    """
    Classification report for the current state of the model on the held-out test set
    :return:
    """
    pred_labels = [1 if model.predict(doc) >= 0.5 else -1 for doc in test_docs]
    return classification_report(test_labels, pred_labels)


@cherrypy.expose
class Root(object):
    def __init__(self):
        self.email = Email()
        self.report = Report()


@cherrypy.popargs("email_id")
@cherrypy.expose
class Email(object):
    def __init__(self):
        self.label = Label()
        self.prediction = Prediction()

    def GET(self, email_id=None):
        if email_id is not None:
            return json.dumps(get_email(email_id), indent=2)
        else:
            # Return 10 random emails
            emails = get_random_emails(10)
            emails = map(lambda random_id: get_email(random_id), emails)
            return json.dumps(list(emails), indent=2)


@cherrypy.expose
class Label(object):
    def GET(self, email_id):
        response = {"id": email_id, "label": ""}
        if email_id in user_labels:
            response["label"] = user_labels[email_id]

        return json.dumps(response, indent=2)

    @cherrypy.tools.json_in()
    def PUT(self, email_id):
        label = cherrypy.request.json["label"]
        set_label(email_id, label)
        return self.GET(email_id)

    def OPTIONS(self, email_id):
        cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET, PUT"
        cherrypy.response.headers["Access-Control-Allow-Headers"] = "content-type"
        return ""


@cherrypy.expose
class Prediction(object):
    def GET(self, email_id):
        response = {"id": email_id, "prediction": get_prediction(email_id)}
        return json.dumps(response, indent=2)


@cherrypy.expose
class Report(object):
    def GET(self):
        response = {
            "count_ham": user_labels["count_1"],
            "count_spam": user_labels["count_-1"],
            "report": get_test_report(),
        }
        return json.dumps(response, indent=2)


def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"


if __name__ == "__main__":
    conf = {
        "global": {"server.socket_port": backend_port, "server.socket_host": "0.0.0.0"},
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "request.show_tracebacks": False,
            "tools.sessions.on": True,
            "tools.response_headers.on": True,
            "tools.response_headers.headers": [("Content-Type", "text/plain")],
            "tools.CORS.on": True,
            "tools.staticdir.root": os.path.abspath(os.getcwd()),
            "tools.staticdir.on": True,
            "tools.staticdir.dir": "./frontend-ui-prototype/build",
            "tools.staticdir.index": "index.html",
        },
    }
    cherrypy.tools.CORS = cherrypy.Tool("before_handler", CORS)
    cherrypy.quickstart(Root(), "/", conf)
