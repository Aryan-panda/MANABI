from typing import List, Optional
from app.academic_data.interface import (
    AcademicDataProvider,
    StudentProfile,
    CourseEnrollment,
    AttendanceRecord,
    ExamResult,
    ClassSchedule,
)


class MockAcademicDataProvider(AcademicDataProvider):
    """
    Mock implementation of institutional student information system (SIS).
    Provides consistent, deterministic academic data for testing and development.
    """

    def __init__(self):
        self._profiles = {
            "STU1001": StudentProfile(
                student_id="STU1001",
                full_name="Aryan Panda",
                email="aryan@university.edu",
                program="B.Tech in Computer Science & Engineering",
                department="Computer Science & Engineering",
                semester=6,
                cgpa=8.85,
                credits_earned=124,
                credits_required=160,
                academic_status="Good Standing",
            ),
            "STU1002": StudentProfile(
                student_id="STU1002",
                full_name="Alex Mercer",
                email="alex@university.edu",
                program="B.Tech in Information Technology",
                department="Information Technology",
                semester=4,
                cgpa=6.42,
                credits_earned=78,
                credits_required=160,
                academic_status="Academic Warning",
            ),
        }

        self._courses = {
            "STU1001": [
                CourseEnrollment(
                    course_code="CS301",
                    course_name="Distributed Systems",
                    credits=4,
                    instructor="Dr. Ramesh Rao",
                    semester=6,
                    status="Enrolled",
                    prerequisites=["CS201", "CS204"],
                ),
                CourseEnrollment(
                    course_code="CS304",
                    course_name="Database Internals & Storage Engines",
                    credits=4,
                    instructor="Prof. Sarah Jenkins",
                    semester=6,
                    status="Enrolled",
                    prerequisites=["CS202"],
                ),
                CourseEnrollment(
                    course_code="CS308",
                    course_name="Machine Learning Systems",
                    credits=3,
                    instructor="Dr. K. V. Sharma",
                    semester=6,
                    status="Enrolled",
                    prerequisites=["MA201", "CS201"],
                ),
                CourseEnrollment(
                    course_code="HS301",
                    course_name="Engineering Ethics & Professional Practice",
                    credits=2,
                    instructor="Prof. David Klein",
                    semester=6,
                    status="Enrolled",
                ),
            ],
            "STU1002": [
                CourseEnrollment(
                    course_code="IT201",
                    course_name="Data Structures & Algorithms",
                    credits=4,
                    instructor="Prof. N. Gupta",
                    semester=4,
                    status="Enrolled",
                ),
                CourseEnrollment(
                    course_code="IT203",
                    course_name="Operating Systems",
                    credits=4,
                    instructor="Dr. H. Miller",
                    semester=4,
                    status="Enrolled",
                ),
            ],
        }

        self._attendance = {
            "STU1001": [
                AttendanceRecord(
                    course_code="CS301",
                    course_name="Distributed Systems",
                    classes_held=32,
                    classes_attended=29,
                    percentage=90.6,
                    is_critical=False,
                ),
                AttendanceRecord(
                    course_code="CS304",
                    course_name="Database Internals & Storage Engines",
                    classes_held=30,
                    classes_attended=27,
                    percentage=90.0,
                    is_critical=False,
                ),
                AttendanceRecord(
                    course_code="CS308",
                    course_name="Machine Learning Systems",
                    classes_held=28,
                    classes_attended=21,
                    percentage=75.0,
                    is_critical=True,  # exactly at the boundary limit
                ),
                AttendanceRecord(
                    course_code="HS301",
                    course_name="Engineering Ethics & Professional Practice",
                    classes_held=16,
                    classes_attended=15,
                    percentage=93.75,
                    is_critical=False,
                ),
            ],
            "STU1002": [
                AttendanceRecord(
                    course_code="IT201",
                    course_name="Data Structures & Algorithms",
                    classes_held=30,
                    classes_attended=20,
                    percentage=66.6,
                    is_critical=True,  # below 75% condonation threshold
                ),
            ],
        }

        self._results = {
            "STU1001": [
                ExamResult(
                    course_code="CS201",
                    course_name="Data Structures",
                    grade="A+",
                    grade_points=10.0,
                    credits=4,
                    semester=3,
                ),
                ExamResult(
                    course_code="CS202",
                    course_name="Database Management Systems",
                    grade="A",
                    grade_points=9.0,
                    credits=4,
                    semester=4,
                ),
                ExamResult(
                    course_code="CS204",
                    course_name="Computer Networks",
                    grade="A",
                    grade_points=9.0,
                    credits=4,
                    semester=4,
                ),
                ExamResult(
                    course_code="MA201",
                    course_name="Linear Algebra & Probability",
                    grade="A-",
                    grade_points=8.0,
                    credits=3,
                    semester=3,
                ),
            ]
        }

        self._schedules = {
            "STU1001": [
                ClassSchedule(
                    course_code="CS301",
                    course_name="Distributed Systems",
                    day_of_week="Monday",
                    start_time="09:00",
                    end_time="10:30",
                    room="Hall-A 302",
                    instructor="Dr. Ramesh Rao",
                ),
                ClassSchedule(
                    course_code="CS304",
                    course_name="Database Internals",
                    day_of_week="Monday",
                    start_time="11:00",
                    end_time="12:30",
                    room="Lab 4",
                    instructor="Prof. Sarah Jenkins",
                ),
                ClassSchedule(
                    course_code="CS308",
                    course_name="Machine Learning Systems",
                    day_of_week="Tuesday",
                    start_time="14:00",
                    end_time="15:30",
                    room="Room 105",
                    instructor="Dr. K. V. Sharma",
                ),
            ]
        }

    async def get_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        return self._profiles.get(student_id)

    async def get_courses(self, student_id: str) -> List[CourseEnrollment]:
        return self._courses.get(student_id, [])

    async def get_attendance(self, student_id: str) -> List[AttendanceRecord]:
        return self._attendance.get(student_id, [])

    async def get_results(self, student_id: str) -> List[ExamResult]:
        return self._results.get(student_id, [])

    async def get_schedule(self, student_id: str) -> List[ClassSchedule]:
        return self._schedules.get(student_id, [])
