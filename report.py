from collections import defaultdict
from utils import attendance_percentage, status_from_percentage, classes_needed_to_reach_target


def build_summary_report(records, students, subjects) -> str:
    if not records:
        return "No records available."

    eligible = 0
    warning = 0
    critical = 0

    for rec in records:
        p = attendance_percentage(rec["attended"], rec["total"])
        status = status_from_percentage(p)

        if status == "Eligible":
            eligible += 1
        elif status == "Warning":
            warning += 1
        else:
            critical += 1

    return (
        "SMART ATTENDANCE SUMMARY\n"
        + "=" * 40 + "\n"
        + f"Students Set Size        : {len(students)}\n"
        + f"Subjects Set Size        : {len(subjects)}\n"
        + f"Attendance Relation Size : {len(records)}\n\n"
        + f"Eligible Records         : {eligible}\n"
        + f"Warning Records          : {warning}\n"
        + f"Critical Records         : {critical}\n"
    )


def build_low_attendance_report(records) -> str:
    if not records:
        return "No records available."

    lines = ["LOW ATTENDANCE REPORT", "=" * 40]
    found = False

    for rec in records:
        p = attendance_percentage(rec["attended"], rec["total"])
        if p < 75:
            found = True
            needed = classes_needed_to_reach_target(
                rec["attended"], rec["total"], rec.get("target", 75)
            )
            lines.append(
                f'{rec["student"]} | {rec["subject"]} | {p:.2f}% | Need next {needed} classes'
            )

    if not found:
        lines.append("All students are at or above target attendance.")

    return "\n".join(lines)


def build_top_performers_report(records) -> str:
    if not records:
        return "No records available."

    ranked = []
    for rec in records:
        p = attendance_percentage(rec["attended"], rec["total"])
        ranked.append((p, rec["student"], rec["subject"]))

    ranked.sort(reverse=True)

    lines = ["TOP PERFORMERS", "=" * 40]
    for i, (p, student, subject) in enumerate(ranked[:5], start=1):
        lines.append(f"{i}. {student} | {subject} | {p:.2f}%")

    return "\n".join(lines)


def build_subject_analysis_report(records) -> str:
    if not records:
        return "No records available."

    subject_map = defaultdict(list)

    for rec in records:
        p = attendance_percentage(rec["attended"], rec["total"])
        subject_map[rec["subject"]].append(p)

    lines = ["SUBJECT ANALYSIS", "=" * 40]
    for subject in sorted(subject_map.keys()):
        avg = sum(subject_map[subject]) / len(subject_map[subject])
        lines.append(f"{subject}: Average Attendance = {avg:.2f}%")

    return "\n".join(lines)


def build_relations_report(records) -> str:
    if not records:
        return "No records available."

    lines = ["ATTENDANCE RELATION VIEW", "=" * 40]
    lines.append("R = {(student, subject)} where attendance is recorded\n")

    for rec in records:
        p = attendance_percentage(rec["attended"], rec["total"])
        status = status_from_percentage(p)
        lines.append(f'({rec["student"]}, {rec["subject"]}) -> {p:.2f}% -> {status}')

    return "\n".join(lines)


def build_graph_report(pair_counts) -> str:
    lines = ["CO-ATTENDANCE GRAPH VIEW", "=" * 40]
    lines.append("Edge between two students means both are eligible in same subject(s).\n")

    if not pair_counts:
        lines.append("No graph connections found yet.")
        return "\n".join(lines)

    for (s1, s2), weight in sorted(pair_counts.items()):
        lines.append(f"{s1} -- {s2} | common eligible subjects = {weight}")

    return "\n".join(lines)

def build_specific_attendance_report(records, student_name, subject_name=None) -> str:
    if not records:
        return "No records available."

    original_student_name = student_name.strip()
    original_subject_name = subject_name.strip() if subject_name else None

    student_name = original_student_name.lower()
    subject_name = original_subject_name.lower() if original_subject_name else None

    matched = []

    for rec in records:
        if rec["student"].strip().lower() == student_name:
            if subject_name is None or rec["subject"].strip().lower() == subject_name:
                matched.append(rec)

    if not matched:
        if original_subject_name:
            return f"No record found for student '{original_student_name}' in subject '{original_subject_name}'."
        return f"No record found for student '{original_student_name}'."

    lines = ["SPECIFIC ATTENDANCE REPORT", "=" * 40]

    total_attended = 0
    total_classes = 0

    for rec in matched:
        p = attendance_percentage(rec["attended"], rec["total"])
        status = status_from_percentage(p)
        needed = classes_needed_to_reach_target(
            rec["attended"], rec["total"], rec.get("target", 75)
        )

        lines.append(
            f"Student : {rec['student']}\n"
            f"Subject : {rec['subject']}\n"
            f"Attended: {rec['attended']}\n"
            f"Total   : {rec['total']}\n"
            f"Percent : {p:.2f}%\n"
            f"Status  : {status}\n"
            f"Need    : {needed} more classes to reach target\n"
            + "-" * 40
        )

        total_attended += rec["attended"]
        total_classes += rec["total"]

    if subject_name is None:
        overall_percentage = attendance_percentage(total_attended, total_classes)
        overall_status = status_from_percentage(overall_percentage)

        lines.append("OVERALL STUDENT ATTENDANCE")
        lines.append("=" * 40)
        lines.append(f"Total Attended : {total_attended}")
        lines.append(f"Total Classes  : {total_classes}")
        lines.append(f"Overall %      : {overall_percentage:.2f}%")
        lines.append(f"Overall Status : {overall_status}")

    return "\n".join(lines)