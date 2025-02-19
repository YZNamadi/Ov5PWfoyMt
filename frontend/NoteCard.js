import React from 'react';
import { Card, CardContent, CardActions, Button, Typography } from '@mui/material';

function NoteCard({ note, onEdit, onDelete, onTogglePin }) {
  return (
    <Card style={{ backgroundColor: note.is_pinned ? 'yellow' : 'white', marginBottom: 10 }}>
      <CardContent>
        <Typography variant="h6">{note.title}</Typography>
        <Typography>{note.content.substring(0, 100)}</Typography>
      </CardContent>
      <CardActions>
        <Button onClick={onEdit}>Edit</Button>
        <Button onClick={onDelete}>Delete</Button>
        <Button onClick={onTogglePin}>{note.is_pinned ? 'Unpin' : 'Pin'}</Button>
      </CardActions>
    </Card>
  );
}

export default NoteCard;

