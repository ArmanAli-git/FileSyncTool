let pathA = null;
let pathB = null;
let pathC = null;

let main = document.querySelector("main");
let cardC = document.querySelector("#card-c");
let cloudToggleName = document.querySelector(".cloudtoggle-name");
let selectFolderBox = document.querySelector("#selectfolder-box");
let selectFolderName = document.querySelector(".selectfolder-name");
let selectFolderOptions = document.querySelector(".selectfolder-options");
let loadingFolder = document.querySelector(".loading-folder");
let selectFolderList = document.querySelector(".selectfolder-list");
let emptyFolder = document.querySelector(".empty-folder");
let syncBtn = document.querySelector(".sync-button");
let syncSts = document.querySelector(".sync-status");
let progressBarContainer = document.querySelector(".progressbar-container");
let progressBarLines = document.querySelector(".progressbar-lines");

const sensitivity = 0.15;

function selectLocations(location) {
  pywebview.api.get_locations(location).then(function (locData) {
    if (locData) {
      document.querySelector(`#name-${location}`).textContent = locData[1];
      document.querySelector(`#path-${location}`).textContent = locData[0];
      if (location === "a") {
        pathA = locData[2];
        document.querySelector("#drop-path-a").classList.add("show");
      }
      if (location === "b") {
        pathB = locData[2];
        document.querySelector("#drop-path-b").classList.add("show");
      }
      syncReady();
    }
  });
}

function dropEffectAnimation(location, callback) {
  let card = document.querySelector(`#card-${location}`);
  card.classList.add("drop-effect");
  setTimeout(() => {
    callback();
    card.classList.remove("drop-effect");
  }, 300);
}

function dropLocations(location) {
  pywebview.api.drop_locations(location).then(function () {
    dropEffectAnimation(location, () => {
      if (location !== "c") {
        document.querySelector(`#name-${location}`).textContent =
          `Location ${location.toUpperCase()}`;
        document.querySelector(`#path-${location}`).textContent =
          "Click to browse";
      }

      if (location === "a") {
        pathA = null;
        document.querySelector("#drop-path-a").classList.remove("show");
      } else if (location === "b") {
        pathB = null;
        document.querySelector("#drop-path-b").classList.remove("show");
      } else if (location === "c") {
        pathC = null;
        selectFolderName.textContent = "Choose a folder";
        document.querySelector("#drop-path-c").classList.remove("show");
      }
      syncReady();
    });
  });
}

function authenticateDrive(checkbox) {
  if (checkbox.checked) {
    checkbox.disabled = true;
    cardC.classList.add("disabled");

    pywebview.api
      .authenticate()
      .then(function () {
        checkbox.disabled = false;
        cardC.classList.remove("disabled");
        cloudToggleName.style.color = "hsla(142, 71%, 58%, 0.7)";
      })
      .catch(function (error) {
        checkbox.checked = false;
        checkbox.disabled = false;
        cardC.classList.remove("disabled");
        cloudToggleName.style.color = "hsla(0, 91%, 71%, 0.7)";
      });
  } else {
    cloudToggleName.style.color = "hsl(240, 100%, 91%)";
  }
}

function createFolder() {
  let newfolderBoxValue = document.querySelector(".newfolder-box").value.trim();
  if (newfolderBoxValue !== "") {
    pywebview.api.create_folder(newfolderBoxValue).then(function (id) {
      if (id) {
        document.querySelector(".newfolder-box").value = "";
        document.querySelector("#selectfolder-box").checked = false;
      }
    });
  }
}

function loadingFolderAnimation(folder, rate) {
  folder.animate(
    [
      { transform: "translateY(1rem)", opacity: 0 },
      { transform: "translateY(0)", opacity: 1 },
    ],
    {
      duration: 300,
      fill: "forwards",
      easing: "cubic-bezier(0.175, 0.885, 0.32, 1.27)",
      delay: rate * 40,
    },
  );
}

async function getFolder(checkbox) {
  if (checkbox.checked) {
    selectFolderBox.disabled = true;
    selectFolderOptions.innerHTML = "";
    emptyFolder.classList.remove("show");
    loadingFolder.classList.add("show");

    let folders = await pywebview.api.scan_root();
    let folderCount = 0;

    folders.forEach((folder) => {
      let option = document.createElement("li");
      folderCount++;

      option.innerText = folder.name;
      option.dataset.id = folder.id;
      option.onclick = () => selectFolder(folder.name, folder.id);

      loadingFolderAnimation(option, folderCount);

      selectFolderOptions.appendChild(option);
    });

    selectFolderBox.disabled = false;
    loadingFolder.classList.remove("show");

    if (selectFolderOptions.childElementCount === 0) {
      emptyFolder.classList.add("show");
    }
  }
}

function selectFolder(name, id) {
  pywebview.api.select_folder(id).then(function () {
    selectFolderName.textContent = name;
    document.querySelector("#selectfolder-box").checked = false;
    pathC = id;
    document.querySelector("#drop-path-c").classList.add("show");
    syncReady();
  });
}

function syncState(state, message = null) {
  if (state === "syncing") {
    main.classList.add("syncing");
    syncBtn.classList.add("fade");
    syncBtn.classList.add("syncing");

    setTimeout(() => {
      syncBtn.innerHTML = "<span>•</span><span>•</span><span>•</span>";
      syncBtn.classList.remove("fade");
    }, 200);

    syncSts.classList.remove("done");
    syncSts.classList.remove("error");
    syncSts.textContent = "Sync in progress, please wait ...";
  } else if (state === "success") {
    main.classList.remove("syncing");
    syncBtn.classList.add("fade");

    setTimeout(() => {
      syncBtn.classList.remove("syncing");
      syncBtn.textContent = "Synced!";
      syncBtn.classList.remove("fade");
    }, 200);

    setTimeout(() => {
      syncBtn.classList.add("fade");
      setTimeout(() => {
        syncBtn.textContent = "Sync";
        syncBtn.classList.remove("fade");
      }, 200);
    }, 3000);

    syncSts.classList.add("done");
    syncSts.textContent = "All files are up to date.";
  } else if (state === "fail") {
    main.classList.remove("syncing");
    syncBtn.classList.add("fade");
    syncBtn.classList.remove("syncing");

    setTimeout(() => {
      syncBtn.textContent = "Retry Sync";
      syncBtn.classList.remove("fade");
    }, 200);

    syncSts.classList.add("error");
    syncSts.textContent =
      message || "Sync failed. Please check your connection.";
  }
}

function syncReady() {
  syncSts.classList.remove("done");
  syncSts.classList.remove("error");
  if ((pathA && pathB) || (pathA && pathC)) {
    syncSts.textContent = "Ready to sync.";
    syncBtn.disabled = false;
  } else if ([pathA, pathB, pathC].filter(Boolean).length === 1) {
    syncSts.textContent = "Waiting for second location ...";
    syncBtn.disabled = true;
  } else {
    syncBtn.disabled = true;
    syncSts.textContent = "Please select locations to begin.";
  }
}

function sync() {
  syncState("syncing");
  let cloudToggleCheck = document.querySelector("#cloudtoggle-box").checked;
  pywebview.api
    .synchronize_files(cloudToggleCheck)
    .then(function (result) {
      if (result && result.ok === false) {
        let msg = result.error || "Unknown error";
        if (result.detail) msg += ": " + result.detail;
        syncState(
          "fail",
          result.error || "An unknown error occurred. Please try again.",
        );
        console.error("[Sync Error]", result);
      } else {
        syncState("success");
      }
    })
    .catch(function (error) {
      syncState("fail", "Unexpected error: " + (error.message || error));
      console.error("[Sync Exception]", error);
    });
}

function updateProgressBar(work_done) {
  progressBarLines.style.width = work_done + "%";
}

function progressBar(visibilty) {
  if (visibilty === "show") {
    progressBarContainer.style.opacity = "100%";
  } else if (visibilty === "hide") {
    setTimeout(function () {
      progressBarContainer.style.opacity = "0%";
      progressBarLines.style.width = "0%";
    }, 300);
  }
}

selectFolderList.addEventListener(
  "wheel",
  (e) => {
    e.preventDefault();
    selectFolderList.scrollTop += e.deltaY * sensitivity;
  },
  { passive: false },
);

function showExitConfirm() {
  document.getElementById("exit-modal").classList.add("show");
}

function cancelExit() {
  document.getElementById("exit-modal").classList.remove("show");
}

function confirmExit() {
  document.getElementById("exit-modal").classList.remove("show");
  pywebview.api.force_quit();
}
