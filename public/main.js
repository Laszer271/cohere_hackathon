class Page {
    constructor(text, image) {
        this.text = text;
        this.imageData = image;
    }

    updateText (text) {
        this.text = text;
    }

    updateImage(image) {
        this.imageData = image;
    }
}

/* TODO - clean it up */

// Prepare variables
const BASE_URL = "http://127.0.0.1:8000";
let pages = [];
let currentPage = 0;
const questionMarkPath = "./qm.png";
// HTML Elements
const story_btn = document.getElementById("gen_story");
const image_btn = document.getElementById("gen_image");
const page_btn = document.getElementById("gen_page");
const new_story_btn = document.getElementById("gen_new_story");
const view_pdf_btn = document.getElementById("view_pdf");
const gen_pdf_btn = document.getElementById("gen_pdf");
const settings_btn = document.getElementById("go_settings");
const pageCounter = document.querySelector(".page-counter");
// Content
const storyText = document.getElementById("story_text");
const storyImage = document.getElementById("story_image");
// Arrows
const pageBack = document.getElementById("page_back");
const pageNext = document.getElementById("page_next");

// Change page content
function changePage(nextPage) {
    if (isContentProgressOn) return;
    if (nextPage) {
        if (currentPage === pages.length - 1) return;
        currentPage++;
    } else {
        if (currentPage === 0) return;
        currentPage--;
    }
    storyText.readOnly = isFinished || !(currentPage === pages.length - 1);
    updatePage();
}

storyText.oninput = (ev) => {
    pages[currentPage].updateText(storyText.value);
};

function updatePage() {
    let pageContent = pages[currentPage];
    storyText.value = pageContent.text;
    storyImage.src = pageContent.imageData;
    pageCounter.innerText = `Page ${currentPage+1} of ${pageNumber.value}`;
    // Update arrows
    pageBack.classList.remove("hidden");
    pageNext.classList.remove("hidden");
    if (currentPage === 0) pageBack.classList.add("hidden");
    if (currentPage === pages.length - 1) pageNext.classList.add("hidden");
    // Update button visibility
    if (!isFinished) updateButtonsDisplay();
}

// API CALLS
const contentProgress = document.getElementById("content_progress");

const summary = document.getElementById("summary");
const option1 = document.getElementById("option1");
const option2 = document.getElementById("option2");
const option3 = document.getElementById("option3");
const style = document.getElementById("story_style");
const pageNumber = document.getElementById("page_number");

// Get settings
function getSettings() {
    return { 
        "summary": summary.value,
        "option1": option1.checked,
        "option2": option2.checked,
        "option3": option3.checked,
        "style": style.value,
        "pages": parseInt(pageNumber.value)
    }
}
// Send settings
async function sendSettings() {
    const response = await fetch(BASE_URL + "/settings", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "settings": getSettings() })
    });
    return await response.json();
}
// Request page, empty text means it's wants to regenerate first page
async function getPage(text) {
    const response = await fetch(BASE_URL + "/page", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "text": text })
    });
    return await response.json();
}
// Image
async function getImage(text) {
    const response = await fetch(BASE_URL + "/image", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({ "text": text })
    });
    return await response.json();
}
// PDF
let pdfPath = "";
gen_pdf_btn.addEventListener("click", async () => {
    toggleProgress();
    let images = [];
    let texts = [];
    pages.forEach((page) => {
        texts.push(page.text);
        images.push(page.imageData === questionMarkPath ? "" : page.imageData);
    });
    const response = await fetch(BASE_URL + "/pdf", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({ 
            images,
            texts
        })
    });
    let data = await response.json();
    view_pdf_btn.href = data.source;
    view_pdf_btn.classList.remove("no-display");
    gen_pdf_btn.classList.add("no-display");
    toggleProgress();
}) 

let isContentProgressOn = false;
function toggleProgress() {
    if (isContentProgressOn) {
        contentProgress.classList.add("opacity-zero");
        contentProgress.classList.remove("clickable");
    } else {
        contentProgress.classList.remove("opacity-zero");
        contentProgress.classList.add("clickable");
    }
    isContentProgressOn = !isContentProgressOn;
}

// Connect buttons

// Send options to server and get first page
new_story_btn.addEventListener("click", async (e) => {
    toggleProgress();
    await sendSettings();
    let content = await getPage(""); // Ask for start of the story
    let page = new Page(content.text, questionMarkPath);
    pages.push(page);
    // Hide settings and show story
    new_story_btn.classList.add("no-display");
    pageCounter.classList.remove("hidden");
    document.getElementById("settings").classList.add("no-display");
    document.getElementById("view_story").classList.remove("no-display");
    updatePage();
    toggleProgress();
});
// Regen current story
story_btn.addEventListener("click", async (e) => {
    toggleProgress(); 
    let text = currentPage == 0 ? "" : pages[currentPage - 1].text;
    let content = await getPage(text);
    pages[currentPage].updateText(content.text);
    updatePage();
    toggleProgress();
});
// Create Image
image_btn.addEventListener("click", async (e) => {
    toggleProgress();
    let content = await getImage(pages[currentPage].text);
    const imageObjectURL = "data:image/png;base64, " + content.image;
    pages[currentPage].updateImage(imageObjectURL);
    updatePage();
    toggleProgress();
});
// Generate next page
let isFinished = false;
page_btn.addEventListener("click", async (e) => {
    if (isFinished) {
        page_btn.innerText = "Continue Story";
        story_btn.classList.add("no-display");
        image_btn.classList.add("no-display");
        page_btn.classList.add("no-display");
        gen_pdf_btn.classList.remove("no-display");
        settings_btn.classList.remove("no-display");
        return;
    } 
    toggleProgress(); 
    let newContent = await getPage(pages[currentPage].text);
    pages.push(new Page(newContent.text, questionMarkPath));
    currentPage++;
    if (parseInt(pageNumber.value) === pages.length) {
        isFinished = true;
        page_btn.innerText = "Finish Story";
    } 
    updatePage();
    toggleProgress(); 
});

function backToSettings() {
    // Hide story and show settings
    pages = [];
    currentPage = 0;
    new_story_btn.classList.remove("no-display");
    pageCounter.classList.add("hidden");
    document.getElementById("settings").classList.remove("no-display");
    document.getElementById("view_story").classList.add("no-display");
    story_btn.classList.add("no-display");
    image_btn.classList.add("no-display");
    page_btn.classList.add("no-display");
    settings_btn.classList.add("no-display");
    isFinished = false;
    view_pdf_btn.classList.add("no-display");
    view_pdf_btn.href = "";
    gen_pdf_btn.classList.add("no-display");
    pdfPath = "";
}

function updateButtonsDisplay() {
    if (currentPage === pages.length - 1) {
        story_btn.classList.remove("no-display");
        image_btn.classList.remove("no-display");
        page_btn.classList.remove("no-display");
    } else {
        story_btn.classList.add("no-display");
        image_btn.classList.add("no-display");
        page_btn.classList.add("no-display");
    }
    // For Image creation
    if (pages[currentPage].imageData === questionMarkPath) image_btn.classList.remove("no-display");
}

