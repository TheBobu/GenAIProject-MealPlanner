import { useState, useEffect } from 'react';
import { Send, Loader, CheckCircle, AlertCircle, User, Plus, History, ArrowLeft } from 'lucide-react';

const API_BASE_URL = import.meta.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
export default function MealPlannerApp() {
  const [activeTab, setActiveTab] = useState('profile');
  const [userPrompt, setUserPrompt] = useState('');
  const [loadingTaskId, setLoadingTaskId] = useState(null);
  const [taskResults, setTaskResults] = useState({});
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [selectedUserHistory, setSelectedUserHistory] = useState(null);
  const [userTasks, setUserTasks] = useState([]);

  const [profileForm, setProfileForm] = useState({
    username: '',
    dietary_preferences: '',
    allergies: '',
    age: '',
    height: '',
    weight: '',
    gender: '',
    activity_level: 'Light',
    nutritional_goals: '',
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const renderMarkdown = (markdown) => {
    if (!markdown) return null;
    
    let html = markdown
      .replace(/^### (.*?)$/gm, '<h3 style="font-size: 1.125rem; font-weight: bold; margin-top: 1rem; margin-bottom: 0.5rem;">$1</h3>')
      .replace(/^## (.*?)$/gm, '<h2 style="font-size: 1.25rem; font-weight: bold; margin-top: 1.5rem; margin-bottom: 0.75rem;">$1</h2>')
      .replace(/^# (.*?)$/gm, '<h1 style="font-size: 1.875rem; font-weight: bold; margin-top: 2rem; margin-bottom: 1rem;">$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight: bold;">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em style="font-style: italic;">$1</em>')
      .replace(/^- (.*?)$/gm, '<li style="margin-left: 1.5rem; margin-bottom: 0.25rem;">$1</li>')
      .replace(/(<li[^>]*>.*?<\/li>)/s, '<ul style="list-style: disc;">$1</ul>')
      .replace(/\n\n/g, '</p><p style="margin-bottom: 1rem;">')
      .replace(/\n/g, '<br/>');

    return <div dangerouslySetInnerHTML={{ __html: html }} />;
  };

  const fetchUsers = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/users`);
      const data = await res.json();
      setUsers(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to fetch users:', err);
    }
  };

  const fetchUserTasks = async (username) => {
    try {
      const res = await fetch(`${API_BASE_URL}/status/${username}`);
      const data = await res.json();
      setUserTasks(data.tasks ? data.tasks.filter(t => t.status === 'completed') : []);
      setSelectedUserHistory(username);
    } catch (err) {
      console.error('Failed to fetch user tasks:', err);
      setUserTasks([]);
    }
  };

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!profileForm.username.trim()) {
      setError('Username is required');
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/users/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileForm),
      });

      if (res.ok) {
        setSuccess(`Profile for ${profileForm.username} saved successfully!`);
        setProfileForm({
          username: '',
          dietary_preferences: '',
          allergies: '',
          age: '',
          height: '',
          weight: '',
          gender: '',
          activity_level: 'Light',
          nutritional_goals: '',
        });
        fetchUsers();
      } else {
        setError('Failed to save profile');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    }
  };

  const handleGeneratePlan = async (e) => {
    e.preventDefault();
    setError('');

    if (!selectedUser) {
      setError('Please select a user');
      return;
    }

    if (!userPrompt.trim()) {
      setError('Please enter a request');
      return;
    }

    try {
      const res = await fetch(
        `${API_BASE_URL}/generate-plan?username=${selectedUser}&prompt=${encodeURIComponent(userPrompt)}`,
        { method: 'POST' }
      );

      if (res.ok) {
        const data = await res.json();
        const taskId = data.task_id;
        setLoadingTaskId(taskId);
        setUserPrompt('');

        const pollInterval = setInterval(async () => {
          try {
            const statusRes = await fetch(`${API_BASE_URL}/status/${selectedUser}`);
            const statusData = await statusRes.json();

            if (statusData.tasks) {
              const task = statusData.tasks.find(t => t.task_id === taskId);
              if (task && task.status !== 'pending') {
                setTaskResults(prev => ({
                  ...prev,
                  [taskId]: task,
                }));
                setLoadingTaskId(null);
                clearInterval(pollInterval);
              }
            }
          } catch (err) {
            console.error('Polling error:', err);
          }
        }, 2000);

        setTimeout(() => clearInterval(pollInterval), 300000);
      } else {
        setError('Failed to generate meal plan');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">🍽️ Meal Planner AI</h1>
          <p className="text-gray-600">Generate personalized meal plans with nutritional analysis</p>
        </div>

        <div className="flex gap-4 mb-6 flex-wrap">
          <button
            onClick={() => setActiveTab('profile')}
            className={`px-6 py-2 rounded-lg font-medium transition flex items-center gap-2 ${
              activeTab === 'profile'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <User size={20} /> Create Profile
          </button>
          <button
            onClick={() => setActiveTab('generate')}
            className={`px-6 py-2 rounded-lg font-medium transition flex items-center gap-2 ${
              activeTab === 'generate'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Plus size={20} /> Generate Plan
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-6 py-2 rounded-lg font-medium transition flex items-center gap-2 ${
              activeTab === 'history'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <History size={20} /> User History
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-red-800">{error}</p>
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
            <CheckCircle className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-green-800">{success}</p>
          </div>
        )}

        {activeTab === 'profile' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-6">Create User Profile</h2>
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Username"
                  value={profileForm.username}
                  onChange={(e) => setProfileForm({...profileForm, username: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <textarea
                  placeholder="Dietary preferences (e.g., vegetarian, low-carb)"
                  value={profileForm.dietary_preferences}
                  onChange={(e) => setProfileForm({...profileForm, dietary_preferences: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows="2"
                />
                <textarea
                  placeholder="Allergies (e.g., peanuts, shellfish)"
                  value={profileForm.allergies}
                  onChange={(e) => setProfileForm({...profileForm, allergies: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows="2"
                />
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="number"
                    placeholder="Age"
                    value={profileForm.age}
                    onChange={(e) => setProfileForm({...profileForm, age: e.target.value})}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <input
                    type="text"
                    placeholder="Height (cm)"
                    value={profileForm.height}
                    onChange={(e) => setProfileForm({...profileForm, height: e.target.value})}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Weight (kg)"
                    value={profileForm.weight}
                    onChange={(e) => setProfileForm({...profileForm, weight: e.target.value})}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <select
                    value={profileForm.gender}
                    onChange={(e) => setProfileForm({...profileForm, gender: e.target.value})}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>
                <select
                  value={profileForm.activity_level}
                  onChange={(e) => setProfileForm({...profileForm, activity_level: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="Light">Light (Sedentary)</option>
                  <option value="Moderate">Moderate</option>
                  <option value="Active">Active</option>
                  <option value="VeryActive">Very Active</option>
                </select>
                <textarea
                  placeholder="Nutritional goals (e.g., lose weight, gain muscle)"
                  value={profileForm.nutritional_goals}
                  onChange={(e) => setProfileForm({...profileForm, nutritional_goals: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows="2"
                />
                <button
                  onClick={handleSaveProfile}
                  className="w-full bg-indigo-600 text-white py-2 rounded-lg font-medium hover:bg-indigo-700 transition"
                >
                  Save Profile
                </button>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-6">Saved Users</h2>
              {users.length > 0 ? (
                <div className="space-y-3">
                  {users.map(user => (
                    <div key={user.username} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <p className="font-bold text-gray-900">{user.username}</p>
                      <p className="text-sm text-gray-600">Age: {user.age || 'N/A'} | Height: {user.height || 'N/A'} cm | Weight: {user.weight || 'N/A'} kg</p>
                      <p className="text-sm text-gray-600">Preferences: {user.dietary_preferences || 'None'}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">No users created yet</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'generate' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-6">Generate Meal Plan</h2>
              <div className="space-y-4">
                <select
                  value={selectedUser}
                  onChange={(e) => setSelectedUser(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Select a user</option>
                  {users.map(user => (
                    <option key={user.username} value={user.username}>
                      {user.username}
                    </option>
                  ))}
                </select>
                <textarea
                  placeholder="What kind of meal plan would you like? (e.g., 'High protein, 3 meals per day, under 30 min prep')"
                  value={userPrompt}
                  onChange={(e) => setUserPrompt(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows="4"
                />
                <button
                  onClick={handleGeneratePlan}
                  disabled={loadingTaskId !== null}
                  className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loadingTaskId ? (
                    <>
                      <Loader size={20} className="animate-spin" /> Generating...
                    </>
                  ) : (
                    <>
                      <Send size={20} /> Generate Plan
                    </>
                  )}
                </button>
              </div>
            </div>

            {Object.entries(taskResults).map(([taskId, task]) => (
              <div key={taskId} className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center gap-2 mb-4">
                  {task.status === 'completed' && (
                    <CheckCircle className="text-green-600" size={24} />
                  )}
                  {task.status === 'failed' && (
                    <AlertCircle className="text-red-600" size={24} />
                  )}
                  <h3 className="text-xl font-bold capitalize">
                    {task.status === 'completed' ? 'Meal Plan Generated' : `Status: ${task.status}`}
                  </h3>
                </div>

                {task.status === 'completed' && task.result && (
                  <div className="bg-gray-50 p-4 rounded-lg text-gray-800 whitespace-pre-wrap text-sm leading-relaxed max-h-96 overflow-y-auto">
                    {task.result}
                  </div>
                )}

                {task.status === 'failed' && task.error && (
                  <p className="text-red-600 bg-red-50 p-4 rounded-lg">{task.error}</p>
                )}
              </div>
            ))}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="space-y-6">
            {!selectedUserHistory ? (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-6">Select User to View History</h2>
                {users.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {users.map(user => (
                      <button
                        key={user.username}
                        onClick={() => fetchUserTasks(user.username)}
                        className="p-4 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg border border-indigo-200 hover:border-indigo-500 hover:shadow-md transition text-left"
                      >
                        <p className="font-bold text-gray-900 mb-2">{user.username}</p>
                        <p className="text-sm text-gray-600">Age: {user.age || 'N/A'}</p>
                        <p className="text-sm text-gray-600">Height: {user.height || 'N/A'} cm</p>
                        <p className="text-sm text-gray-600">Weight: {user.weight || 'N/A'} kg</p>
                      </button>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600">No users found</p>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <button
                  onClick={() => {
                    setSelectedUserHistory(null);
                    setUserTasks([]);
                  }}
                  className="flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium mb-4"
                >
                  <ArrowLeft size={20} /> Back to Users
                </button>

                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h2 className="text-2xl font-bold mb-6">
                    Completed Tasks for <span className="text-indigo-600">{selectedUserHistory}</span>
                  </h2>

                  {userTasks.length > 0 ? (
                    <div className="space-y-4">
                      {userTasks.map(task => (
                        <div key={task.task_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                              <CheckCircle className="text-green-600" size={24} />
                              <div>
                                <p className="font-bold text-gray-900">Meal Plan Generated</p>
                                <p className="text-sm text-gray-600">
                                  {task.created_at ? new Date(task.created_at).toString() : 'N/A'}
                                </p>
                              </div>
                            </div>
                            <p className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                              {task.task_id}...
                            </p>
                          </div>

                          {task.result && (
                            <div className="bg-gray-50 p-4 rounded-lg text-gray-800 text-sm leading-relaxed max-h-64 overflow-y-auto">
                              {renderMarkdown(task.result)}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-600 text-center py-8">No completed tasks for this user</p>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}