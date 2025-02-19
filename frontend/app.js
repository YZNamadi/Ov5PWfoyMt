import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button, Typography } from '@mui/material';
import LoginModal from './LoginModal';
import NoteCard from './NoteCard';
import NoteForm from './NoteForm';

function App() {
  const [user, setUser] = useState(null);
  const [notes, setNotes] = useState([]);
  const [showLogin, setShowLogin] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingNote, setEditingNote] = useState(null);

  const handleLogin = async (email, password) => {
    try {
      const response = await axios.post('http://localhost:8000/auth/login', { email, password });
      setUser(response.data.access_token);
      fetchNotes();
    } catch (error) {
      alert('Invalid credentials');
    }
  };

  const fetchNotes = async () => {
    const response = await axios.get('http://localhost:8000/notes', {
      headers: { Authorization: `Bearer ${user}` },
    });
    setNotes(response.data);
  };

  const handleLogout = () => {
    setUser(null);
    setNotes([]);
  };

  const addNote = async (note) => {
    await axios.post('http://localhost:8000/notes', note, {
      headers: { Authorization: `Bearer ${user}` },
    });
    fetchNotes();
  };

  const updateNote = async (id, updatedNote) => {
    await axios.put(`http://localhost:8000/notes/${id}`, updatedNote, {
      headers: { Authorization: `Bearer ${user}` },
    });
    fetchNotes();
  };

  const deleteNote = async (id) => {
    await axios.delete(`http://localhost:8000/notes/${id}`, {
      headers: { Authorization: `Bearer ${user}` },
    });
    fetchNotes();
  };

  const togglePin = async (id) => {
    await axios.patch(`http://localhost:8000/notes/${id}/toggle-pin`, null, {
      headers: { Authorization: `Bearer ${user}` },
    });
    fetchNotes();
  };

  return (
    <div>
      <nav>
        {user ? (
          <Button onClick={handleLogout}>Logout</Button>
        ) : (
          <Button onClick={() => setShowLogin(true)}>Login</Button>
        )}
      </nav>
      <LoginModal open={showLogin} onClose={() => setShowLogin(false)} onLogin={handleLogin} />
      <Button
        onClick={() => setShowForm(true)}
        style={{ position: 'fixed', bottom: 20, right: 20 }}
      >
        +
      </Button>
      <NoteForm
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditingNote(null);
        }}
        onSubmit={(note) => {
          if (editingNote) {
            updateNote(editingNote.id, note);
          } else {
            addNote(note);
          }
        }}
        initialData={editingNote}
      />
      {notes.map((note) => (
        <NoteCard
          key={note.id}
          note={note}
          onEdit={(updatedNote) => {
            setEditingNote({ ...note, ...updatedNote });
            setShowForm(true);
          }}
          onDelete={() => deleteNote(note.id)}
          onTogglePin={() => togglePin(note.id)}
        />
      ))}
    </div>
  );
}

export default App;