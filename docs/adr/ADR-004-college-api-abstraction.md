# ADR-004: College API Abstraction & Student Data Privacy

## Status
Accepted

## Context
The Academic Advisor agent provides course planning, attendance tracking, and degree progress guidance. In production, this data resides within institutional Student Information Systems (SIS) / ERPs (e.g., Banner, Canvas, PeopleSoft, or custom university portals). However, demanding a live production college API during local development or testing halts development, while hardcoding student records couples the platform to a single institution. Crucially, under no circumstances should the system fabricate absent student records.

## Decision
Define an abstract provider interface `AcademicDataProvider`:
```python
class AcademicDataProvider(ABC):
    @abstractmethod
    async def get_student_profile(self, student_id: str) -> Optional[StudentProfile]: ...
    @abstractmethod
    async def get_courses(self, student_id: str) -> List[CourseEnrollment]: ...
    @abstractmethod
    async def get_attendance(self, student_id: str) -> List[AttendanceRecord]: ...
    @abstractmethod
    async def get_results(self, student_id: str) -> List[ExamResult]: ...
    @abstractmethod
    async def get_schedule(self, student_id: str) -> List[ClassSchedule]: ...
```
Two concrete implementations are provided:
1. `MockAcademicDataProvider`: Provides deterministic, realistic synthetic student profiles, attendance records, and grades for testing and demo purposes without network dependencies.
2. `ExternalCollegeAPIProvider`: A production-ready HTTP adapter that queries institutional endpoints using secure credentials and timeouts.

If the institutional API is unavailable or unconfigured, student-specific queries return an explicit, controlled "Student data integration currently unavailable" notification. General academic policy RAG and curriculum guidance continue functioning unimpeded.

## Alternatives Considered
1. **Mocking directly within agent prompts**:
   - *Rejected*: Leads to LLM hallucination and arithmetic errors.
2. **Requiring a real college API endpoint before running the application**:
   - *Rejected*: Prevents standalone installation, open-source adoption, and offline testing.

## Consequences
- **Positive**: Platform can be run and tested anywhere; clean adapter architecture allows institutions to plug in custom SIS connectors without modifying agent logic.
- **Negative**: Mock provider data must be kept realistic and consistent with academic business rules.
