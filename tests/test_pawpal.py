from pawpal_system import Owner, Pet, Task, Scheduler


def test_mark_complete_changes_status():
    """Task completion: mark_complete() should set is_completed to True."""
    task = Task(name="Morning Walk", task_type="walk", duration_minutes=30, priority="high")
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    """Task addition: adding a task to a Pet should increase its task count."""
    pet = Pet(name="Buddy", species="Dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Breakfast", task_type="feeding", duration_minutes=10, priority="high"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(name="Evening Walk", task_type="walk", duration_minutes=20, priority="medium"))
    assert len(pet.tasks) == 2
