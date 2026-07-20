import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './Dashboard.css';

export default function Dashboard({ token, role, onLogout }) {
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [newProjName, setNewProjName] = useState('');
  const [selectedProjId, setSelectedProjId] = useState('');
  const [activeTask, setActiveTask] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');

  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskProjId, setNewTaskProjId] = useState('');
  const [newTaskAssignee, setNewTaskAssignee] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState('Low');

  const canManage = role === 'Admin' || role === 'Manager';
  const apiOpts = { headers: { Authorization: `Bearer ${token}` } };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const pRes = await axios.get('http://localhost:8000/projects', apiOpts);
      setProjects(pRes.data);

      if (pRes.data && pRes.data.length > 0) {
        setSelectedProjId(prev => prev || pRes.data[0].id);
        setNewTaskProjId(prev => prev || pRes.data[0].id);
      } else {
        setSelectedProjId('');
      }

      const tRes = await axios.get('http://localhost:8000/tasks', apiOpts);
      setTasks(tRes.data);

      if (canManage) {
        const uRes = await axios.get('http://localhost:8000/users', apiOpts);
        setUsers(uRes.data);
      }
    } catch (err) {
      console.error("Data matrix sync failure", err);
    }
  };

  const createProject = async () => {
    if(!newProjName) return;
    try {
      await axios.post('http://localhost:8000/projects', { name: newProjName }, apiOpts);
      setNewProjName('');
      fetchData();
    } catch(err) {
      alert("Unauthorized operational interaction.");
    }
  };

  const softDeleteProject = async (projId) => {
    if(!window.confirm("Soft-delete this project channel record?")) return;
    try {
      await axios.delete(`http://localhost:8000/projects/${projId}`, apiOpts);
      fetchData();
    } catch (err) {
      alert("Access Denied: Administrative authority requirements unmet.");
    }
  };

  const createTask = async (e) => {
    e.preventDefault();
    if (!newTaskTitle || !newTaskProjId) return;
    try {
      await axios.post('http://localhost:8000/tasks', {
        title: newTaskTitle,
        project_id: Number(newTaskProjId),
        assigned_to: newTaskAssignee ? Number(newTaskAssignee) : null,
        priority: newTaskPriority,
      }, apiOpts);
      setNewTaskTitle('');
      setNewTaskAssignee('');
      fetchData();
    } catch (err) {
      const detail = err.response?.data?.detail;
      const status = err.response?.status;
      if (status === 401 || status === 403) {
        alert(detail || "Unauthorized operational interaction.");
      } else {
        alert(`Failed to create task (${status || 'network error'}): ${detail || err.message}`);
      }
    }
  };

  const handleStatusChange = async (taskId, nextStatus) => {
    try {
      await axios.put(`http://localhost:8000/tasks/${taskId}`, { status: nextStatus }, apiOpts);
      fetchData();
      if(activeTask && activeTask.id === taskId) {
        setActiveTask(prev => ({ ...prev, status: nextStatus }));
      }
    } catch (err) {
      alert("Failed to update status parameters.");
    }
  };

  const selectTaskDetails = async (task) => {
    setActiveTask(task);
    setNewComment('');
    try {
      const res = await axios.get(`http://localhost:8000/tasks/${task.id}/comments`, apiOpts);
      setComments(res.data);
    } catch (err) {
      console.error("Could not fetch comment nodes.", err);
    }
  };

  const postComment = async (e) => {
    e.preventDefault();
    if(!newComment || !activeTask) return;
    try {
      const res = await axios.post(`http://localhost:8000/tasks/${activeTask.id}/comments`, { comment: newComment }, apiOpts);
      setComments(prev => [...prev, res.data]);
      setNewComment('');
    } catch (err) {
      alert("Failed to anchor comment entry.");
    }
  };

  return (
    <div className="dashboard-layout">
      <header className="dash-header">
        <h1>Workspace Management Matrix</h1>
        <button className="logout-btn" onClick={onLogout}>Logout</button>
      </header>

      <div className="dashboard-content-grid">
        <section className="panel project-panel">
          <h3>Project Pipelines</h3>
          {canManage && (
            <div className="action-row">
              <input value={newProjName} placeholder="New project name..." onChange={e=>setNewProjName(e.target.value)}/>
              <button onClick={createProject}>Create</button>
            </div>
          )}
          <ul className="project-list">
            {projects.map(p => (
              <li key={p.id} className="project-item">
                <span>📂 {p.name}</span>
                {role === 'Admin' && (
                  <button className="delete-btn" onClick={() => softDeleteProject(p.id)}>Delete</button>
                )}
              </li>
            ))}
          </ul>
        </section>

        <section className="kanban-wrapper">
          <h3>Operational Task Board Matrix</h3>

          {canManage && (
            <form className="action-row" onSubmit={createTask}>
              <input
                value={newTaskTitle}
                placeholder="New task title..."
                onChange={e => setNewTaskTitle(e.target.value)}
                required
              />
              <select value={newTaskProjId} onChange={e => setNewTaskProjId(e.target.value)} required>
                <option value="" disabled>Project...</option>
                {projects.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
              <select value={newTaskAssignee} onChange={e => setNewTaskAssignee(e.target.value)}>
                <option value="">Unassigned</option>
                {users.map(u => (
                  <option key={u.id} value={u.id}>{u.full_name}</option>
                ))}
              </select>
              <select value={newTaskPriority} onChange={e => setNewTaskPriority(e.target.value)}>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
              <button type="submit">Assign Task</button>
            </form>
          )}

          <div className="kanban-grid">
            {['Pending', 'In Progress', 'Completed'].map(statusType => (
              <div key={statusType} className="kanban-column">
                <h4 className={`column-title ${statusType.toLowerCase().replace(' ', '-')}-header`}>
                  {statusType === 'Pending' ? 'Pending' : statusType === 'In Progress' ? '⚡ In Progress' : '✅ Completed'}
                </h4>
                <div className="card-container">
                  {tasks.filter(t => t.status === statusType).map(t => (
                    <div key={t.id} className="kanban-card" onClick={() => selectTaskDetails(t)}>
                      <h5>{t.title}</h5>
                      <div className="card-controls" onClick={e => e.stopPropagation()}>
                        <select value={t.status} onChange={(e) => handleStatusChange(t.id, e.target.value)}>
                          <option value="Pending">Pending</option>
                          <option value="In Progress">In Progress</option>
                          <option value="Completed">Completed</option>
                        </select>
                        <span className={`priority-tag ${t.priority}`}>{t.priority}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      {activeTask && (
        <div className="modal-backdrop" onClick={() => setActiveTask(null)}>
          <div className="comment-drawer" onClick={e => e.stopPropagation()}>
            <div className="drawer-header">
              <h4>{activeTask.title} <span className="p-tag">{activeTask.priority}</span></h4>
              <button onClick={() => setActiveTask(null)}>✕</button>
            </div>
            
            <div className="comment-feed">
              <h5>Discussion Board Feed</h5>
              <div className="feed-scroll">
                {comments.length === 0 ? <p className="empty">No log responses anchored.</p> : 
                  comments.map(c => (
                    <div key={c.id} className="comment-bubble">
                      <span className="user-stamp">User ID: #{c.user_id}</span>
                      <p>{c.comment}</p>
                    </div>
                  ))
                }
              </div>
            </div>

            <form className="drawer-input-row" onSubmit={postComment}>
              <input value={newComment} placeholder="Add progress log note..." onChange={e=>setNewComment(e.target.value)} required />
              <button type="submit">Publish</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
