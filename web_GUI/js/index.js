function select_A() {
    pywebview.api.select_A().then(function(path) {
        if (path) {
            document.getElementById("path-a").textContent = path;
        }
    });
}

function select_B() {
    pywebview.api.select_B().then(function(path) {
        if (path) {
            document.getElementById("path-b").textContent = path;
        }
    });
}

function sync() {
    var btn = document.getElementById("sync-btn");
    var status = document.getElementById("sync-status");

    // Start syncing state
    btn.classList.add("syncing");
    btn.disabled = true;
    status.className = "sync-status";
    status.textContent = "Syncing...";

    pywebview.api.sync().then(function(result) {
        // Done
        btn.classList.remove("syncing");
        btn.disabled = false;
        status.textContent = result;
        status.classList.add("done");
    }).catch(function(error) {
        // Error
        btn.classList.remove("syncing");
        btn.disabled = false;
        status.textContent = "Sync failed!";
        status.classList.add("error");
    });
}

function updateProgress(work_done) {
    var bar = document.querySelector(".bar");

    bar.style.width = work_done + "%";
}

function progressShow() {
    var progressBar = document.querySelector(".progress-bar");
    var bar = document.querySelector(".bar");

    progressBar.style.opacity = "100%";
    bar.style.opacity = "100%";
}

function progressHide() {
    var progressBar = document.querySelector(".progress-bar");
    var bar = document.querySelector(".bar");
    
    progressBar.style.opacity = "0%";
    bar.style.opacity = "0%";

    setTimeout(function() {
        bar.style.width = "0%";
    }, 500);
}