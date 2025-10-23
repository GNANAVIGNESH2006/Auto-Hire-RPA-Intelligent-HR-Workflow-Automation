from ranker import score_candidate_for_job

def test_score():
    job = "Backend developer needed with python, flask, postgres"
    resume = "Python developer experienced with Flask and Postgres"
    score = score_candidate_for_job(resume, job)
    assert score > 20.0
