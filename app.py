"""Simple Flask boilerplate for a 60-minute machine coding interview."""

import logging
from flask import Flask, jsonify, request

# ==============================================================================
# 1. CONSOLE LOGGER (prints timestamp, level, and message to the terminal)
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ==============================================================================
# 2. IN-MEMORY STORAGE (just a plain Python dictionary, no database needed)
# ==============================================================================
employees = {
    "emp-101" : {"name": "Asha", "daysLeft": 1},
    "emp-102" : {"name": "Ravi", "daysLeft": 1}
}
leaves = {}  # maps id -> item dict (you can also use a plain list: items = [])


# ==============================================================================
# 3. SERVICE / BUSINESS LOGIC LAYER (all validation and rules live here)
# ==============================================================================
def fail(message, status=400):
    logger.warning("Request failed (%s): %s", status, message)
    return {"error": message}, status


def add_leave(data):
    # 1. Check that we actually got a JSON object (a Python dict)
    if type(data) is not dict:
        return fail("Request body must be valid JSON.", 400)
    #2 validate employee id
    employeeId = data.get("employeeId")
    if type(employeeId) is not str or employeeId.strip() == "" or employeeId not in employees:
        return fail("'employeeId' must be a non-empty string and should be a current employee", 400)

    # # 2. Validate 'name'
    # name = data.get("name")
    # if type(name) is not str or name.strip() == "":
    #     return fail("'name' must be a non-empty string.", 400)

    # 3. Validate 'quantity' (defaults to 1 if omitted)
    days = data.get("days", 1)
    emp = employees[employeeId]
    if type(days) is not int or days > emp["daysLeft"] or days < 1:
        return fail("'days' must be a positive integer, and be available for the particular employee", 400)
    reason = data.get("reason")
    # 4. Save into our dict and log
    leave = {
        "lid" : len(leaves)+1,
        "employeeId": employeeId,
        "days": days,
        "reason": reason,
        "status" : "PENDING",
    }
    leaves[leave["lid"]] = leave 
    logger.info("Created leave request for employeeId=%s for days=%s and reaosn=%s", leave["employeeId"], leave["days"], leave["reason"])
    return leave, 201

def approve_leave(lid):
    leave = leaves[lid]
    leave["status"] = "APPROVED"
    empid = leave["employeeId"]
    emp = employees[empid]
    days = leave[days]
    # if days > emp[daysLeft]:
    #     return fail("", 400)
    emp[daysLeft] -= leave["days"]
    logger.info("Approved leave request for employeeId=%s for days=%s and reaosn=%s", leave["employeeId"], leave["days"], leave["reason"])
    res = {
        "leaveId" : lid,
        "status" : "APPROVED",
        "daysLeft" : emp[daysLeft],
    }
    
    return res, 201

# ==============================================================================
# 4. HTTP LAYER (Flask routes only read the request and return JSON responses)
# ==============================================================================
app = Flask(__name__)


@app.post("/leaves")
def apply_leave():
    # silent=True returns None instead of throwing an error on bad JSON
    data = request.get_json(silent=True)
    result, status = add_leave(data)
    return jsonify(result), status
@app.post("/leaves/<lid>/approve")
def approve_leave(lid):
    #data = request.get_json(silent=True)
    result, status = approve_leave(lid)
    return jsonify(result), status

if __name__ == "__main__":
    logger.info("Server running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)


# --- HOW TO HIT THE ENDPOINTS ---
# 1. Success (201 Created):
# curl -i -X POST http://127.0.0.1:5000/items \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Notebook", "quantity": 3}'
#
# 2. Blank name (400 Bad Request):
# curl -i -X POST http://127.0.0.1:5000/items \
#   -H "Content-Type: application/json" \
#   -d '{"name": "   ", "quantity": 2}'
#
# 3. Invalid quantity (400 Bad Request):
# curl -i -X POST http://127.0.0.1:5000/items \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Pen", "quantity": 0}'
#
# 4. Invalid JSON body (400 Bad Request):
# curl -i -X POST http://127.0.0.1:5000/items \
#   -H "Content-Type: application/json" \
#   -d 'not-json'
