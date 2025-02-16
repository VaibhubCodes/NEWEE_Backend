import openai
import json
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY  # Ensure API key is set

def split_text(text, num_batches=3):
    """Splits the input text into equal parts for parallel processing."""
    chunk_size = len(text) // num_batches
    return [text[i * chunk_size: (i + 1) * chunk_size] for i in range(num_batches)]

def generate_questions_batch(text_batch, num_questions, difficulty, include_explanations):
    """Generate a specific number of questions from a batch of text using OpenAI GPT-4."""
    
    questions_per_batch = max(1, num_questions // 3)  # Ensure at least 1 question per batch
    
    prompt = f"""
    Generate exactly {questions_per_batch} multiple-choice questions from the following text:
    {text_batch}

    Each question should have:
    - 4 answer choices
    - One correct answer
    - Difficulty: {difficulty}
    - Include explanations: {include_explanations}

    Format the output **strictly** as a JSON list:
    [
        {{
            "text": "Question?",
            "option1": "A",
            "option2": "B",
            "option3": "C",
            "option4": "D",
            "correct_answer": "option1",
            "explanation": "Brief explanation"
        }}
    ]
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1800
        )

        response_text = response.choices[0].message.content.strip()
        print(f"🔍 OpenAI Raw Response:\n{response_text}")

        # Ensure response is not empty
        if not response_text:
            print("⚠️ OpenAI returned an empty response.")
            return []

        questions = json.loads(response_text)

        # Trim excess questions if OpenAI returns more
        return questions[:questions_per_batch]

    except openai.OpenAIError as e:
        print(f"❌ OpenAI API Error: {str(e)}")
        return []

def generate_questions_with_openai(text, num_questions=10, difficulty="Medium", include_explanations=False):
    """Parallelized OpenAI API calls to generate questions faster with correct count."""
    num_batches = 3  # Number of parallel OpenAI calls
    text_batches = split_text(text, num_batches)

    with ThreadPoolExecutor() as executor:
        results = executor.map(lambda batch: generate_questions_batch(batch, num_questions, difficulty, include_explanations), text_batches)

    # Merge all results
    all_questions = [q for batch in results for q in batch]

    # Ensure we return exactly `num_questions`
    return all_questions[:num_questions]
