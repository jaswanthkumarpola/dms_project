def attendance_percentage(attended: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return (attended / total) * 100


def status_from_percentage(percentage: float) -> str:
    if percentage >= 75:
        return "Eligible"
    elif percentage >= 60:
        return "Warning"
    return "Critical"


def classes_needed_to_reach_target(attended: int, total: int, target: int = 75) -> int:
    if total <= 0:
        return 0
    if attended > total or attended < 0:
        return 0
    if attendance_percentage(attended, total) >= target:
        return 0

    x = 0
    while ((attended + x) / (total + x)) * 100 < target:
        x += 1
    return x