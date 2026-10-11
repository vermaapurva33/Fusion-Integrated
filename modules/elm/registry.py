"""Permissions this module recognises. No nav: it has no screens of its own."""

PERMISSIONS = [
    ("elm.leave_type.list", "List Leave Types"),
    ("elm.balance.list", "List Leave Balances"),
    ("elm.application.list", "List Leave Applications"),
    ("elm.application.create", "Create Leave Application"),
    ("elm.application.withdraw", "Withdraw Leave Application"),
]

SYSTEM_PERMISSIONS = []

_STAFF = ["elm.leave_type.list", "elm.balance.list", "elm.application.list", "elm.application.create", "elm.application.withdraw"]

#: Keyed by the designation name as it exists in globals_designation.
ROLE_GRANTS = {
    "faculty": _STAFF,
    "staff": _STAFF,
}
