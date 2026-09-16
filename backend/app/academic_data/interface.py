from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import date, time


class StudentProfile(BaseModel):
    student_id: str
    full_name: str
    email: str
    program: str
    department: str
    semester: int
    cgpa: float
    credits_earned: int
    credits_required: int
    academic_status: str  # 'Good Standing', 'Probation', 'Dean's List'


class CourseEnrollment(BaseModel):
    course_code: str
    course_name: str
    credits: int
    instructor: str
    semester: int
    status: str  # 'Enrolled', 'Completed', 'Dropped'
    prerequisites: List[str] = Field(default_factory=list)


class AttendanceRecord(BaseModel):
    course_code: str
    course_name: str
    classes_held: int
    classes_attended: int
    percentage: float
    is_critical: bool = False  # Critical if < 75% according to standard regulations


class ExamResult(BaseModel):
    course_code: str
    course_name: str
    grade: str
    grade_points: float
    credits: int
    semester: int


class ClassSchedule(BaseModel):
    course_code: str
    course_name: str
    day_of_week: str  # 'Monday', 'Tuesday', etc.
    start_time: str
    end_time: str
    room: str
    instructor: str


class AcademicDataProvider(ABC):
    @abstractmethod
    async def get_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        """Fetch student profile information."""
        pass

    @abstractmethod
    async def get_courses(self, student_id: str) -> List[CourseEnrollment]:
        """Fetch current and past course enrollments."""
        pass

    @abstractmethod
    async def get_attendance(self, student_id: str) -> List[AttendanceRecord]:
        """Fetch current attendance records and percentages."""
        pass

    @abstractmethod
    async def get_results(self, student_id: str) -> List[ExamResult]:
        """Fetch grade transcripts and historical semester results."""
        pass

    @abstractmethod
    async def get_schedule(self, student_id: str) -> List[ClassSchedule]:
        """Fetch weekly class schedule."""
        pass
