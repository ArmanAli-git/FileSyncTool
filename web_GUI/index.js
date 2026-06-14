function selectA() {
    pywebview.api.select_A().then(function(path) {
        if (path) {
            document.querySelector("#path-a").textContent = path;
        }
    });
}


function selectB() {
    pywebview.api.select_B().then(function(path) {
        if (path) {
            document.querySelector("#path-b").textContent = path;
        }
    });
}


function syncStatus(syncStatus) {
    let btn = document.querySelector(".sync-button");
    let status = document.querySelector(".sync-status");
    
    if (syncStatus === "syncing") {
        btn.classList.add("syncing");
        btn.disabled = true;
        status.className = "sync-status";
        status.textContent = "Syncing...";
    } else if (syncStatus === "sync success") {
        btn.classList.remove("syncing");
        btn.disabled = false;
        status.textContent = "Synced!";
        status.classList.add("done");
    } else if (syncStatus === "sync fail") {
        btn.classList.remove("syncing");
        btn.disabled = false;
        status.textContent = "Sync failed!";
        status.classList.add("error");
    }
}


function sync() {
    syncStatus("syncing");

    pywebview.api.sync().then(function() {
        syncStatus("sync success");
    }).catch(function(error) {
        syncStatus("sync fail");
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

        setTimeout(function() {
            progressBarLine.style.width = "0%";
        }, 500);
    }
}


function authenticateDrive(checkbox) {
    pywebview.api.authenticate_ready().then(function(result) {
        if (checkbox.checked) {
            let toggleName = document.querySelector(".cloudtoggle-name")
            toggleName.style.color = "hsl(142, 71%, 58%)";
        } else {
            toggleName.style.color = "hsl(240, 100%, 91%)";
        }
    })
}


function createFolder() {
    let inputValue = document.querySelector(".newfolder-box").value;
    pywebview.api.create_folder(inputValue).then(function(folderId) {
        if (folderId) {
            document.querySelector(".newfolder-box").value = "";
            document.querySelector("#selectfolder-box").checked = false;
        }
    });
}


function loadingFoldersAnimation(visibilty) {
    const loadingSet = `
    <div class="loading-filler">
    <span>.</span>
    <span>.</span>
    <span>.</span>
    </div>`;
    
    if (visibilty === "show") {
        let optionContainer = document.querySelector(".selectfolder-options");
        optionContainer.insertAdjacentHTML('beforeend', loadingSet)
    } else if (visibilty === "hide") {
        let loadingFolderAnimation = document.querySelector(".loading-filler");
        if (loadingFolderAnimation) {
            document.querySelector(".loading-filler").remove()
        }
    }
}

async function getFolder(checkbox) {
    if (checkbox.checked) {
        let container = document.querySelector(".selectfolder-options");
        container.innerHTML = "";
        
        loadingFoldersAnimation("show")

        let folders = await pywebview.api.scan_root();

        loadingFoldersAnimation("hide")

        folders.forEach(folder => {
            let newElement = document.createElement("ul");
            
            newElement.innerText = folder.name;
            newElement.dataset.id = folder.id;
            
            container.appendChild(newElement);
        });
        
        if (container.childElementCount === 0) {
            let emptyList = document.createElement("label")
            emptyList.innerHTML = "Empty";
            container.appendChild(emptyList)
        }
    }
}