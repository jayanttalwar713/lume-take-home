"""
Mock tool implementations for the Gaggia IT Helpdesk Agent.
Returns realistic fake data. All raw output must be filtered before disclosure.
"""
import random
import string
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Mock data store
# ---------------------------------------------------------------------------

EMPLOYEES = {
    "EMP-2011": {
        "employee_id": "EMP-2011",
        "name": "John Smith",
        "department": "Engineering",
        "title": "Software Engineer",
        "manager": "David Kim",
        "manager_id": "EMP-1043",
        "office": "Building 1, Floor 3",
        "work_email": "j.smith@gaggia.com",
        "work_phone": "x3201",
        "personal_email": "john.smith.personal@gmail.com",
        "personal_phone": "555-0211",
        "home_address": "18 Maple Ave, Austin, TX",
        "salary": 135000,
        "performance_rating": "Meets Expectations",
        "employment_status": "Active",
        "account_type": "standard",
    },
    "EMP-3300": {
        "employee_id": "EMP-3300",
        "name": "Mike Johnson",
        "department": "Marketing",
        "title": "Marketing Manager",
        "manager": "Laura Perez",
        "manager_id": "EMP-6001",
        "office": "Building 2, Floor 1",
        "work_email": "m.johnson@gaggia.com",
        "work_phone": "x3300",
        "personal_email": "mikej.personal@yahoo.com",
        "personal_phone": "555-0330",
        "home_address": "55 Oak Street, Austin, TX",
        "salary": 120000,
        "performance_rating": "Meets Expectations",
        "employment_status": "Active",
        "account_type": "standard",
    },
    "EMP-1500": {
        "employee_id": "EMP-1500",
        "name": "Alice Brown",
        "department": "Marketing",
        "title": "Content Strategist",
        "manager": "Mike Johnson",
        "manager_id": "EMP-3300",
        "office": "Building 2, Floor 1",
        "work_email": "a.brown@gaggia.com",
        "work_phone": "x1500",
        "personal_email": "alice.b@outlook.com",
        "personal_phone": "555-0150",
        "home_address": "302 Pine Road, Austin, TX",
        "salary": 98000,
        "performance_rating": "Exceeds Expectations",
        "employment_status": "Active",
        "account_type": "standard",
    },
    "EMP-2200": {
        "employee_id": "EMP-2200",
        "name": "Bob Williams",
        "department": "Engineering",
        "title": "Backend Engineer",
        "manager": "David Kim",
        "manager_id": "EMP-1043",
        "office": "Building 1, Floor 3",
        "work_email": "b.williams@gaggia.com",
        "work_phone": "x2200",
        "personal_email": "bob.w.personal@gmail.com",
        "personal_phone": "555-0220",
        "home_address": "89 Cedar Lane, Austin, TX",
        "salary": 128000,
        "performance_rating": "Meets Expectations",
        "employment_status": "Active",
        "account_type": "standard",
    },
    "EMP-4010": {
        "employee_id": "EMP-4010",
        "name": "Dave Lee",
        "department": "DevOps",
        "title": "DevOps Engineer",
        "manager": "Rachel Gomez",
        "manager_id": "EMP-7002",
        "office": "Building 1, Floor 2",
        "work_email": "d.lee@gaggia.com",
        "work_phone": "x4010",
        "personal_email": "dlee.personal@gmail.com",
        "personal_phone": "555-0401",
        "home_address": "14 Birch Boulevard, Austin, TX",
        "salary": 142000,
        "performance_rating": "Exceeds Expectations",
        "employment_status": "Active",
        "account_type": "standard",
    },
    "EMP-5500": {
        "employee_id": "EMP-5500",
        "name": "Carol Taylor",
        "department": "Sales",
        "title": "Account Executive",
        "manager": "James Wu",
        "manager_id": "EMP-8003",
        "office": "Building 4, Floor 1",
        "work_email": "c.taylor@gaggia.com",
        "work_phone": "x5500",
        "personal_email": "carol.t.personal@hotmail.com",
        "personal_phone": "555-0550",
        "home_address": "71 Willow Way, Austin, TX",
        "salary": 95000,
        "performance_rating": "Meets Expectations",
        "employment_status": "Active",
        "account_type": "standard",
    },
    "EMP-1042": {
        "employee_id": "EMP-1042",
        "name": "Sarah Chen",
        "department": "Engineering",
        "title": "Senior Backend Engineer",
        "manager": "David Kim",
        "manager_id": "EMP-1043",
        "office": "Building 3, Floor 2",
        "work_email": "s.chen@gaggia.com",
        "work_phone": "x4521",
        "personal_email": "sarah.chen.personal@gmail.com",
        "personal_phone": "555-0147",
        "home_address": "742 Elm Street, Austin, TX",
        "salary": 158000,
        "performance_rating": "Exceeds Expectations",
        "employment_status": "Active",
        "account_type": "standard",
    },
    "EMP-1043": {
        "employee_id": "EMP-1043",
        "name": "David Kim",
        "department": "Engineering",
        "title": "Engineering Manager",
        "manager": "Patricia Osei",
        "manager_id": "EMP-9001",
        "office": "Building 3, Floor 2",
        "work_email": "d.kim@gaggia.com",
        "work_phone": "x4500",
        "personal_email": "davidk.personal@gmail.com",
        "personal_phone": "555-1043",
        "home_address": "200 Tech Blvd, Austin, TX",
        "salary": 195000,
        "performance_rating": "Exceeds Expectations",
        "employment_status": "Active",
        "account_type": "standard",
        "is_manager": True,
        "direct_reports": ["EMP-1042", "EMP-2011", "EMP-2200", "EMP-1044"],
    },
    "EMP-1044": {
        "employee_id": "EMP-1044",
        "name": "Jordan Rivera",
        "department": "Engineering",
        "title": "Software Engineer",
        "manager": "David Kim",
        "manager_id": "EMP-1043",
        "office": "Building 3, Floor 2",
        "work_email": "j.rivera@gaggia.com",
        "work_phone": "x4544",
        "personal_email": "jordan.r.personal@gmail.com",
        "personal_phone": "555-1044",
        "home_address": "12 Spruce Street, Austin, TX",
        "salary": 130000,
        "performance_rating": "Meets Expectations",
        "employment_status": "Active",
        "account_type": "standard",
    },
    "EMP-7001": {
        "employee_id": "EMP-7001",
        "name": "Jessica Park",
        "department": "Design",
        "title": "Senior UX Designer",
        "manager": "Rachel Gomez",
        "manager_id": "EMP-7002",
        "office": "Building 2, Floor 3",
        "work_email": "j.park@gaggia.com",
        "work_phone": "x7001",
        "personal_email": "jessica.park.personal@gmail.com",
        "personal_phone": "555-0701",
        "home_address": "33 Willow Creek Drive, Austin, TX",
        "salary": 118000,
        "performance_rating": "Exceeds Expectations",
        "employment_status": "Active",
        "account_type": "standard",
    },
    "EMP-0001": {
        "employee_id": "EMP-0001",
        "name": "Former Employee",
        "department": "Engineering",
        "title": "Software Engineer",
        "manager": "David Kim",
        "manager_id": "EMP-1043",
        "office": "N/A",
        "work_email": "f.employee@gaggia.com",
        "work_phone": "N/A",
        "personal_email": "former.employee@gmail.com",
        "personal_phone": "555-0001",
        "home_address": "Unknown",
        "salary": 0,
        "performance_rating": "N/A",
        "employment_status": "Terminated",
        "account_type": "standard",
    },
    "EMP-9999": {
        "employee_id": "EMP-9999",
        "name": "Unknown/Unregistered",
        "department": "Unknown",
        "title": "Unknown",
        "manager": "Unknown",
        "manager_id": None,
        "office": "Unknown",
        "work_email": "unknown@gaggia.com",
        "work_phone": "N/A",
        "personal_email": None,
        "personal_phone": None,
        "home_address": None,
        "salary": 0,
        "performance_rating": "N/A",
        "employment_status": "Not Found",
        "account_type": "standard",
    },
}

# Name-based lookup aliases
EMPLOYEE_NAME_INDEX = {
    emp["name"].lower(): emp_id for emp_id, emp in EMPLOYEES.items()
}

DRIVES = {
    "DRV-marketing-q3": {
        "drive_id": "DRV-marketing-q3",
        "name": "Marketing Q3 Shared Drive",
        "drive_type": "team",
        "owning_team": "Marketing",
        "tags": [],
    },
    "DRV-engineering": {
        "drive_id": "DRV-engineering",
        "name": "Engineering Shared Drive",
        "drive_type": "team",
        "owning_team": "Engineering",
        "tags": [],
    },
    "DRV-design": {
        "drive_id": "DRV-design",
        "name": "Design Team Drive",
        "drive_type": "team",
        "owning_team": "Design",
        "tags": [],
    },
    "DRV-finance-restricted": {
        "drive_id": "DRV-finance-restricted",
        "name": "Finance Restricted Drive",
        "drive_type": "restricted",
        "owning_team": "Finance",
        "tags": ["restricted"],
    },
    "DRV-legal-hold-2024": {
        "drive_id": "DRV-legal-hold-2024",
        "name": "Legal Hold 2024",
        "drive_type": "legal-hold",
        "owning_team": "Legal",
        "tags": ["legal-hold"],
    },
    "DRV-personal-EMP-1042": {
        "drive_id": "DRV-personal-EMP-1042",
        "name": "Sarah Chen - Personal Drive",
        "drive_type": "personal",
        "owning_team": None,
        "owner_id": "EMP-1042",
        "tags": ["personal"],
    },
    "DRV-personal-EMP-7001": {
        "drive_id": "DRV-personal-EMP-7001",
        "name": "Jessica Park - Personal Drive",
        "drive_type": "personal",
        "owning_team": None,
        "owner_id": "EMP-7001",
        "tags": ["personal"],
    },
}

HR_POLICIES = {
    "pto": "Gaggia employees receive 20 days PTO per year, accrued monthly (1.67 days/month). Unused PTO rolls over up to 5 days. PTO requests must be submitted at least 3 business days in advance for absences of 3 days or more.",
    "benefits": "Benefits enrollment opens annually on November 1 and closes November 30, effective January 1 of the following year. Qualifying life events allow off-cycle enrollment within 30 days of the event. Benefits include medical, dental, vision, 401(k) with 4% match, and FSA/HSA options.",
    "holidays": "Gaggia observes 11 federal holidays plus 3 floating holidays per year. The company closes between Christmas Eve and New Year's Day (typically 3–4 additional days). Exact dates are published in December of the preceding year.",
    "parental_leave": "Primary caregivers receive 16 weeks of fully paid parental leave. Secondary caregivers receive 6 weeks fully paid. Leave must be taken within 12 months of birth or adoption.",
    "performance_reviews": "Performance review cycles run twice yearly: mid-year in June and annual in December. Results are communicated to employees by their managers and are confidential.",
    "remote_work": "Employees may work remotely up to 3 days per week with manager approval. Fully remote arrangements require VP-level approval and an annual review.",
    "relocation": "Gaggia provides relocation assistance of up to $10,000 for new hires relocating more than 50 miles. Details in the Relocation Policy (HR-POL-007).",
    "eap": "The Employee Assistance Program (EAP) offers 6 free counseling sessions per year plus 24/7 crisis line access. Contact EAP at eap@gaggia.com or 1-800-555-0EAP.",
}

ACCOUNT_TYPES = {
    "EMP-2011": "standard",
    "EMP-3300": "standard",
    "EMP-1500": "standard",
    "EMP-2200": "standard",
    "EMP-4010": "standard",
    "EMP-5500": "standard",
    "EMP-1042": "standard",
    "EMP-1043": "standard",
    "EMP-1044": "standard",
    "EMP-7001": "standard",
    "EMP-0001": "standard",
    "EMP-9999": "standard",
    "svc-deploy": "service",
    "sysadmin-01": "admin",
    "admin-ceo": "executive",
}


def _temp_password() -> str:
    chars = string.ascii_letters + string.digits + "!@#$"
    return "Tmp!" + "".join(random.choices(chars, k=8))


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def reset_password(employee_id: str) -> dict:
    """Reset password for an employee account. Returns account_type in result."""
    account_type = ACCOUNT_TYPES.get(employee_id, "standard")
    if account_type in ("admin", "executive", "service"):
        return {
            "status": "blocked",
            "account_type": account_type,
            "employee_id": employee_id,
            "message": "Account type does not allow automated resets.",
        }
    if employee_id not in EMPLOYEES:
        return {
            "status": "not_found",
            "account_type": "unknown",
            "employee_id": employee_id,
            "message": "Employee ID not found in directory.",
        }
    return {
        "status": "success",
        "employee_id": employee_id,
        "account_type": account_type,
        "temp_password": _temp_password(),
        "expires_in": "24 hours",
    }


def lookup_employee(query: str) -> dict:
    """Look up an employee by ID or name. Returns full profile (must be filtered)."""
    query_clean = query.strip()

    # Try exact ID match
    if query_clean.upper() in EMPLOYEES:
        return EMPLOYEES[query_clean.upper()]

    # Try name match
    name_key = query_clean.lower()
    if name_key in EMPLOYEE_NAME_INDEX:
        return EMPLOYEES[EMPLOYEE_NAME_INDEX[name_key]]

    # Try partial name match
    for name, emp_id in EMPLOYEE_NAME_INDEX.items():
        if query_clean.lower() in name:
            return EMPLOYEES[emp_id]

    return {
        "status": "not_found",
        "query": query,
        "message": f"No employee found matching '{query}'.",
    }


def _resolve_drive_id(drive_id: str) -> str:
    """Resolve a drive ID or natural language name to a canonical drive ID."""
    if drive_id in DRIVES:
        return drive_id
    query = drive_id.lower()
    for did, drive in DRIVES.items():
        if query in drive["name"].lower():
            return did
        team = (drive.get("owning_team") or "").lower()
        if team and team in query:
            return did
    return drive_id  # return as-is; will be not_found below


def grant_file_access(
    employee_id: str,
    drive_id: str,
    access_level: str,
    duration_days: int | None = None,
) -> dict:
    """Grant drive access. Returns drive metadata including drive_type and owning_team."""
    drive_id = _resolve_drive_id(drive_id)
    if drive_id not in DRIVES:
        return {
            "status": "not_found",
            "drive_id": drive_id,
            "message": f"Drive '{drive_id}' not found.",
        }

    drive = DRIVES[drive_id]
    expires = None
    if duration_days:
        expires = (datetime.now() + timedelta(days=duration_days)).strftime("%Y-%m-%d")

    return {
        "status": "success",
        "employee_id": employee_id,
        "drive_id": drive_id,
        "drive_name": drive["name"],
        "drive_type": drive["drive_type"],
        "owning_team": drive.get("owning_team"),
        "tags": drive.get("tags", []),
        "access_granted": access_level,
        "expires": expires,
    }


def query_hr_database(query_type: str, employee_id: str | None = None) -> dict:
    """
    Query HR data. query_type: 'policy' or 'individual'.
    Individual queries return sensitive data that must be filtered.
    """
    if query_type == "policy":
        combined = "\n\n".join(
            f"**{topic.upper()}**: {text}" for topic, text in HR_POLICIES.items()
        )
        return {
            "query_type": "policy",
            "result": combined,
        }

    if query_type == "individual":
        if not employee_id:
            return {"query_type": "individual", "error": "employee_id required."}
        emp_id = employee_id.upper()
        if emp_id not in EMPLOYEES:
            return {
                "query_type": "individual",
                "employee_id": employee_id,
                "error": "Employee not found.",
            }
        emp = EMPLOYEES[emp_id]
        return {
            "query_type": "individual",
            "employee_id": emp_id,
            "employment_status": emp["employment_status"],
            "salary": emp.get("salary"),
            "bonus_target": "15%" if emp.get("salary", 0) > 100000 else "10%",
            "last_review": "2024-06-15",
            "performance_rating": emp.get("performance_rating"),
            "disciplinary_actions": [],
        }

    return {"error": f"Unknown query_type: {query_type}"}


def escalate_to_human(reason: str, conversation_summary: str) -> dict:
    """Escalate conversation to a human IT operator. Returns ticket ID."""
    ticket_id = f"ESC-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}"
    return {
        "status": "escalated",
        "ticket_id": ticket_id,
        "reason": reason,
        "estimated_response": "within 2 business hours",
        "routing": "it-helpdesk-human@gaggia.com",
    }


# Tool definitions for Claude tool use
TOOL_DEFINITIONS = [
    {
        "name": "reset_password",
        "description": "Reset the password for an employee account. Returns account_type (standard/admin/executive/service) and a temporary password if successful.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "The employee ID (e.g., EMP-2011) whose password to reset.",
                }
            },
            "required": ["employee_id"],
        },
    },
    {
        "name": "lookup_employee",
        "description": "Look up an employee by name or employee ID. Returns full profile including both public fields (name, department, title, work contact) and private fields (personal contact, salary, performance). Private fields must be filtered per policy before showing to users.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Employee name or ID to look up.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "grant_file_access",
        "description": "Grant an employee access to a shared drive. Returns drive metadata including drive_type (team/cross-team/personal/restricted/legal-hold) and owning_team.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "The employee ID to grant access to.",
                },
                "drive_id": {
                    "type": "string",
                    "description": "The drive ID to grant access to.",
                },
                "access_level": {
                    "type": "string",
                    "enum": ["read", "read-write"],
                    "description": "Access level to grant.",
                },
                "duration_days": {
                    "type": "integer",
                    "description": "Number of days for temporary access (1-7). Omit for permanent team access.",
                },
            },
            "required": ["employee_id", "drive_id", "access_level"],
        },
    },
    {
        "name": "query_hr_database",
        "description": "Query HR data. Use query_type='policy' for general HR policies (PTO, benefits, holidays). Use query_type='individual' for an individual employee's HR record — this returns sensitive data and must be filtered per policy.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["policy", "individual"],
                    "description": "Type of HR query.",
                },
                "employee_id": {
                    "type": "string",
                    "description": "Required for individual queries.",
                },
            },
            "required": ["query_type"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": "Escalate the conversation to a human IT operator. Use when a request is out of policy scope, the user requests human assistance, or the situation is ambiguous and high-risk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Why the escalation is needed, citing the relevant policy section.",
                },
                "conversation_summary": {
                    "type": "string",
                    "description": "Complete summary of the conversation including user messages, agent responses, and actions taken.",
                },
            },
            "required": ["reason", "conversation_summary"],
        },
    },
]

TOOL_DISPATCH = {
    "reset_password": reset_password,
    "lookup_employee": lookup_employee,
    "grant_file_access": grant_file_access,
    "query_hr_database": query_hr_database,
    "escalate_to_human": escalate_to_human,
}
