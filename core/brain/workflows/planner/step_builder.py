# A helper function to create a step dictionary for trace recording
def create_step(
    task_id: str,
    step_index: int,
    name: str,
    task_type: str,
    objective: str,
    assigned_agent_type: str = "",
) -> dict:

    return {
        "task_id": task_id,
        "step_index": step_index,
        "name": name,
        "task_type": task_type,
        "objective": objective,
        "assigned_agent_type": assigned_agent_type,
        "assigned_agent_id": None,
        "required_tools": [],
        "input_schema": f"{name}_input",
        "output_schema": f"{name}_output",
        "depends_on": [],
        "retry_policy": {
            "max_retries": 2,
            "fallback_allowed": True
        },
        "validation_rule": {
            "type": "schema_validation"
        },
        "status": "pending",
        "notes": ""
    }
