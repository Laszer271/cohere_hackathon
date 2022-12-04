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
const pages = [];
let currentPage = 0;
const questionMarkPath = "./qm.png";
// HTML Elements
const story_btn = document.getElementById("gen_story");
const image_btn = document.getElementById("gen_image");
const page_btn = document.getElementById("gen_page");
const new_story_btn = document.getElementById("gen_new_story");
const pageCounter = document.querySelector(".page-counter");
// Content
const storyText = document.getElementById("story_text");
const storyImage = document.getElementById("story_image");
// Arrows
const pageBack = document.getElementById("page_back");
const pageNext = document.getElementById("page_next");

// Test pages
/* let p1 = new Page("1st page", questionMarkPath);
pages.push(p1);
let p2 = new Page("2nd Page", questionMarkPath);
pages.push(p2);
let p3 = new Page("3rd Page", questionMarkPath);
pages.push(p3); */

// Change page content
function changePage(nextPage) {
    if (nextPage) {
        if (currentPage === pages.length - 1) return;
        currentPage++;
    } else {
        if (currentPage === 0) return;
        currentPage--;
    }
    updatePage();
}

function updatePage() {
    let pageContent = pages[currentPage];
    storyText.value = pageContent.text;
    storyImage.src = pageContent.imageData;
    pageCounter.innerText = `Page ${currentPage+1} of ${pages.length}`;
    // Update arrows
    pageBack.classList.remove("hidden");
    pageNext.classList.remove("hidden");
    if (currentPage === 0) pageBack.classList.add("hidden");
    if (currentPage === pages.length - 1) pageNext.classList.add("hidden");
    // Update button visibility
    updateButtonsDisplay();
}

// API CALLS

const contentProgress = document.getElementById("content_progress");

const summary = document.getElementById("summary");
const option1 = document.getElementById("option1");
const option2 = document.getElementById("option2");
const option3 = document.getElementById("option3");
const style = document.getElementById("story_style");

// Post options
async function sendOptions() {
    let data = JSON.stringify({ 
        "summary": summary.value,
        "option1": option1.checked,
        "option2": option2.checked,
        "option3": option3.checked,
        "style": style.value
    });
    const response = await fetch(BASE_URL + "/options", { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: data
    });
}
// Request page, empty text means it's wants to regenerate first page
async function getPage(text) {
    const response = await fetch(BASE_URL + "/page", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "data": text })
    });
    return await response.json();
}
// Image
async function getImage(text) {
    const response = await fetch(BASE_URL + "/image", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({ "data": text })
    });
    return await response.blob();
}

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
    await sendOptions(); // Send options first
    let content = await getPage(""); // Then ask for start ofthe story
    let page = new Page(content.text, questionMarkPath);
    pages.push(page);
    // Hide settings and show
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
    const imageObjectURL = URL.createObjectURL(content);
    pages[currentPage].updateImage(imageObjectURL);
    updatePage();
    toggleProgress();
});
// Generate next page
page_btn.addEventListener("click", async (e) => {
    toggleProgress(); 
    let newContent = await getPage(pages[currentPage].text);
    pages.push(new Page(newContent.text, questionMarkPath));
    currentPage++;
    updatePage();
    toggleProgress(); 
});

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

