from typing import Dict, Any, Optional, List
from collections import Counter

from models.database import get_db


def calculate_statistics(recent: Optional[int] = None) -> Dict[str, Any]:
    """Calculate comprehensive lotto statistics."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Get results (all or recent N)
        if recent:
            cursor.execute('''
                SELECT num1, num2, num3, num4, num5, num6, bonus
                FROM lotto_results
                ORDER BY draw_no DESC
                LIMIT ?
            ''', (recent,))
        else:
            cursor.execute('''
                SELECT num1, num2, num3, num4, num5, num6, bonus
                FROM lotto_results
                ORDER BY draw_no DESC
            ''')

        rows = cursor.fetchall()
        total_draws = len(rows)

        if total_draws == 0:
            return _empty_statistics()

        # Calculate all statistics
        number_frequency = _calculate_number_frequency(rows)
        odd_even_distribution = _calculate_odd_even(rows)
        sum_distribution = _calculate_sum_distribution(rows)
        consecutive_stats = _calculate_consecutive(rows)
        section_distribution = _calculate_section_distribution(rows)

        return {
            "number_frequency": number_frequency,
            "odd_even_distribution": odd_even_distribution,
            "sum_distribution": sum_distribution,
            "consecutive_stats": consecutive_stats,
            "section_distribution": section_distribution,
            "total_draws": total_draws
        }


def _empty_statistics() -> Dict[str, Any]:
    """Return empty statistics structure."""
    return {
        "number_frequency": {str(i): 0 for i in range(1, 46)},
        "odd_even_distribution": {f"{i}_odd": 0 for i in range(7)},
        "sum_distribution": {
            "ranges": ["61-80", "81-100", "101-120", "121-140", "141-160", "161-180", "181-200"],
            "counts": [0, 0, 0, 0, 0, 0, 0]
        },
        "consecutive_stats": {"has_consecutive": 0, "no_consecutive": 0},
        "section_distribution": {
            "low_1_15": {"avg": 0, "distribution": {}},
            "mid_16_30": {"avg": 0, "distribution": {}},
            "high_31_45": {"avg": 0, "distribution": {}}
        },
        "total_draws": 0
    }


def _calculate_number_frequency(rows: List) -> Dict[str, int]:
    """Calculate frequency of each number (1-45)."""
    counter: Counter = Counter()

    for row in rows:
        for i in range(6):  # num1 to num6 (excluding bonus)
            counter[row[i]] += 1

    return {str(i): counter.get(i, 0) for i in range(1, 46)}


def _calculate_odd_even(rows: List) -> Dict[str, int]:
    """Calculate odd/even distribution per draw."""
    distribution: Counter = Counter()

    for row in rows:
        numbers = [row[i] for i in range(6)]
        odd_count = sum(1 for n in numbers if n % 2 == 1)
        distribution[f"{odd_count}_odd"] += 1

    return {f"{i}_odd": distribution.get(f"{i}_odd", 0) for i in range(7)}


def _calculate_sum_distribution(rows: List) -> Dict[str, Any]:
    """Calculate sum distribution of 6 numbers."""
    ranges = ["61-80", "81-100", "101-120", "121-140", "141-160", "161-180", "181-200", "201+"]
    counts = [0] * len(ranges)

    for row in rows:
        total = sum(row[i] for i in range(6))

        if total <= 80:
            counts[0] += 1
        elif total <= 100:
            counts[1] += 1
        elif total <= 120:
            counts[2] += 1
        elif total <= 140:
            counts[3] += 1
        elif total <= 160:
            counts[4] += 1
        elif total <= 180:
            counts[5] += 1
        elif total <= 200:
            counts[6] += 1
        else:
            counts[7] += 1

    return {"ranges": ranges, "counts": counts}


def _calculate_consecutive(rows: List) -> Dict[str, int]:
    """Calculate consecutive number statistics."""
    has_consecutive = 0
    no_consecutive = 0

    for row in rows:
        numbers = sorted([row[i] for i in range(6)])
        has_consec = False

        for i in range(len(numbers) - 1):
            if numbers[i + 1] - numbers[i] == 1:
                has_consec = True
                break

        if has_consec:
            has_consecutive += 1
        else:
            no_consecutive += 1

    return {"has_consecutive": has_consecutive, "no_consecutive": no_consecutive}


def _calculate_section_distribution(rows: List) -> Dict[str, Any]:
    """Calculate section distribution (low: 1-15, mid: 16-30, high: 31-45)."""
    low_counts: List[int] = []
    mid_counts: List[int] = []
    high_counts: List[int] = []

    for row in rows:
        numbers = [row[i] for i in range(6)]
        low = sum(1 for n in numbers if 1 <= n <= 15)
        mid = sum(1 for n in numbers if 16 <= n <= 30)
        high = sum(1 for n in numbers if 31 <= n <= 45)

        low_counts.append(low)
        mid_counts.append(mid)
        high_counts.append(high)

    def calc_section_stats(counts: List[int]) -> Dict[str, Any]:
        if not counts:
            return {"avg": 0, "distribution": {}}
        counter = Counter(counts)
        return {
            "avg": round(sum(counts) / len(counts), 2),
            "distribution": {str(k): v for k, v in sorted(counter.items())}
        }

    return {
        "low_1_15": calc_section_stats(low_counts),
        "mid_16_30": calc_section_stats(mid_counts),
        "high_31_45": calc_section_stats(high_counts)
    }
