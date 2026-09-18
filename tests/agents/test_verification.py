from app.agents.verification import verify_answer
def test_empty_fails(): assert not verify_answer("",[]).passed
def test_answer_passes(): assert verify_answer("A useful answer",[]).passed
