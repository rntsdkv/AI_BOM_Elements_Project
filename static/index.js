var input_file = document.getElementById("input-file");
var drop_area = document.getElementById("drop-area");
var load_button = document.getElementById("load-button");
var frame_title = document.querySelector(".frame-title");
var frame_subtitle = document.querySelector(".frame-subtitle");
var download_examples = document.querySelector(".download-example");
console.log(document.cookie);

drop_area.addEventListener('dragover', (event) => {
    event.preventDefault();
    drop_area.classList.add('dragover');
    event.dataTransfer.dropEffect = "copy";
});

drop_area.addEventListener('dragleave', () => {
    drop_area.classList.remove('dragover');
});

drop_area.addEventListener('drop', (event) => {
    event.preventDefault();
    drop_area.classList.remove('dragover');
    if (handleFiles(event.dataTransfer.files)) {
        drop_area.classList.add('drop');
        // load_button.classList.remove("hidden");
        // frame_title.classList.add("hidden");
        frame_title.textContent = "Загрузка файла...";
        frame_title.classList.add("white");
        frame_title.classList.add("small");
        frame_subtitle.classList.add("hidden");
        download_examples.classList.add("hidden");
    }
});

input_file.addEventListener('change', () => {
    handleFiles(input_file.files);
});

function handleFiles(files) {
    if (files.length === 0) {
        return 0;
    }

    if (files.length > 1) {
        frame_title.textContent = "Нам нужен только один файл";
        return 0;
    }

    let file = files[0];

    if (!file.name.endsWith('.csv') && !file.name.endsWith('.txt') && !file.name.endsWith('.xlsx')) {
        frame_title.textContent = "Неверный формат";
        return 0;
    }

    uploadFile(file);
    return 1;
}

function uploadFile(file) {
    let formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
        method: "POST",
        body: formData,
    })
        .then(res => {
            if (!res.ok) {
                throw new Error(`Ошибка сервера: ${res.status}`);
            }
            return res.json();
        })
        .then(data => console.log("Файл загружен:", data.filename))
        .then(() => {
            setTimeout(() => {
                frame_title.textContent = "Файл загружен";
                load_button.classList.remove("hidden");
            }, 1000);
        })
        .catch(error => console.error("Ошибка загрузки:", error));
}
