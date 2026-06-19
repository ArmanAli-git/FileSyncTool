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
    cardC.classList.add("disabled-state");
    cloudToggleSlider.classList.add("disabled-state");
    checkbox.disabled = true;

    pywebview.api
      .authenticate_ready()
      .then(function (result) {
        cardC.classList.remove("disabled-state");
        cloudToggleSlider.classList.remove("disabled-state");
        checkbox.disabled = false;
        cloudToggleName.style.color = "hsl(142, 71%, 58%)";
      })
      .catch(function (error) {
        cardC.classList.remove("disabled-state");
        checkbox.checked = false;
        checkbox.disabled = false;
        cloudToggleSlider.classList.remove("disabled-state");
        cloudToggleName.style.color = "hsl(0, 91%, 71%)";
      });
  } else {
    cloudToggleName.style.color = "hsl(240, 100%, 91%)";
    cardC.classList.remove("disabled-state");
  }
}

function createFolder() {
  let inputValue = document.querySelector(".newfolder-box").value.trim();
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

let selectFolderPicker = document.querySelector(".selectfolder-picker");
selectFolderBox.disabled = false;

async function getFolder(checkbox) {
  if (checkbox.checked) {
    selectFolderBox.disabled = true;
    selectFolderPicker.classList.add("active");
    selectFolderOptions.innerHTML = "";

    loadingFoldersAnimation(true);

    let folders = await pywebview.api.scan_root();

    folders.forEach((folder) => {
      let option = document.createElement("li");

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
  } else {
    selectFolderPicker.classList.remove("active");
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
let cloudToggleBox = document.querySelector("#cloudtoggle-box");
let allCardButton = document.querySelectorAll(".card-button");
let cloudToggleContainer = document.querySelector(".cloudtoggle-container");

function syncState(state) {
  if (state === "syncing") {
    syncBtn.disabled = true;
    cloudToggleBox.disabled = true;
    cloudToggleContainer.classList.add("disabled-state");
    if (cloudToggleBox.checked) {
      document.querySelector("#card-a").classList.add("disabled-state");
      document.querySelector("#card-c").classList.add("disabled-state");
    } else {
      document.querySelector("#card-a").classList.add("disabled-state");
      document.querySelector("#card-b").classList.add("disabled-state");
    }

    syncBtn.classList.add("syncing");
    syncBtn.textContent = "Syncing ...";
    syncSts.textContent = "Sync in progress, please wait ...";
  } else if (state === "success") {
    syncBtn.disabled = false;
    cloudToggleBox.disabled = false;
    cloudToggleContainer.classList.remove("disabled-state");
    allCardButton.forEach((card) => card.classList.remove("disabled-state"));

    syncBtn.classList.remove("syncing");
    syncBtn.textContent = "Synced!";
    setTimeout(() => {
      syncBtn.textContent = "Synced";
    }, 1000);
    setTimeout(() => {
      syncBtn.textContent = "Synce";
    }, 2000);
    setTimeout(() => {
      syncBtn.textContent = "Sync";
    }, 3000);
    syncSts.textContent = "All files are up to date.";
    syncSts.classList.add("done");
  } else if (state === "fail") {
    syncBtn.disabled = false;
    cloudToggleBox.disabled = false;
    cloudToggleContainer.classList.remove("disabled-state");
    allCardButton.forEach((card) => card.classList.remove("disabled-state"));

    syncBtn.classList.remove("syncing");
    syncBtn.textContent = "Retry Sync";
    syncSts.classList.add("error");
    syncSts.textContent = "Sync failed. Please check your connection.";
  }

  if (state !== "success") syncSts.classList.remove("done");
  if (state !== "fail") syncSts.classList.remove("error");
}

function syncReady() {
  if ((pathA && pathB) || (pathA && pathC)) {
    syncBtn.textContent = "Sync Now";
    syncSts.textContent = "Ready to sync.";
    syncBtn.disabled = false;
  } else if (pathA || pathB || pathC) {
    syncSts.textContent = "Waiting for second location ...";
  }
}

function sync() {
  syncState("syncing");
  let cloudBtnCheck = document.querySelector("#cloudtoggle-box").checked;
  pywebview.api
    .sync(cloudBtnCheck, pathC)
    .then(function () {
      syncState("success");
    })
    .catch(function (error) {
      syncState("fail");
    });
}

function updateProgress(work_done) {
  let progressBarLine = document.querySelector(".progressbar-lines");
  progressBarLine.style.width = work_done + "%";
}

function progressBar(visibilty) {
  let progressBar = document.querySelector(".progressbar-container");
  let progressBarLine = document.querySelector(".progressbar-line");

  if (visibilty === "show") {
    progressBar.style.opacity = "100%";
  } else if (visibilty === "hide") {
    setTimeout(function () {
      progressBar.style.opacity = "0%";
      progressBarLine.style.width = "0%";
    }, 300);
  }
}
