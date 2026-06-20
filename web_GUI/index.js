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
  let apiCall =
    location === "a" ? pywebview.api.select_A() : pywebview.api.select_B();

  apiCall.then(function (pathData) {
    if (pathData) {
      document.querySelector(`#name-${location}`).textContent = pathData[1];
      document.querySelector(`#path-${location}`).textContent = pathData[0];
      if (location === "a") pathA = pathData[2];
      if (location === "b") pathB = pathData[2];
      syncReady();
    }
  });
}

function authenticateDrive(checkbox) {
  if (checkbox.checked) {
    checkbox.disabled = true;
    cardC.classList.add("disabled");

    pywebview.api
      .authenticate_ready()
      .then(function (result) {
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
    pywebview.api.create_folder(newfolderBoxValue).then(function (folderId) {
      if (folderId) {
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
  } else {
    selectFolderOptions.innerHTML = "";
    emptyFolder.classList.remove("show");
  }
}

function selectFolder(name, id) {
  pywebview.api.lock_target_folder(id).then(function () {
    selectFolderName.textContent = name;
    document.querySelector("#selectfolder-box").checked = false;
    pathC = id;
    syncReady();
  });
}

function syncState(state) {
  if (state === "syncing") {
    main.classList.add("syncing");
    syncBtn.classList.add("fade");
    syncBtn.classList.add("syncing");

    setTimeout(() => {
      syncBtn.innerHTML = "<span>•</span><span>•</span><span>•</span>";
      syncBtn.classList.remove("fade");
    }, 200);

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
    syncSts.textContent = "Sync failed. Please check your connection.";
  }

  if (state === "syncing") {
    syncSts.classList.remove("done");
    syncSts.classList.remove("error");
  }
}

function syncReady() {
  if ((pathA && pathB) || (pathA && pathC)) {
    syncSts.textContent = "Ready to sync.";
    syncBtn.disabled = false;
  } else if (pathA || pathB || pathC) {
    syncSts.textContent = "Waiting for second location ...";
  }
}

function sync() {
  syncState("syncing");
  let cloudToggleCheck = document.querySelector("#cloudtoggle-box").checked;
  pywebview.api
    .sync(cloudToggleCheck, pathC)
    .then(function () {
      syncState("success");
    })
    .catch(function (error) {
      syncState("fail");
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
