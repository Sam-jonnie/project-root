# Full-Stack Role-Based Project Management Matrix Dashboard (FastAPI + React)

A containerized, full-stack project management platform engineered with an asynchronous backend engine, strict Role-Based Access Control (RBAC), and cool UI

## Live System Architecture Links

- **React UI Portal**: `http://localhost:3000`
- **Asynchronous OpenAPI Swagger Engine**: `http://localhost:8000/docs`

---

## Rigorous Role-Based Authorization Framework (RBAC)

The system automatically limits endpoint consumption and dashboard parameters based on three distinct tiers:

1.  **Admin (`Admin`)**
    - _Clearance Level_: Global Master Control.
    - _Privileges_: Complete database mutation, project/task channel initialization, and destructive structural **Purge (Soft-Delete)** options.
2.  **Manager (`Manager`)**
    - _Clearance Level_: Operational Supervision.
    - _Privileges_: Initialize project tracking headers, mount new roadmap tasks, assign parameters, and append context notes. Blocked from administrative record purging.
3.  **Member (`Member`)**
    - _Clearance Level_: Task Tracking & Execution.
    - _Privileges_: Strictly restricted to changing task states (**Status Switcher Dropdowns**). Mutating titles, descriptions, due dates, or deleting entries triggers an immediate `403 Forbidden` API exception block.

---

## Implemented Requirements & Bonus Features

- **100% Standalone Bearer Authorization**: Configured using a pure `HTTPBearer` scheme in the backend router context. The Swagger UI interface presents _exactly one unified token text input field_, with all username/password blocks removed per specifications.
- **3-Column Kanban Board Grid**: Tasks are broken down positionally into horizontal `Pending`, `In Progress`, and `Completed` columns styled dynamically via CSS flex layouts.
- **Slide-Out Discussion Thread Drawers**: Clicking any task card activates an overlay sidebar feed that asynchronously fetches and posts live database comment notes.
- **Soft-Delete Security Safeguards**: Purging entries switches an internal database `is_deleted = Column(Boolean)` flag layout, wiping row visibility without erasing transaction histories.
- **Background Task Simulated Emailers**: Intercepts task assignments via FastAPI `BackgroundTasks` threads, logging outbox alert dispatches to targets cleanly without freezing route processing speeds.

---

## Local Compilation & Execution Strategy

To deploy and clear the entire platform stack from a clean terminal window, run:

```bash
# 1. Clear out container states and cached volumes cleanly
docker-compose down -v

# 2. Rebuild image dependency layers and fire up the cluster
docker-compose up --build

# 3. Populate default operational mock data matrices (Run in a separate window)
docker-compose exec backend python seed.py
```

### Sandbox Seed Profiles Matrix

(Password is `securepassword` for all accounts)

- **Admin**: `deepak@company.com`
- **Manager**: `sarah@company.com`
- **Member 1**: `alex@company.com`
- **Member 2**: `elena@company.com`

### Author
Samuel Jonathan, Stackly
