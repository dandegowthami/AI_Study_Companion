import random
from app.services.mastery_service import get_project_mastery, update_mastery
from app.services.llm_service import call_llm, parse_json_safe


QUESTION_GEN_PROMPT = """Generate one quiz question about the concept "{concept}" for a student
at approximately {mastery}% mastery of this topic.

Rules:
- If mastery is below 50%, ask a foundational/definition-level question.
- If mastery is 50-75%, ask an applied "how/why" question.
- If mastery is above 75%, ask a harder, scenario-based question.
- Randomly choose the question type: multiple_choice or open_ended.

For multiple_choice questions, "options" MUST be formatted exactly as "A) ...", "B) ...", "C) ...", "D) ...",
and "correct_answer" MUST be ONLY the single letter (e.g. "B"), never the full option text.

Return ONLY valid JSON in this exact format:
{{
  "question_type": "multiple_choice",
  "question_text": "...",
  "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
  "correct_answer": "B",
  "difficulty": "easy"
}}
(For open_ended questions, omit "options" and set "correct_answer" to a short
model answer instead of a letter.)"""

GRADE_OPEN_ENDED_PROMPT = """A student was asked: "{question}"
The expected key points were: "{expected}"
The student answered: "{student_answer}"

Evaluate their understanding. Return ONLY valid JSON:
{{
  "correct": true or false,
  "feedback": "one or two sentences of specific, constructive feedback",
  "missing_concepts": ["concept if any were missed"]
}}"""


def select_next_concept(project_id: str) -> dict:
    """
    Adaptive selection: weighted toward weaker concepts, but not
    exclusively - occasionally reinforces stronger ones too, and
    never gets stuck repeating the single weakest concept forever.
    """
    mastery_records = get_project_mastery(project_id)
    if not mastery_records:
        return {"concept": "General Concepts", "mastery_pct": 30}

    # Weight = inverse of mastery, so weaker concepts are picked more often
    weights = [max(1, 100 - m["mastery_pct"]) for m in mastery_records]
    return random.choices(mastery_records, weights=weights, k=1)[0]


def generate_question(project_id: str) -> dict:
    concept_record = select_next_concept(project_id)
    prompt = QUESTION_GEN_PROMPT.format(
        concept=concept_record["concept"], mastery=concept_record["mastery_pct"]
    )
    raw = call_llm(prompt, feature="quiz_generation", json_mode=True)
    parsed = parse_json_safe(raw)

    if not parsed:
        # Fallback so a bad AI response never breaks the quiz flow
        parsed = {
            "question_type": "open_ended",
            "question_text": f"Explain what you understand about {concept_record['concept']}.",
            "correct_answer": "Any reasonable explanation of the concept.",
            "difficulty": "medium",
        }

    parsed["concept"] = concept_record["concept"]
    return parsed


def evaluate_answer(question: dict, student_answer: str) -> dict:
    if question["question_type"] == "multiple_choice":
        correct = question["correct_answer"].strip().lower()
        student = student_answer.strip().lower()

        # Handle cases where correct_answer is just a letter ("B") or the full option text
        is_correct = (
            student == correct
            or student.startswith(correct + ")")
            or student.startswith(correct + ".")
            or (len(correct) == 1 and student[:1] == correct)
        )

        return {
            "correct": is_correct,
            "feedback": "Correct!" if is_correct else f"Not quite - the correct answer was {question['correct_answer']}.",
            "missing_concepts": [],
        }

    prompt = GRADE_OPEN_ENDED_PROMPT.format(
        question=question["question_text"],
        expected=question["correct_answer"],
        student_answer=student_answer,
    )
    raw = call_llm(prompt, feature="quiz_grading", json_mode=True)
    parsed = parse_json_safe(raw)

    if not parsed:
        return {"correct": False, "feedback": "Could not evaluate this automatically.", "missing_concepts": []}

    return parsed