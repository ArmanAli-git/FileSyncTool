let pathA = null;
let pathB = null;
let pathC = null;

function selectA() {
  pywebview.api.select_A().then(function (pathData) {
    if (pathData) {
      document.querySelector("#name-a").textContent = pathData[1];
      document.querySelector("#path-a").textContent = pathData[0];
      pathA = pathData[2];
      syncReady();
    }
  });
}

function selectB() {
  pywebview.api.select_B().then(function (pathData) {
    if (pathData) {
      document.querySelector("#name-b").textContent = pathData[1];
      document.querySelector("#path-b").textContent = pathData[0];
      pathB = pathData[2];
      syncReady();
    }
  });
}

let cloudToggleName = document.querySelector(".cloudtoggle-name");
let cloudToggleSlider = document.querySelector(".cloudtoggle-slider");
let cardC = document.querySelector("#card-c");

function authenticateDrive(checkbox) {
  if (checkbox.checked) {
    cardC.style.opacity = "0.6";
    cardC.style.pointerEvents = "none";
    cloudToggleSlider.style.opacity = "0.6";
    checkbox.disabled = true;

    pywebview.api
      .authenticate_ready()
      .then(function (result) {
        cardC.style.opacity = "";
        cardC.style.pointerEvents = "";
        cloudToggleSlider.style.opacity = "";
        checkbox.disabled = false;
        cloudToggleName.style.color = "hsl(142, 71%, 58%)";
      })
      .catch(function (error) {
        cardC.style.opacity = "";
        cardC.style.pointerEvents = "";
        checkbox.checked = false;
        checkbox.disabled = false;
        cloudToggleSlider.style.opacity = "";
        cloudToggleName.style.color = "hsl(0, 91%, 71%)";
      });
  } else {
    cloudToggleName.style.color = "hsl(240, 100%, 91%)";
    cardC.style.opacity = "";
    cardC.style.pointerEvents = "";
  }
}

let inputValue = document.querySelector(".newfolder-box").value.trim();

function createFolder() {
  if (inputValue !== "") {
    pywebview.api.create_folder(inputValue).then(function (folderId) {
      if (folderId) {
        document.querySelector(".newfolder-box").value = "";
        document.querySelector("#selectfolder-box").checked = false;
      }
    });
  }
}

let selectFolderBox = document.querySelector("#selectfolder-box");
let selectFolderOptions = document.querySelector(".selectfolder-options");

function loadingFoldersAnimation(show) {
  const loadingHTML = `
  <div class="loading-filler">
  <span>.</span>
  <span>.</span>
  <span>.</span>
  </div>`;

  let loadingFillerAnimation = document.querySelector(".loading-filler");

  if (show) {
    selectFolderOptions.insertAdjacentHTML("beforeend", loadingHTML);
  } else {
    if (loadingFillerAnimation) {
      document.querySelector(".loading-filler").remove();
    }
  }
}

selectFolderBox.disabled = false;

async function getFolder(checkbox) {
  if (checkbox.checked) {
    selectFolderBox.disabled = true;
    selectFolderOptions.innerHTML = "";

    loadingFoldersAnimation(true);

    let folders = await pywebview.api.scan_root();

    folders.forEach((folder) => {
      let option = document.createElement("ul");

      option.innerText = folder.name;
      option.dataset.id = folder.id;
      option.onclick = () => selectFolder(folder.name, folder.id);

      selectFolderOptions.appendChild(option);
    });

    loadingFoldersAnimation(false);

    if (selectFolderOptions.childElementCount === 0) {
      let emptyFiller = document.createElement("label");
      emptyFiller.textContent = "Empty";
      selectFolderOptions.appendChild(emptyFiller);
    }
    selectFolderBox.disabled = false;
  }
}

let selectFolderName = document.querySelector(".selectfolder-name");

function selectFolder(name, id) {
  pywebview.api.lock_target_folder(id).then(function () {
    selectFolderName.textContent = name;
    document.querySelector("#selectfolder-box").checked = false;
    pathC = id;
    syncReady();
  });
}

let syncBtn = document.querySelector(".sync-button");
let syncSts = document.querySelector(".sync-status");

function syncStatus(state) {
  if (state === "syncing") {
    syncBtn.disabled = true;
    syncBtn.classList.add("syncing");
    syncBtn.textContent = "Syncing ...";
    syncSts.textContent = "Sync in progress, please wait ...";
  } else if (state === "success") {
    syncBtn.disabled = false;
    syncBtn.classList.remove("syncing");
    syncBtn.textContent = "Synced!";
    syncSts.textContent = "All files are up to date.";
    syncSts.classList.add("done");
  } else if (state === "fail") {
    syncBtn.disabled = false;
    syncBtn.classList.remove("syncing");
    syncBtn.textContent = "Retry Sync";
    syncSts.classList.add("error");
    syncSts.textContent = "Sync failed. Please check your connection.";
  }
  syncSts.classList.remove("done");
  syncSts.classList.remove("error");
}

function syncReady() {
  if ((pathA && pathB) || (pathA && pathC)) {
    syncBtn.textContent = "Sync Now";
    syncSts.textContent = "Ready to sync.";
    syncBtn.disabled = false;
  } else if ((pathA || pathB) && (pathA || pathC)) {
    syncSts.textContent = "Waiting for second location ...";
  }
}

function sync() {
  syncStatus("syncing");
  let cloudBtn = document.querySelector("#cloudtoggle-box").checked;
  pywebview.api
    .sync(cloudBtn, pathC)
    .then(function () {
      syncStatus("success");
    })
    .catch(function (error) {
      syncStatus("fail");
    });
}

function updateProgress(work_done) {
  let progressBarLine = document.querySelector(".progressbar-line");
  progressBarLine.style.width = work_done + "%";
}

function progressBar(visibilty) {
  let progressBar = document.querySelector(".progressbar-container");
  let progressBarLine = document.querySelector(".progressbar-line");

  if (visibilty === "show") {
    progressBar.style.opacity = "100%";
    progressBarLine.style.opacity = "100%";
  } else if (visibilty === "hide") {
    progressBar.style.opacity = "0%";
    progressBarLine.style.opacity = "0%";

    setTimeout(function () {
      progressBarLine.style.width = "0%";
    }, 500);
  }
}
