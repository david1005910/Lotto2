import random
from typing import Dict, Any, List
from collections import Counter

from models.database import get_db


def get_recommendations() -> Dict[str, Any]:
    """Generate all recommendation strategies."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT num1, num2, num3, num4, num5, num6
            FROM lotto_results
            ORDER BY draw_no DESC
        ''')
        rows = cursor.fetchall()

    if not rows:
        return {"recommendations": {}}

    return {
        "recommendations": {
            "high_frequency": _high_frequency_recommendation(rows),
            "low_frequency": _low_frequency_recommendation(rows),
            "balanced_odd_even": _balanced_odd_even_recommendation(),
            "section_spread": _section_spread_recommendation(),
            "optimal_sum": _optimal_sum_recommendation()
        }
    }


def _high_frequency_recommendation(rows: List) -> Dict[str, Any]:
    """Recommend numbers with highest historical frequency."""
    counter: Counter = Counter()

    for row in rows:
        for i in range(6):
            counter[row[i]] += 1

    # Get top 15 most frequent numbers and pick 6
    top_numbers = [num for num, _ in counter.most_common(15)]
    selected = random.sample(top_numbers, 6)

    return {
        "numbers": sorted(selected),
        "description": "역대 출현 빈도가 높은 번호 조합"
    }


def _low_frequency_recommendation(rows: List) -> Dict[str, Any]:
    """Recommend numbers that haven't appeared recently."""
    recent_50 = rows[:50] if len(rows) >= 50 else rows

    recent_numbers: set = set()
    for row in recent_50:
        for i in range(6):
            recent_numbers.add(row[i])

    # Find numbers not in recent draws
    cold_numbers = [n for n in range(1, 46) if n not in recent_numbers]

    # If not enough cold numbers, add least frequent
    if len(cold_numbers) < 6:
        counter: Counter = Counter()
        for row in recent_50:
            for i in range(6):
                counter[row[i]] += 1

        least_frequent = [num for num, _ in counter.most_common()[-15:]]
        cold_numbers.extend(least_frequent)
        cold_numbers = list(set(cold_numbers))

    selected = random.sample(cold_numbers[:15], min(6, len(cold_numbers)))

    # Fill remaining with random if needed
    while len(selected) < 6:
        num = random.randint(1, 45)
        if num not in selected:
            selected.append(num)

    return {
        "numbers": sorted(selected),
        "description": "최근 오래 출현하지 않은 번호 조합"
    }


def _balanced_odd_even_recommendation() -> Dict[str, Any]:
    """Recommend balanced odd/even combination (3 odd, 3 even)."""
    odd_numbers = [n for n in range(1, 46) if n % 2 == 1]  # 23 odd numbers
    even_numbers = [n for n in range(1, 46) if n % 2 == 0]  # 22 even numbers

    selected_odd = random.sample(odd_numbers, 3)
    selected_even = random.sample(even_numbers, 3)

    return {
        "numbers": sorted(selected_odd + selected_even),
        "description": "홀수 3개, 짝수 3개 균형 조합"
    }


def _section_spread_recommendation() -> Dict[str, Any]:
    """Recommend evenly spread across sections (2 from each: low/mid/high)."""
    low_section = list(range(1, 16))   # 1-15
    mid_section = list(range(16, 31))  # 16-30
    high_section = list(range(31, 46)) # 31-45

    selected = []
    selected.extend(random.sample(low_section, 2))
    selected.extend(random.sample(mid_section, 2))
    selected.extend(random.sample(high_section, 2))

    return {
        "numbers": sorted(selected),
        "description": "저/중/고 구간 균등 분포 조합"
    }


def _optimal_sum_recommendation() -> Dict[str, Any]:
    """Recommend numbers with optimal sum range (130-150)."""
    target_min = 130
    target_max = 150
    max_attempts = 1000

    for _ in range(max_attempts):
        numbers = random.sample(range(1, 46), 6)
        total = sum(numbers)
        if target_min <= total <= target_max:
            return {
                "numbers": sorted(numbers),
                "description": "합계 130-150 범위 최적 조합"
            }

    # Fallback: return best attempt
    best_numbers = random.sample(range(1, 46), 6)
    return {
        "numbers": sorted(best_numbers),
        "description": "합계 130-150 범위 최적 조합"
    }
