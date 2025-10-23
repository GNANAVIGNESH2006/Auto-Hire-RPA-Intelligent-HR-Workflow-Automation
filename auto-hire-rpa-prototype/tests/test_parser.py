from parser import parse_resume_text

def test_parse_basic():
    txt = "Jane Smith\nEmail: jane.smith@sample.com\nExperience: 5 years\nSkills: Python, Java, AWS"
    parsed = parse_resume_text(txt)
    assert parsed["email"] == "jane.smith@sample.com"
    assert "python" in [s.lower() for s in parsed["skills"]]
    assert parsed["experience_years"] == 5.0
