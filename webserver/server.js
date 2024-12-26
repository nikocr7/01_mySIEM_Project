const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());

// Verbindung zur MongoDB herstellen
mongoose.connect('mongodb://127.0.0.1:27017/mySIEM')
.then(() => {
  logger('Datenbank verbunden');
})
.catch(err => {
  logger(`Datenbankverbindung fehlgeschlagen: ${err}`);
});

// Logger-Funktion
function logger(message) {
  const date = new Date();
  const timestamp = `${date.toISOString()} - `;
  const logMessage = `${timestamp}${message}\n`;

  // Hier verwenden wir das heutige Datum für die Logdatei
  const logFileName = `logs/server_${date.toISOString().split('T')[0]}.log`; // z.B. server_2024-12-26.log

  // Logdatei-Pfad generieren
  const logFilePath = path.join(__dirname, '..',  logFileName);

  // Logmessage in die Datei schreiben
  fs.appendFile(logFilePath, logMessage, (err) => {
    if (err) {
      console.error('Fehler beim Schreiben der Logdatei:', err);
    }
  });
}

// Log Schema definieren
const logSchema = new mongoose.Schema(
  {
    file: { type: String, required: true },
    timestamp: { type: String, required: true },  // Datumsformat als String, kann später in Date umgewandelt werden
    line: { type: String, required: true },
  },
  { versionKey: false } // VersionKey deaktivieren
);

const Log = mongoose.model('Log', logSchema);

// POST-Route zum Empfangen von Logs
app.post('/logs', async (req, res) => {
  try {
    const log = new Log(req.body);
    await log.save();
    logger(`Neuer Log-Eintrag hinzugefügt: ${JSON.stringify(log)}`);
    res.status(201).send(log);
  } catch (error) {
    logger(`Fehler beim Speichern des Logs: ${error}`);
    res.status(400).send(error);
  }
});

// Server starten
app.listen(PORT, '192.168.178.26', () => {
  logger(`Server läuft auf http://localhost:${PORT}`);
  console.log("Server läuft auf http://localhost:3000");
});