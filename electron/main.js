const { app, BrowserWindow, dialog, shell } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const fs = require("fs");
const http = require("http");

let mainWindow;
let backendProcess;

// Détection du mode développement vs production
const isDev = !app.isPackaged;

// En production, les ressources sont dans process.resourcesPath
// En dev, elles sont relatives à __dirname
const resourcesPath = isDev ? path.join(__dirname, "..") : process.resourcesPath;

function startBackend() {
  // En développement : backend/dist/PharmaBackend.exe
  // En production : resources/backend/PharmaBackend.exe
  const backendPath = isDev 
    ? path.join(resourcesPath, "backend", "dist", "PharmaBackend.exe")
    : path.join(resourcesPath, "backend", "PharmaBackend.exe");

  console.log("🚀 Démarrage du backend :", backendPath);
  console.log("📍 Mode :", isDev ? "DÉVELOPPEMENT" : "PRODUCTION");
  console.log("📂 Resources Path:", resourcesPath);

  // VÉRIFICATION CRITIQUE : Le fichier existe-t-il ?
  if (!fs.existsSync(backendPath)) {
    console.error("❌ ERREUR FATALE : Backend introuvable !");
    console.error("   Chemin recherché :", backendPath);
    console.error("   Le fichier n'existe pas.");
    
    // Afficher un message à l'utilisateur
    dialog.showErrorBox(
      'Erreur de démarrage',
      `Le serveur backend est introuvable.\n\nChemin: ${backendPath}\n\nVeuillez réinstaller l'application.`
    );
    app.quit();
    return;
  }

  console.log("✅ Backend trouvé, lancement en cours...");

  // Le backend doit tourner depuis le dossier où il est (backend/dist)
  // pour trouver la DB qui est copiée là
  const backendCwd = isDev 
    ? path.join(resourcesPath, "backend", "dist")
    : path.join(resourcesPath, "backend");

  console.log("📂 Backend CWD:", backendCwd);

  // Créer un fichier de log pour le backend
  const logPath = path.join(resourcesPath, "backend_log.txt");
  const logStream = fs.createWriteStream(logPath, { flags: 'w' });
  
  console.log(`📝 Logs du backend seront dans: ${logPath}`);

  const startTime = Date.now();
  console.log(`⏰ Lancement du backend à ${new Date().toISOString()}`);

  backendProcess = spawn(backendPath, [], {
    cwd: backendCwd,
    shell: true, // Essayer avec shell pour debug
    stdio: ['ignore', 'pipe', 'pipe'],
    env: {
      ...process.env,
      PHARMA_ELECTRON_MODE: "true"
    }
  });

  console.log(`🔢 PID du backend: ${backendProcess.pid}`);

  // Capturer et afficher stdout
  if (backendProcess.stdout) {
    backendProcess.stdout.on('data', (data) => {
      const msg = data.toString();
      console.log(`[BACKEND] ${msg}`);
      if (logStream && !logStream.closed) {
        logStream.write(`[STDOUT] ${msg}\n`);
      }
    });
  } else {
    console.error("❌ Pas de stdout disponible !");
  }

  // Capturer et afficher stderr
  if (backendProcess.stderr) {
    backendProcess.stderr.on('data', (data) => {
      const msg = data.toString();
      console.error(`[BACKEND ERROR] ${msg}`);
      if (logStream && !logStream.closed) {
        logStream.write(`[STDERR] ${msg}\n`);
      }
    });
  } else {
    console.error("❌ Pas de stderr disponible !");
  }

  backendProcess.on("error", (err) => {
    const elapsed = Date.now() - startTime;
    console.error(`❌ Erreur backend après ${elapsed}ms:`, err);
    if (logStream && !logStream.closed) {
      logStream.write(`[ERROR after ${elapsed}ms] ${err.message}\n`);
    }
    dialog.showErrorBox(
      'Erreur de démarrage',
      `Erreur lors du démarrage du serveur backend:\n\n${err.message}`
    );
  });

  backendProcess.on("exit", (code, signal) => {
    const elapsed = Date.now() - startTime;
    console.log(`🛑 Backend arrêté après ${elapsed}ms (code=${code}, signal=${signal})`);
    
    if (logStream && !logStream.closed) {
      logStream.write(`[EXIT after ${elapsed}ms] code=${code}, signal=${signal}\n`);
      logStream.end();
    }
    
    if (code !== 0 && code !== null) {
      console.error(`❌ Le backend s'est arrêté avec une erreur (code ${code})`);
    }
  });

  backendProcess.on("spawn", () => {
    const elapsed = Date.now() - startTime;
    console.log(`✅ Backend process spawned après ${elapsed}ms`);
    if (logStream && !logStream.closed) {
      logStream.write(`[SPAWN after ${elapsed}ms]\n`);
    }
  });

  backendProcess.on("close", (code) => {
    const elapsed = Date.now() - startTime;
    console.log(`🔒 Backend process closed après ${elapsed}ms (code=${code})`);
    if (logStream && !logStream.closed) {
      logStream.write(`[CLOSE after ${elapsed}ms] code=${code}\n`);
      logStream.end();
    }
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // GESTION DES TÉLÉCHARGEMENTS
  mainWindow.webContents.session.on('will-download', (event, item, webContents) => {
    // Définir le chemin de sauvegarde (ou laisser l'utilisateur choisir via savePath si on ne le set pas, 
    // mais item.setSavePath(path) force le chemin. 
    // Pour afficher "Enregistrer sous", on laisse Electron gérer par défaut, 
    // OU on peut explicitement demander :
    item.setSaveDialogOptions({ title: 'Enregistrer le rapport' });

    item.once('done', (event, state) => {
      if (state === 'completed') {
        const filePath = item.getSavePath();
        const fileName = path.basename(filePath);
        
        // Notification de succès
        dialog.showMessageBox(mainWindow, {
          type: 'info',
          title: 'Téléchargement terminé',
          message: `Le fichier "${fileName}" a été téléchargé avec succès.`,
          buttons: ['Ouvrir le dossier', 'OK']
        }).then(({ response }) => {
          if (response === 0) { // Premier bouton : "Ouvrir le dossier"
            shell.showItemInFolder(filePath);
          }
        });
      } else {
        dialog.showErrorBox(
          'Échec du téléchargement', 
          `Le téléchargement a échoué ou a été annulé: ${state}`
        );
      }
    });
  });

  // CHARGEMENT DU FRONTEND VIA HTTP (résout les problèmes de routing)
  console.log("📦 Chargement UI: http://localhost:8000");
  mainWindow.loadURL("http://localhost:8000");

  // DevTools facultatif
  mainWindow.webContents.openDevTools();
}

// Fonction pour attendre que le backend soit prêt
async function waitForBackend(maxRetries = 15) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await new Promise((resolve, reject) => {
        console.log(`🔍 Vérification de la disponibilité du backend (tentative ${i + 1}/${maxRetries})...`);
        const req = http.get('http://localhost:8000/health', (res) => {
          if (res.statusCode === 200) {
            console.log("✅ Backend prêt !");
            resolve();
          } else {
            reject(new Error(`Status code: ${res.statusCode}`));
          }
        });
        req.on('error', reject);
        req.setTimeout(1000, () => reject(new Error('Timeout')));
      });
      return true;
    } catch (e) {
      console.log(`⏳ Attente du backend (tentative ${i + 1}/${maxRetries})...`);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  return false;
}

app.whenReady().then(async () => {
  startBackend();

  // Attendre que le backend soit VRAIMENT prêt
  console.log("⏳ Vérification de la disponibilité du backend...");
  const isReady = await waitForBackend();
  
  if (!isReady) {
    console.error("❌ Le backend ne répond pas après 15 secondes");
    dialog.showErrorBox(
      'Erreur de démarrage',
      'Le serveur backend ne répond pas.\n\nVeuillez vérifier que le port 8000 est disponible et réessayer.'
    );
    app.quit();
    return;
  }

  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("before-quit", () => {
  if (backendProcess) {
    console.log("🧹 Arrêt du backend...");
    backendProcess.kill();
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
