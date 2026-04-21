import pytest
from app.main import (
    fetch_all_tasks,
    generate_productivity_report,
    DeveloperTask,
    TaskStatus,
    MOCK_TASKS,
)


class TestFetchAllTasks:
    """Tests for the fetch_all_tasks async function."""

    @pytest.mark.asyncio
    async def test_fetch_all_tasks_returns_list(self):
        """Test that fetch_all_tasks returns a list of DeveloperTask objects."""
        tasks = await fetch_all_tasks()
        assert isinstance(tasks, list)
        assert all(isinstance(task, DeveloperTask) for task in tasks)

    @pytest.mark.asyncio
    async def test_fetch_all_tasks_returns_all_mock_tasks(self):
        """Test that fetch_all_tasks returns all mock tasks."""
        tasks = await fetch_all_tasks()
        assert len(tasks) == len(MOCK_TASKS)

    @pytest.mark.asyncio
    async def test_fetch_all_tasks_task_content(self):
        """Test that returned tasks contain correct data."""
        tasks = await fetch_all_tasks()
        task_ids = {task.task_id for task in tasks}
        expected_ids = set(MOCK_TASKS.keys())
        assert task_ids == expected_ids

    @pytest.mark.asyncio
    async def test_fetch_all_tasks_task_statuses(self):
        """Test that returned tasks have valid statuses."""
        tasks = await fetch_all_tasks()
        for task in tasks:
            assert task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETE]

    @pytest.mark.asyncio
    async def test_fetch_all_tasks_task_hours_spent(self):
        """Test that returned tasks have non-negative hours_spent."""
        tasks = await fetch_all_tasks()
        for task in tasks:
            assert task.hours_spent >= 0.0


class TestGenerateProductivityReport:
    """Tests for the generate_productivity_report async function."""

    @pytest.mark.asyncio
    async def test_generate_productivity_report_returns_correct_type(self):
        """Test that generate_productivity_report returns a ProductivityReport."""
        from app.main import ProductivityReport
        report = await generate_productivity_report()
        assert isinstance(report, ProductivityReport)

    @pytest.mark.asyncio
    async def test_generate_productivity_report_total_tasks(self):
        """Test that total_tasks matches the number of tasks."""
        report = await generate_productivity_report()
        assert report.total_tasks == len(MOCK_TASKS)

    @pytest.mark.asyncio
    async def test_generate_productivity_report_total_hours_calculation(self):
        """Test that total_hours_spent is calculated correctly."""
        report = await generate_productivity_report()
        expected_hours = sum(task.hours_spent for task in MOCK_TASKS.values())
        assert report.total_hours_spent == round(expected_hours, 2)

    @pytest.mark.asyncio
    async def test_generate_productivity_report_completion_rate_range(self):
        """Test that completion_rate is between 0 and 1."""
        report = await generate_productivity_report()
        assert 0.0 <= report.completion_rate <= 1.0

    @pytest.mark.asyncio
    async def test_generate_productivity_report_completion_rate_decimal_places(self):
        """Test that completion_rate has at most 2 decimal places."""
        report = await generate_productivity_report()
        # Check if it's a valid float with proper rounding
        assert isinstance(report.completion_rate, float)

    @pytest.mark.asyncio
    async def test_generate_productivity_report_fields_are_numeric(self):
        """Test that numeric fields are actual numbers."""
        report = await generate_productivity_report()
        assert isinstance(report.total_tasks, int)
        assert isinstance(report.completed_tasks, int)
        assert isinstance(report.total_hours_spent, float)
        assert isinstance(report.completion_rate, float)

    @pytest.mark.asyncio
    async def test_generate_productivity_report_completed_tasks_non_negative(self):
        """Test that completed_tasks is non-negative."""
        report = await generate_productivity_report()
        assert report.completed_tasks >= 0

    @pytest.mark.asyncio
    async def test_generate_productivity_report_completed_tasks_not_exceeds_total(self):
        """Test that completed_tasks does not exceed total_tasks."""
        report = await generate_productivity_report()
        assert report.completed_tasks <= report.total_tasks


class TestTaskStatusEnum:
    """Tests for the TaskStatus enum."""

    def test_task_status_values(self):
        """Test that TaskStatus enum has expected values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETE.value == "complete"

    def test_task_status_is_string_enum(self):
        """Test that TaskStatus members can be used as strings."""
        assert isinstance(TaskStatus.PENDING, str)
        assert isinstance(TaskStatus.IN_PROGRESS, str)
        assert isinstance(TaskStatus.COMPLETE, str)


class TestDeveloperTaskModel:
    """Tests for the DeveloperTask Pydantic model."""

    def test_developer_task_creation_with_all_fields(self):
        """Test creating a DeveloperTask with all fields."""
        task = DeveloperTask(
            task_id=99,
            title="Test Task",
            status=TaskStatus.IN_PROGRESS,
            hours_spent=5.5
        )
        assert task.task_id == 99
        assert task.title == "Test Task"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.hours_spent == 5.5

    def test_developer_task_default_status(self):
        """Test that status defaults to PENDING."""
        task = DeveloperTask(task_id=1, title="Test Task")
        assert task.status == TaskStatus.PENDING

    def test_developer_task_default_hours_spent(self):
        """Test that hours_spent defaults to 0.0."""
        task = DeveloperTask(task_id=1, title="Test Task")
        assert task.hours_spent == 0.0

    def test_developer_task_zero_hours(self):
        """Test creating a task with zero hours spent."""
        task = DeveloperTask(task_id=1, title="Test Task", hours_spent=0.0)
        assert task.hours_spent == 0.0

    def test_developer_task_high_hours(self):
        """Test creating a task with high hours spent."""
        task = DeveloperTask(task_id=1, title="Test Task", hours_spent=100.5)
        assert task.hours_spent == 100.5
