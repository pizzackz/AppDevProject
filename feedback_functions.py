import shelve
from random import randint
from Feedback import Feedback


def create_new_feedback(cust_id, display_name, category, rating, message):
    # Open database
    feedback_dict = {}
    db = shelve.open("feedback.db", "c")
    if "Feedback" in db:
        feedback_dict = db["Feedback"]
    else:
        db["Feedback"] = feedback_dict

       # feedback[cust_id] = {feedback_id:feedback_object}
    cust_feedback = feedback_dict.get(cust_id, {})

    # Generate postfix from length of dict, Create new object, Save to db
    id_postfix = len(feedback_dict) + randint(0, 999)
    feedback = Feedback(cust_id, display_name, id_postfix, category, rating, message)
    print(cust_feedback)
    print(feedback.get_feedback_id())
    cust_feedback[str(feedback.get_feedback_id())] = feedback

    feedback_dict[cust_id] = cust_feedback

    db["Feedback"] = feedback_dict
    db.close()

    return feedback.get_feedback_id()


def retrieve_all_feedback():
    db = shelve.open("feedback.db", "c")
    feedback_dict = db["Feedback"]
    db.close()
    return feedback_dict


def retrieve_cust_feedback_dict(cust_id):
    # Open database
    feedback_dict = {}
    db = shelve.open("feedback.db", "c")
    if "Feedback" in db:
        feedback_dict = db["Feedback"]
    else:
        db["Feedback"] = feedback_dict

    if cust_id not in feedback_dict:
        return None

    return feedback_dict.get(cust_id)


def retrieve_cust_feedback(cust_id, feedback_id):
    feedback_dict = retrieve_cust_feedback_dict(cust_id)

    if not feedback_dict:
        return None
    
    return feedback_dict.get(feedback_id)


def delete_cust_feedback(cust_id, feedback_id):
    # Open database
    feedback_dict = {}
    db = shelve.open("feedback.db", "c")
    if "Feedback" in db:
        feedback_dict = db["Feedback"]
    else:
        db["Feedback"] = feedback_dict
    
    cust_feedback_dict = feedback_dict.get(cust_id)
    print(feedback_id, ' ', cust_id, ' f')
    cust_feedback_dict.pop(feedback_id)

    db["Feedback"] = feedback_dict
    db.close()


# Testing


