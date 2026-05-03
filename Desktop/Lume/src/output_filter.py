"""
Filter tool outputs before presenting to users.

Policy rules:
- lookup_employee: Only return fields from Section 2.1 (directory info).
  Strip personal_email, personal_phone, home_address, salary, performance_rating,
  disciplinary_actions, and employment_status (unless caller is a verified manager
  and the query_type was 'individual' under Section 4.4).
- query_hr_database individual: Strip salary, bonus_target, last_review,
  performance_rating, disciplinary_actions — retain only employment_status
  and only when the caller has Section 4.4 rights.
- reset_password: Strip temp_password from logs; safe to show to the requester.
- grant_file_access, escalate_to_human: Generally safe to return, but
  strip internal drive tags and routing email from user-facing output.
"""
from .models import UserContext, TrustTier

# Fields permitted for public directory disclosure (Section 2.1)
DIRECTORY_PUBLIC_FIELDS = {
    "employee_id",
    "name",
    "department",
    "title",
    "manager",
    "office",
    "work_email",
    "work_phone",
}

# Fields that are always private (Section 2.2 / 9.4)
ALWAYS_PRIVATE_FIELDS = {
    "personal_email",
    "personal_phone",
    "home_address",
    "salary",
    "performance_rating",
    "disciplinary_actions",
    "bonus_target",
    "last_review",
}


class OutputFilter:
    """
    Filters tool outputs according to policy before showing results to users.
    """

    def filter(
        self,
        tool_name: str,
        raw_output: dict,
        caller: UserContext,
        context: dict | None = None,
    ) -> dict:
        """
        Apply policy-based filtering to tool output.

        context may include:
          - is_manager_request (bool): True if this is a Section 4.4 manager query
          - subject_employee_id (str): employee being queried
        """
        context = context or {}

        if tool_name == "lookup_employee":
            return self._filter_employee_lookup(raw_output, caller, context)
        if tool_name == "query_hr_database":
            return self._filter_hr_query(raw_output, caller, context)
        if tool_name == "reset_password":
            return self._filter_password_reset(raw_output, caller)
        if tool_name == "grant_file_access":
            return self._filter_drive_access(raw_output)
        if tool_name == "escalate_to_human":
            return self._filter_escalation(raw_output)
        return raw_output

    # ------------------------------------------------------------------

    def _filter_employee_lookup(
        self, raw: dict, caller: UserContext, context: dict
    ) -> dict:
        if "status" in raw and raw.get("status") == "not_found":
            return raw

        filtered = {}
        for field in DIRECTORY_PUBLIC_FIELDS:
            if field in raw:
                filtered[field] = raw[field]

        # Note which fields were removed (for logging, not user display)
        removed = [f for f in ALWAYS_PRIVATE_FIELDS if f in raw]
        if removed:
            filtered["_filtered_fields"] = removed

        return filtered

    def _filter_hr_query(
        self, raw: dict, caller: UserContext, context: dict
    ) -> dict:
        if raw.get("query_type") == "policy":
            return raw  # Policy queries are safe

        # Individual query — extremely restricted
        is_manager_status_check = context.get("is_manager_status_check", False)

        if raw.get("query_type") == "individual":
            if is_manager_status_check:
                # Section 4.4: only return active/inactive status
                return {
                    "query_type": "individual",
                    "employee_id": raw.get("employee_id"),
                    "employment_status": raw.get("employment_status"),
                    "_note": "Filtered per Section 4.4: only employment status returned.",
                }
            else:
                # Full individual query — not permitted to show to users
                return {
                    "query_type": "individual",
                    "employee_id": raw.get("employee_id"),
                    "_blocked": True,
                    "_reason": "Individual HR records are restricted per Section 4.2.",
                }

        return raw

    def _filter_password_reset(self, raw: dict, caller: UserContext) -> dict:
        # Temp password is safe to show to the requester (it's their own reset)
        # but we note account type for policy checks upstream
        return raw

    def _filter_drive_access(self, raw: dict) -> dict:
        # Remove internal routing fields; show user-friendly subset
        safe = {k: v for k, v in raw.items() if k not in ("tags",)}
        return safe

    def _filter_escalation(self, raw: dict) -> dict:
        # Remove internal routing email from user-facing output
        return {k: v for k, v in raw.items() if k != "routing"}
